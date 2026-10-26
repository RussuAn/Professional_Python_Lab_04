from typing import TypedDict
from domain_app.models import Student
from domain_app.value_objects import Grade, Group


class StudentPayload(TypedDict):
    student_id: int
    first_name: str
    last_name: str
    group_id: int
    group: str
    grades: list[float]


def student_from_payload(data: StudentPayload) -> Student:
    student = Student(data["student_id"], data["first_name"], data["last_name"],
                      Group(data["group_id"], data["group"]))
    for value in data["grades"]:
        student.record.add_grade(Grade(value))
    return student
