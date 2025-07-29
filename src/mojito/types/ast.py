import dataclasses


@dataclasses.dataclass(frozen=True)
class Location:
    line_number: int
    start: int
    end: int


@dataclasses.dataclass(frozen=True)
class Number:
    location: Location
    value: float

    def __eq__(self, other_number) -> bool:
        if isinstance(other_number, (int, float)):
            return self.value == other_number
        return self.value == other_number.value


@dataclasses.dataclass(frozen=True)
class String:
    location: Location
    value: str


@dataclasses.dataclass(frozen=True)
class Word:
    location: Location
    name: str

    def __eq__(self, other_word) -> bool:
        if isinstance(other_word, str):
            return self.name == other_word
        return self.name == other_word.name


@dataclasses.dataclass(frozen=True)
class Quotation:
    items: list = dataclasses.field(default_factory=list)

    def __len__(self):
        return len(self.items)

    def __getitem__(self, index):
        return self.items[index]

    def head(self):
        return self.items[0]

    def tail(self):
        return Quotation(self.items[1:])

    def append(self, element): ...

    def __iter__(self):
        return iter(self.items)


@dataclasses.dataclass(frozen=True)
class Program:
    items: list = dataclasses.field(default_factory=list)

    def __len__(self):
        return len(self.items)

    def __getitem__(self, index):
        return self.items[index]

    def __iter__(self):
        return iter(self.items)
