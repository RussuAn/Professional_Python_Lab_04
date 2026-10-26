from domain_app.dto import StudentPayload
from domain_app.models import Student, StudentRegistry
from domain_app.protocols import Notifier
from domain_app.reporting import BriefReport, ReportingService, TableReport
from domain_app.repositories import InMemoryRepository
from domain_app.services import ConsoleNotifier, StudentService
from domain_app.value_objects import Grade, Group


def main() -> None:
    groups = InMemoryRepository[Group]()
    for group in (Group(1, "ФЕП-32"), Group(2, "ФЕП-31"), Group(3, "ФЕП-33")):
        groups.add(group)
    registry = StudentRegistry(InMemoryRepository[Student]())
    notifier = ConsoleNotifier()
    service = StudentService(registry, notifier)
    payloads: list[StudentPayload] = [
        {"student_id": 1, "first_name": "Марія", "last_name": "Дорош",
         "group_id": 1, "group": "ФЕП-32", "grades": [80.0, 93.0]},
        {"student_id": 2, "first_name": "Данило", "last_name": "Левицький",
         "group_id": 2, "group": "ФЕП-31", "grades": [95.0, 95.0]},
        {"student_id": 3, "first_name": "Соломія", "last_name": "Климчук",
         "group_id": 1, "group": "ФЕП-32", "grades": [90.0, 93.0]},
        {"student_id": 4, "first_name": "Остап", "last_name": "Мазур",
         "group_id": 2, "group": "ФЕП-31", "grades": [76.0, 80.0]},
        {"student_id": 5, "first_name": "Олена", "last_name": "Романюк",
         "group_id": 3, "group": "ФЕП-33", "grades": [84.0, 86.0]},
        {"student_id": 6, "first_name": "Тарас", "last_name": "Дорош",
         "group_id": 3, "group": "ФЕП-33", "grades": [70.0, 74.0]},
    ]
    for data in payloads:
        service.add_student(data)
    print()
    print(ReportingService(registry, TableReport()).create_report())
    average = registry.average_grade()
    if average is not None:
        print(f"Середній бал студентів: {average:.4f}")
    print("Найкращий студент:", registry.best_student())

    print("\nПОШУК ЗА ID 2")
    print(registry.get(2))
    print("ПОШУК ЗА ПРІЗВИЩЕМ ДОРОШ")
    for student in registry.search(last_name="ДОРОШ"):
        print(student)
    print("ПОШУК ЗА ГРУПОЮ ФЕП-32")
    for student in registry.search(group=Group(1, "ФЕП-32")):
        print(student)

    print("\nРЕДАГУВАННЯ СТУДЕНТА З ID 6")
    service.edit_student(6, first_name="Тарас Іван", group=Group(1, "ФЕП-32"))
    service.add_grade(6, 90)
    print(registry[6], "середній бал:", registry[6].average_grade)
    print("\nПОЛІМОРФІЗМ ЗВІТІВ")
    print(ReportingService(registry, BriefReport()).create_report())
    print("\nDUNDER METHODS І PROTOCOL")
    print("len(registry):", len(registry))
    print("2 in registry:", 2 in registry)
    print("registry[2]:", registry[2])
    print("repr(registry[2]):", repr(registry[2]))
    print("Бали студента 2:", [str(grade) for grade in registry[2].record])
    print("Notifier:", isinstance(notifier, Notifier))
    print("Репозиторій груп:", [str(group) for group in groups.all()])

    print("\nПЕРЕВІРКА НЕКОРЕКТНИХ ДАНИХ")
    try:
        Grade(105)
    except ValueError as error:
        print(error)
    try:
        registry[1].first_name = " "
    except ValueError as error:
        print(error)
    try:
        service.add_student(payloads[0])
    except ValueError as error:
        print(error)
    print("Пошук відсутнього ID:", registry.get(999))
    empty = StudentRegistry(InMemoryRepository[Student]())
    print("Порожній реєстр:", empty.average_grade(), empty.best_student())


if __name__ == "__main__":
    main()
