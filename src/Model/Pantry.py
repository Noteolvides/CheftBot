class Pantry(object):
    ingredients = None

    def __init__(self, token):
        self.token = token

    def newIngredient(self, ingredient):
        self.ingredients.append(ingredient)