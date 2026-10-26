from typing import Protocol, TypeVar, runtime_checkable


class HasId(Protocol):
    @property
    def id(self) -> int: ...


T = TypeVar("T", bound=HasId)


class Repository(Protocol[T]):
    def add(self, item: T) -> None: ...
    def get(self, item_id: int) -> T | None: ...
    def all(self) -> list[T]: ...
    def remove(self, item_id: int) -> bool: ...


@runtime_checkable
class Notifier(Protocol):
    def send(self, recipient: str, message: str) -> None: ...
