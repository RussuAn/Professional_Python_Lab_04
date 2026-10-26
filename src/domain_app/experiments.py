import csv
from abc import ABC, abstractmethod
from io import StringIO
from domain_app.dto import StudentPayload, student_from_payload
from domain_app.models import Student, StudentRegistry
from domain_app.protocols import Notifier
from domain_app.reporting import BriefReport, StudentReport, TableReport
from domain_app.repositories import InMemoryRepository
from domain_app.services import ConsoleNotifier, MemoryNotifier, StudentService


class CoupledStudentService:
    def __init__(self, registry: StudentRegistry) -> None:
        self._registry = registry
        self._notifier = ConsoleNotifier()

    def add_student(self, data: StudentPayload) -> Student:
        student = student_from_payload(data)
        self._registry.add(student)
        self._notifier.send(str(student), "Дані додано до реєстру.")
        return student


class CsvParser:
    def parse(self, text: str) -> list[StudentPayload]:
        rows = csv.DictReader(StringIO(text))
        return [StudentPayload(student_id=int(row["student_id"]),
                               first_name=row["first_name"], last_name=row["last_name"],
                               group_id=int(row["group_id"]), group=row["group"],
                               grades=[float(row["average_grade"])]) for row in rows]


class StudentValidator:
    def validate(self, payloads: list[StudentPayload]) -> list[Student]:
        return [student_from_payload(data) for data in payloads]


class BaseProcessor(ABC):
    @abstractmethod
    def parse(self, text: str) -> list[StudentPayload]: ...

    def process(self, text: str) -> str:
        students = StudentValidator().validate(self.parse(text))
        return TableReport().render(students)


class CsvProcessor(BaseProcessor):
    def parse(self, text: str) -> list[StudentPayload]:
        return CsvParser().parse(text)


class Processor:
    def __init__(self, parser: CsvParser, validator: StudentValidator,
                 formatter: StudentReport) -> None:
        self._parser = parser
        self._validator = validator
        self._formatter = formatter

    def process(self, text: str) -> str:
        rows = self._parser.parse(text)
        students = self._validator.validate(rows)
        return self._formatter.render(students)


def main() -> None:
    data: StudentPayload = {"student_id": 1, "first_name": "Марія",
                            "last_name": "Дорош", "group_id": 1,
                            "group": "ФЕП-32", "grades": [86.5]}
    print("ВАРІАНТ A: ЗАЛЕЖНІСТЬ СТВОРЮЄ СЕРВІС")
    coupled = CoupledStudentService(StudentRegistry(InMemoryRepository[Student]()))
    coupled.add_student(data)
    print("\nВАРІАНТ B: DEPENDENCY INJECTION")
    memory = MemoryNotifier()
    notifier: Notifier = memory
    service = StudentService(StudentRegistry(InMemoryRepository[Student]()), notifier)
    service.add_student(data)
    print("Повідомлення в пам’яті:", memory.messages)
    print("ConsoleNotifier сумісний:", isinstance(ConsoleNotifier(), Notifier))
    print("MemoryNotifier сумісний:", isinstance(memory, Notifier))

    text = ("student_id,first_name,last_name,group_id,group,average_grade\n"
            "1,Марія,Дорош,1,ФЕП-32,86.5\n2,Данило,Левицький,2,ФЕП-31,95\n")
    inherited = CsvProcessor().process(text)
    composed = Processor(CsvParser(), StudentValidator(), TableReport()).process(text)
    print("\nНАСЛІДУВАННЯ І КОМПОЗИЦІЯ")
    print(inherited)
    print("Результати збігаються:", inherited == composed)
    print("Заміна форматування через композицію:")
    print(Processor(CsvParser(), StudentValidator(), BriefReport()).process(text))


if __name__ == "__main__":
    main()
