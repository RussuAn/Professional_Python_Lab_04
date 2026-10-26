# Система обліку студентів

Лабораторна робота №4 «Професійне ООП та система типів Python»  
Курс «Професійний Python», варіант №1  
Руссу Анастасія Сергіївна, ФЕП-32  
Викладач: Свелеба С. А.

## Опис роботи

Програма додає та редагує студентів, виконує пошук за ID, прізвищем і групою, обчислює середній бал та визначає найкращого студента. Дані шести студентів задано в main.py. Результати виводяться в терміналі.

Основні класи — Student, Group, Grade, AcademicRecord і StudentRegistry. Використано dataclass, властивості, наслідування, композицію, абстрактний клас, протоколи та анотації типів.

## Структура проєкту

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

## Запуск у Windows

Команди виконуються в PowerShell із папки, у якій розміщено pyproject.toml.

Створення середовища та встановлення пакета:

```powershell
& "C:\Program Files\Python311\python.exe" -m venv .venv
.\.venv\Scripts\python.exe -m pip install -e ".[dev]"
```

Запуск програми:

```powershell
.\.venv\Scripts\python.exe -m domain_app.main
```

## Перевірка типів і тести

```powershell
.\.venv\Scripts\python.exe -m mypy src tests
.\.venv\Scripts\python.exe -m pytest -q
```

У pyproject.toml увімкнено строгий режим mypy. Тести перевіряють додавання, редагування, пошук, обчислення середнього бала та обробку некоректних даних.

## Експерименти

Перевірка трьох навмисних помилок типів і повторна перевірка після виправлення:

```powershell
.\.venv\Scripts\python.exe -m domain_app.type_experiment
```

Порівняння створення залежності всередині сервісу з dependency injection, а також наслідування з композицією:

```powershell
.\.venv\Scripts\python.exe -m domain_app.experiments
```

## Обробка даних

Оцінки мають бути в межах від 0 до 100. Порожні імена, нескінченні значення, NaN та повторні ID не допускаються. Пошук за прізвищем не враховує регістр.

Загальний середній бал обчислюється як середнє індивідуальних середніх. Студенти без оцінок у розрахунку не враховуються. Для порожнього реєстру середній бал і найкращий студент дорівнюють None. За однакових максимальних балів обирається перший доданий студент.

Дані зберігаються в пам’яті протягом роботи програми.