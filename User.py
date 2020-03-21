from typing import List


class Ingredient:
    text: str

    def __init__(self, text: str) -> None:
        self.text = text


class User:
    step_counter: int
    ingredients: List[Ingredient]

    def __init__(self, step_counter: int, ingredients: List[Ingredient]) -> None:
        self.step_counter = step_counter
        self.ingredients = ingredients

