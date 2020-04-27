from typing import List


class Ingredient:
    text: str

    def __init__(self, text: str) -> None:
        self.text = text


class Instructions:
    text: str

    def __init__(self, text: str) -> None:
        self.text = text


class Recipe:
    ingredients: List[Ingredient]
    instructions: List[Instructions]
    quantity: List[float]
    title: str

    def __init__(self, title: str, ingredients: List[Ingredient], instructions: List[Ingredient],
                 quantity: List[float]) -> None:
        self.title = title
        self.ingredients = ingredients
        self.instructions = instructions
        self.quantity = quantity


huevoFrito = Recipe("Huevo duro", ["Huevo", "Aceite", "Sal"],
                    ["Coger una sarten", "Cubre la sartén con aceite", "Pon el fuego alto", "Añadir el Huevo a la sarten", "Cuidado que no se te queme", "Cuando este listo sacalo", "Y ya estaria"],
                    [8.00, 5.00, 9.00])

huevoDuro = Recipe("Huevo frito", ["Huevo", "Aceite", "Sal"],
                    ["Coger una sarten", "Cubre la sartén con aceite", "Pon el fuego alto", "Añadir el Huevo a la sarten", "Cuidado que no se te queme", "Cuando este listo sacalo", "Y ya estaria"],
                    [8.00, 5.00, 9.00])
