from dataclasses import dataclass, field
from domain_app.dto import StudentPayload, student_from_payload
from domain_app.models import Student, StudentRegistry
from domain_app.protocols import Notifier
from domain_app.value_objects import Grade, Group


class ConsoleNotifier:
    def send(self, recipient: str, message: str) -> None:
        print(f"Повідомлення для {recipient}: {message}")


@dataclass
class MemoryNotifier:
    messages: list[tuple[str, str]] = field(default_factory=list)

    def send(self, recipient: str, message: str) -> None:
        self.messages.append((recipient, message))


class StudentService:
    def __init__(self, registry: StudentRegistry, notifier: Notifier) -> None:
        self._registry = registry
        self._notifier = notifier

    def add_student(self, data: StudentPayload) -> Student:
        student = student_from_payload(data)
        self._registry.add(student)
        self._notifier.send(str(student), "Дані додано до реєстру.")
        return student

    def edit_student(self, student_id: int, *, first_name: str | None = None,
                     last_name: str | None = None, group: Group | None = None) -> Student:
        student = self._registry.edit(student_id, first_name=first_name,
                                      last_name=last_name, group=group)
        self._notifier.send(str(student), "Дані оновлено.")
        return student

    def add_grade(self, student_id: int, value: float) -> None:
        student = self._registry[student_id]
        student.record.add_grade(Grade(value))
        self._notifier.send(str(student), "Бал додано.")
