from typing import List


class Ingredient:
    text: str

    def __init__(self, text: str) -> None:
        self.text = text


class User:
    step_counter: int
    ingredients: List[Ingredient]

    def __init__(self) -> None:
        self.step_counter = 0

