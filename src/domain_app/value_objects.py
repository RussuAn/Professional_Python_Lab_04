from dataclasses import dataclass
from math import isfinite


@dataclass(frozen=True, slots=True)
class Grade:
    value: float

    def __post_init__(self) -> None:
        if isinstance(self.value, bool) or not isfinite(self.value):
            raise ValueError("Бал має бути скінченним числом.")
        if not 0 <= self.value <= 100:
            raise ValueError("Бал має належати діапазону від 0 до 100.")

    def __str__(self) -> str:
        return f"{self.value:.2f}"


@dataclass(frozen=True, slots=True)
class Group:
    id: int
    name: str

    def __post_init__(self) -> None:
        if isinstance(self.id, bool) or self.id <= 0:
            raise ValueError("ID групи має бути додатним.")
        if not self.name.strip():
            raise ValueError("Назва групи не може бути порожньою.")
        object.__setattr__(self, "name", self.name.strip())

    def __str__(self) -> str:
        return self.name
