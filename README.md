# Система обліку студентів

Лабораторна робота №4 з курсу «Професійний Python», варіант №1.
Авторка: Руссу Анастасія Сергіївна, ФЕП-32.
Викладач: Свелеба С. А.

## Призначення

Програма додає та редагує студентів, шукає за ID, прізвищем і групою,
обчислює середній бал та знаходить найкращого студента.
Демонстраційні дані шести студентів задано в main.py.
Результати та повідомлення виводяться в терміналі.

## Встановлення у Windows PowerShell

Відкрийте термінал у папці з pyproject.toml. Команди виконуються по черзі.

```powershell
& "C:\Program Files\Python311\python.exe" -m venv .venv
.\.venv\Scripts\python.exe -m pip install -e ".[dev]"
.\.venv\Scripts\python.exe -m domain_app.main
```

Якщо Python установлено в іншому місці, у першій команді потрібно вказати його шлях.
Активація середовища не потрібна. Після встановлення також доступна команда
`.\.venv\Scripts\student-registry.exe`.

## Перевірки й експерименти

```powershell
.\.venv\Scripts\python.exe -m mypy src tests
.\.venv\Scripts\python.exe -m pytest -q
.\.venv\Scripts\python.exe -m domain_app.type_experiment
.\.venv\Scripts\python.exe -m domain_app.experiments
```

mypy працює у strict-режимі з цільовою версією Python 3.11.
У type_experiment спочатку перевіряється тимчасовий файл із трьома навмисними
помилками, потім той самий файл виправляється і перевіряється повторно.
Це експеримент із розділу 71 методички. Помилковий файл не залишається в проєкті.
Вивід містить diagnostics до та після виправлення.

experiments порівнює створення залежності всередині сервісу з dependency injection,
а також обробку CSV через наслідування та композицію.
MemoryNotifier зберігає повідомлення в пам’яті й дозволяє перевірити сервіс без
консольного виводу. Повідомлення не надсилаються зовнішнім сервісам.

## Структура

```text
Lab_04_variant_1/
├── pyproject.toml
├── README.md
├── .gitignore
├── src/domain_app/
│   ├── __init__.py
│   ├── py.typed
│   ├── value_objects.py
│   ├── models.py
│   ├── protocols.py
│   ├── repositories.py
│   ├── dto.py
│   ├── reporting.py
│   ├── services.py
│   ├── main.py
│   ├── experiments.py
│   └── type_experiment.py
└── tests/test_domain.py
```

## Об’єктна модель

Student містить Group та AcademicRecord. AcademicRecord зберігає оцінки Grade.
Grade і Group — frozen dataclass, AcademicRecord використовує default_factory.
StudentRegistry отримує Repository[Student] і надає пошук та статистику.
InMemoryRepository[T] має TypeVar з обмеженням HasId; використовується для Student і Group.
StudentPayload описує зовнішні дані через TypedDict; student_from_payload створює об’єкт.

StudentReport — ABC. TableReport і BriefReport успадковують його та використовують super().
ReportingService отримує потрібний формат звіту через конструктор.
StudentService залежить від Notifier, якому структурно відповідають ConsoleNotifier
і MemoryNotifier. Notifier має runtime_checkable.

Реалізовані __str__, __repr__, __len__, __iter__, __contains__ і __getitem__.
Індекс у registry[id] означає ID студента, а не позицію у списку.

## Правила обробки

Оцінка має бути скінченним числом від 0 до 100. Порожні імена й назви груп
відхиляються. ID додатні, повторне додавання ID спричиняє ValueError.
Пошук за прізвищем точний, без урахування регістру та крайніх пробілів.
Групи порівнюються за ID та назвою. get повертає None для відсутнього ID;
редагування та registry[id] у такому випадку піднімають KeyError.

Середній бал студента обчислюється за його оцінками. Загальний середній — середнє
індивідуальних середніх студентів, які мають оцінки. Якщо оцінок немає, повертається None.
За однакових максимальних середніх обирається перший доданий студент.
Помилкове редагування імен не змінює інших полів. ID доступний лише для читання.
Сховище працює в пам’яті; після завершення програми дані не зберігаються.

## SOLID

SRP: сутності контролюють дані, repository зберігає їх, reporting форматує вивід.
OCP: новий формат звіту додається реалізацією StudentReport без зміни ReportingService.
LSP: обидва формати приймають ту саму послідовність студентів, зокрема порожню.
ISP: Repository і Notifier мають окремі невеликі інтерфейси.
DIP: StudentRegistry та StudentService отримують залежності через протоколи.

Додаткові можливості з розділу 74: bound TypeVar, generic repository,
runtime_checkable Protocol, власна колекція, __getitem__, __iter__, __contains__,
абстракція repository та стратегія форматування звіту.

## Звіт

Готовий Report_lab_04.pdf додається окремо до папки report.
Для сервісу перевірки в репозиторії має бути лише один PDF/DOCX-звіт цієї лабораторної.
