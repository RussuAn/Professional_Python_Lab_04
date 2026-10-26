from pathlib import Path
import subprocess
import sys
from tempfile import TemporaryDirectory


BROKEN = """from domain_app.models import Student
from domain_app.repositories import InMemoryRepository
from domain_app.value_objects import Group

student_id: int = "1"

def average() -> float:
    return "95.0"

repository = InMemoryRepository[Student]()
repository.add(Group(1, "ФЕП-32"))
"""

FIXED = """from domain_app.models import Student
from domain_app.repositories import InMemoryRepository
from domain_app.value_objects import Group

student_id: int = 1

def average() -> float:
    return 95.0

repository = InMemoryRepository[Student]()
repository.add(Student(student_id, "Марія", "Дорош", Group(1, "ФЕП-32")))
"""


def check(path: Path) -> subprocess.CompletedProcess[str]:
    return subprocess.run([sys.executable, "-m", "mypy", "--strict",
                           "--no-incremental", "--show-error-codes", str(path)],
                          capture_output=True, text=True, encoding="utf-8")


def main() -> None:
    with TemporaryDirectory() as directory:
        path = Path(directory) / "type_demo.py"
        path.write_text(BROKEN, encoding="utf-8")
        broken = check(path)
        print("ДО ВИПРАВЛЕННЯ")
        print(broken.stdout.replace(str(path), "type_demo.py"))
        if broken.returncode != 1 or broken.stdout.count("error:") != 3:
            raise RuntimeError(broken.stderr or "Очікувалися рівно три помилки mypy.")
        path.write_text(FIXED, encoding="utf-8")
        fixed = check(path)
        print("ПІСЛЯ ВИПРАВЛЕННЯ")
        print(fixed.stdout.replace(str(path), "type_demo.py"))
        if fixed.returncode != 0:
            raise RuntimeError(fixed.stderr or fixed.stdout)


if __name__ == "__main__":
    main()
