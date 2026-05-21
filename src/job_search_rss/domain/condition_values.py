from dataclasses import dataclass


@dataclass(frozen=True)
class Region:
    prefecture: str
    city: str | None = None

    @property
    def normalized_key(self) -> str:
        parts = ["region", _normalize_key_part(self.prefecture)]
        if self.city is not None:
            parts.append(_normalize_key_part(self.city))
        return ":".join(parts)


@dataclass(frozen=True)
class Occupation:
    category: str
    detail: str

    @property
    def normalized_key(self) -> str:
        return ":".join(
            [
                "occupation",
                _normalize_key_part(self.category),
                _normalize_key_part(self.detail),
            ]
        )


def _normalize_key_part(value: str) -> str:
    return "-".join(value.strip().lower().split())
