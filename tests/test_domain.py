from dataclasses import FrozenInstanceError
import pytest
from domain_app.dto import StudentPayload, student_from_payload
from domain_app.experiments import CsvParser, CsvProcessor, Processor, StudentValidator
from domain_app.models import AcademicRecord, Student, StudentRegistry
from domain_app.protocols import Notifier
from domain_app.reporting import BriefReport, ReportingService, TableReport
from domain_app.repositories import InMemoryRepository
from domain_app.services import MemoryNotifier, StudentService
from domain_app.value_objects import Grade, Group


def payload(student_id: int = 1) -> StudentPayload:
    return {"student_id": student_id, "first_name": " Марія ", "last_name": "Дорош",
            "group_id": 1, "group": "ФЕП-32", "grades": [80.0, 93.0]}


@pytest.mark.parametrize("value", [-1.0, 101.0, float("nan"), float("inf"), -float("inf")])
def test_invalid_grade(value: float) -> None:
    with pytest.raises(ValueError):
        Grade(value)


def test_grade_boundaries_and_immutability() -> None:
    assert Grade(0).value == 0
    assert str(Grade(100)) == "100.00"
    with pytest.raises(FrozenInstanceError):
        setattr(Grade(90), "value", 50)


def test_groups() -> None:
    assert Group(1, " ФЕП-32 ") == Group(1, "ФЕП-32")
    with pytest.raises(ValueError):
        Group(0, "ФЕП-32")
    with pytest.raises(ValueError):
        Group(1, " ")


def test_record_empty_and_separate_defaults() -> None:
    first, second = AcademicRecord(), AcademicRecord()
    assert first.average is None
    first.add_grade(Grade(80))
    first.add_grade(Grade(100))
    assert first.average == 90
    assert len(first) == 2
    assert list(first) == [Grade(80), Grade(100)]
    assert first.grades == (Grade(80), Grade(100))
    assert second.grades == ()


def test_payload_and_property() -> None:
    student = student_from_payload(payload())
    assert student.first_name == "Марія"
    assert student.average_grade == 86.5
    assert "Марія" in str(student)
    assert "student_id=1" in repr(student)
    with pytest.raises(ValueError):
        student.first_name = " "
    assert student.first_name == "Марія"
    with pytest.raises(AttributeError):
        setattr(student, "id", 2)


def test_repository_duplicate_remove_and_snapshot() -> None:
    repository = InMemoryRepository[Student]()
    student = student_from_payload(payload())
    repository.add(student)
    with pytest.raises(ValueError):
        repository.add(student_from_payload(payload()))
    assert repository.get(1) is student
    repository.all().clear()
    assert len(repository.all()) == 1
    assert repository.remove(1)
    assert not repository.remove(1)
    assert repository.get(1) is None


def test_repository_second_type() -> None:
    repository = InMemoryRepository[Group]()
    group = Group(1, "ФЕП-32")
    repository.add(group)
    assert repository.get(1) == group


def test_registry_search_and_collection() -> None:
    registry = StudentRegistry(InMemoryRepository[Student]())
    registry.add(student_from_payload(payload(1)))
    registry.add(student_from_payload(payload(2)))
    registry.edit(2, group=Group(2, "ФЕП-31"))
    assert len(registry) == 2
    assert 1 in registry and 99 not in registry
    assert [s.id for s in registry.search(last_name=" дОрОш ")] == [1, 2]
    assert [s.id for s in registry.search(group=Group(1, "ФЕП-32"))] == [1]
    assert registry.search(last_name="Інше") == []
    with pytest.raises(KeyError):
        registry[99]
    with pytest.raises(KeyError):
        registry.edit(99, first_name="Іван")


def test_edit_is_atomic_and_preserves_record() -> None:
    registry = StudentRegistry(InMemoryRepository[Student]())
    registry.add(student_from_payload(payload()))
    with pytest.raises(ValueError):
        registry.edit(1, first_name="Олена", last_name=" ")
    assert registry[1].first_name == "Марія"
    student = registry.edit(1, first_name="Олена", last_name="Романюк")
    assert student.last_name == "Романюк"
    assert student.average_grade == 86.5


def test_average_best_empty_ungraded_and_tie() -> None:
    registry = StudentRegistry(InMemoryRepository[Student]())
    assert registry.average_grade() is None
    assert registry.best_student() is None
    registry.add(Student(3, "Іван", "Мазур", Group(1, "ФЕП-32")))
    assert registry.best_student() is None
    registry.add(student_from_payload(payload(1)))
    registry.add(student_from_payload(payload(2)))
    assert registry.best_student() is registry[1]
    registry[2].record.add_grade(Grade(100))
    assert registry.best_student() is registry[2]
    assert registry.average_grade() == pytest.approx((86.5 + 91) / 2)


def test_service_injected_notifier_and_failed_operation() -> None:
    registry = StudentRegistry(InMemoryRepository[Student]())
    notifier = MemoryNotifier()
    service = StudentService(registry, notifier)
    assert isinstance(notifier, Notifier)
    service.add_student(payload())
    service.edit_student(1, first_name="Марія Іванна")
    service.add_grade(1, 100)
    assert len(notifier.messages) == 3
    with pytest.raises(ValueError):
        service.add_grade(1, 105)
    with pytest.raises(ValueError):
        service.add_student(payload())
    assert len(notifier.messages) == 3
    assert len(registry[1].record) == 3


def test_invalid_payload_not_saved() -> None:
    registry = StudentRegistry(InMemoryRepository[Student]())
    notifier = MemoryNotifier()
    data = payload()
    data["grades"] = [80, 105]
    with pytest.raises(ValueError):
        StudentService(registry, notifier).add_student(data)
    assert len(registry) == 0
    assert notifier.messages == []


def test_report_polymorphism_and_empty() -> None:
    registry = StudentRegistry(InMemoryRepository[Student]())
    assert "Студентів немає" in ReportingService(registry, TableReport()).create_report()
    registry.add(student_from_payload(payload()))
    assert "86.50" in ReportingService(registry, TableReport()).create_report()
    assert "студентів — 1" in ReportingService(registry, BriefReport()).create_report()


def test_inheritance_and_composition() -> None:
    text = ("student_id,first_name,last_name,group_id,group,average_grade\n"
            "1,Марія,Дорош,1,ФЕП-32,86.5\n")
    composed = Processor(CsvParser(), StudentValidator(), TableReport())
    assert CsvProcessor().process(text) == composed.process(text)
    brief = Processor(CsvParser(), StudentValidator(), BriefReport())
    assert "студентів — 1" in brief.process(text)
    with pytest.raises(ValueError):
        composed.process(text.replace("86.5", "105"))
