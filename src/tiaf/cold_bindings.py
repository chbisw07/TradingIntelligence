"""Dependency-free lifecycle failure shared by COLD binding owners."""


class FrozenBindingsError(RuntimeError):
    """Registration or replacement was attempted after composition freeze."""

    def __init__(self) -> None:
        super().__init__("COLD composition is frozen; construct a new startup owner")
