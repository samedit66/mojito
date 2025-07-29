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


@dataclasses.dataclass(frozen=True)
class String:
    location: Location
    value: str


@dataclasses.dataclass(frozen=True)
class Word:
    location: Location
    name: str


@dataclasses.dataclass(frozen=True)
class Quotation:
    items: list = dataclasses.field(default_factory=list)

    def __len__(self):
        return len(self.items)

    def __getitem__(self, index):
        return self.items[index]

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
