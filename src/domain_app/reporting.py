from abc import ABC, abstractmethod
from collections.abc import Sequence
from domain_app.models import Student, StudentRegistry


class StudentReport(ABC):
    def __init__(self, title: str) -> None:
        self.title = title

    @abstractmethod
    def render(self, students: Sequence[Student]) -> str: ...


class TableReport(StudentReport):
    def __init__(self) -> None:
        super().__init__("РЕЄСТР СТУДЕНТІВ")

    def render(self, students: Sequence[Student]) -> str:
        lines = [self.title,
                 f"{'ID':<5} {'Прізвище та ім’я':<25} {'Група':<10} {'Середній бал':>12}"]
        for student in students:
            average = student.average_grade
            grade = "немає" if average is None else f"{average:.2f}"
            name = f"{student.last_name} {student.first_name}"
            lines.append(f"{student.id:<5} {name:<25} {student.group.name:<10} {grade:>12}")
        if not students:
            lines.append("Студентів немає.")
        return "\n".join(lines)


class BriefReport(StudentReport):
    def __init__(self) -> None:
        super().__init__("КОРОТКИЙ ЗВІТ")

    def render(self, students: Sequence[Student]) -> str:
        return f"{self.title}: студентів — {len(students)}"


class ReportingService:
    def __init__(self, registry: StudentRegistry, report: StudentReport) -> None:
        self._registry = registry
        self._report = report

    def create_report(self) -> str:
        return self._report.render(list(self._registry))
