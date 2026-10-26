from collections.abc import Iterator
from dataclasses import dataclass, field
from domain_app.protocols import Repository
from domain_app.value_objects import Grade, Group


@dataclass
class AcademicRecord:
    _grades: list[Grade] = field(default_factory=list, init=False, repr=False)

    def add_grade(self, grade: Grade) -> None:
        self._grades.append(grade)

    @property
    def grades(self) -> tuple[Grade, ...]:
        return tuple(self._grades)

    @property
    def average(self) -> float | None:
        if not self._grades:
            return None
        return sum(grade.value for grade in self._grades) / len(self._grades)

    def __len__(self) -> int:
        return len(self._grades)

    def __iter__(self) -> Iterator[Grade]:
        return iter(self._grades)


class Student:
    def __init__(self, student_id: int, first_name: str,
                 last_name: str, group: Group) -> None:
        if isinstance(student_id, bool) or student_id <= 0:
            raise ValueError("ID студента має бути додатним.")
        self._id = student_id
        self.first_name = first_name
        self.last_name = last_name
        self.group = group
        self._record = AcademicRecord()

    @property
    def id(self) -> int:
        return self._id

    @property
    def first_name(self) -> str:
        return self._first_name

    @first_name.setter
    def first_name(self, value: str) -> None:
        if not value.strip():
            raise ValueError("Ім'я не може бути порожнім.")
        self._first_name = value.strip()

    @property
    def last_name(self) -> str:
        return self._last_name

    @last_name.setter
    def last_name(self, value: str) -> None:
        if not value.strip():
            raise ValueError("Прізвище не може бути порожнім.")
        self._last_name = value.strip()

    @property
    def record(self) -> AcademicRecord:
        return self._record

    @property
    def average_grade(self) -> float | None:
        return self.record.average

    def __str__(self) -> str:
        return f"{self.last_name} {self.first_name} ({self.group})"

    def __repr__(self) -> str:
        return (f"Student(student_id={self.id!r}, first_name={self.first_name!r}, "
                f"last_name={self.last_name!r}, group={self.group!r})")


class StudentRegistry:
    def __init__(self, repository: Repository[Student]) -> None:
        self._repository = repository

    def add(self, student: Student) -> None:
        self._repository.add(student)

    def get(self, student_id: int) -> Student | None:
        return self._repository.get(student_id)

    def edit(self, student_id: int, *, first_name: str | None = None,
             last_name: str | None = None, group: Group | None = None) -> Student:
        student = self.get(student_id)
        if student is None:
            raise KeyError(f"Студента з ID {student_id} не знайдено.")
        if first_name is not None and not first_name.strip():
            raise ValueError("Ім'я не може бути порожнім.")
        if last_name is not None and not last_name.strip():
            raise ValueError("Прізвище не може бути порожнім.")
        if first_name is not None:
            student.first_name = first_name
        if last_name is not None:
            student.last_name = last_name
        if group is not None:
            student.group = group
        return student

    def search(self, last_name: str | None = None,
               group: Group | None = None) -> list[Student]:
        return [student for student in self
                if (last_name is None or student.last_name.casefold()
                    == last_name.strip().casefold())
                and (group is None or student.group == group)]

    def average_grade(self) -> float | None:
        grades = [student.average_grade for student in self
                  if student.average_grade is not None]
        return sum(grades) / len(grades) if grades else None

    def best_student(self) -> Student | None:
        best = None
        maximum = -1.0
        for student in self:
            average = student.average_grade
            if average is not None and average > maximum:
                best, maximum = student, average
        return best

    def __len__(self) -> int:
        return len(self._repository.all())

    def __iter__(self) -> Iterator[Student]:
        return iter(self._repository.all())

    def __contains__(self, student_id: int) -> bool:
        return self.get(student_id) is not None

    def __getitem__(self, student_id: int) -> Student:
        student = self.get(student_id)
        if student is None:
            raise KeyError(student_id)
        return student
