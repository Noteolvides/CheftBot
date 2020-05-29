import re

import spacy
import emoji

nlp = spacy.load("en_core_web_sm")

units = {"cup": ['c', 'c.', 'C', 'Cups'],
         "gallon": ['gal'],
         "ounce": ['oz', 'oz.'],
         "pint": ['pt', 'pts', 'pt.'],
         "pound": ['lb', 'lb.', 'lbs', 'lbs.', 'Lb', 'Lbs'],
         "quart": ['qt', 'qt.', 'qts', 'qts.'],
         "tablespoon": ['tbs', 'tbsp', 'tbspn', 'T', 'T.', 'Tablespoons', 'Tablespoon'],
         "teaspoon": ['tsp', 'tspn', 't', 't.'],
         "gram": ['g', 'g.'],
         "kilogram": ['kg', 'kg.', 'Kg', 'Kg.'],
         "liter": ['l', 'l.', 'L', 'L.'],
         "milligram": ['mg', 'mg.'],
         "milliliter": ['ml', 'ml.', 'mL', 'mL.'],
         "package": ['pkg', 'pkgs'],
         "stick": ['sticks'],
         "piece": ['pcs', 'pcs.'],
         "pinch": ['pinch'],
         "small": ['Small'],
         "medium": ['Medium'],
         "large": ['large', 'Large']}
pluralUnits = {
    "cup": 'cups',
    "gallon": 'gallons',
    "ounce": 'ounces',
    "pint": 'pints',
    "pound": 'pounds',
    "quart": 'quarts',
    "tablespoon": 'tablespoons',
    "teaspoon": 'teaspoons',
    "gram": 'grams',
    "kilogram": 'kilograms',
    "liter": 'liters',
    "milligram": 'milligrams',
    "milliliter": 'milliliters',
    "clove": 'cloves',
    "bag": 'bags',
    "box": 'boxes',
    "pinch": 'pinches',
    "can": 'cans',
    "slice": 'slices',
    "piece": 'pieces'
}


def findQuantity(ingredient):
    numericAndFractionRegex = '^(\d+\/\d+)|(\d+\s\d+\/\d+)|(\d+.\d+)|\d+'
    numericRangeWithSpaceRegex = '^(\d+\-\d+)|^(\d+\s\-\s\d+)'

    if re.match(numericRangeWithSpaceRegex, ingredient):
        quantity = re.search(numericRangeWithSpaceRegex, ingredient).group()
        restOfIngredient = ingredient.replace(quantity, "").strip()
        return [quantity, restOfIngredient]

    if re.match(numericAndFractionRegex, ingredient):
        quantity = re.search(numericAndFractionRegex, ingredient).group()
        restOfIngredient = ingredient.replace(quantity, "").strip()
        return [quantity, restOfIngredient]

    return [None, ingredient]


def toNumber(quantity):
    if quantity and len(quantity.split(' ')) > 1:
        rest = quantity.split(' ')
        whole = rest[0]
        fraction = rest[1]
        [a, b] = fraction.split('/')
        remainder = int(a) / int(b)
        return round(int(whole) + remainder, 3)
    else:
        res = quantity.split('/')
        if len(res) > 1:
            a = res[0]
            b = res[1]
            return round(int(a) / int(b), 3)
        else:
            return res[0]


def getUnit(inp):
    if inp in units or inp in pluralUnits:
        return inp
    for unit in units.keys():
        for eachUnit in units[unit]:
            if inp == eachUnit:
                return unit
    for eachUnit in pluralUnits.keys():
        if inp == pluralUnits[eachUnit]:
            return eachUnit
    return ""
    pass


def parserIngredient(ingredientString):
    try:
        ingredient = ingredientString.strip()
        [quantity, restOfIngredient] = findQuantity(ingredient)
        quantity = toNumber(quantity)

        unit = getUnit(restOfIngredient.split(' ')[0])
        if unit != "":
            ingredient = restOfIngredient.replace(restOfIngredient.split(' ')[0], "").strip()
            return ingredientParser(quantity, unit, ingredient)
        return ingredientParser(quantity, unit, restOfIngredient.strip())

    except:
        return None


class ingredientParser(object):
    def __init__(self, quantity, unit, ingredient):
        self.quantity = quantity
        self.unit = unit
        self.ingredient = ingredient

    def __repr__(self):
        return self.ingredient + " " + self.unit + " " + self.quantity

    def print(self):
        string = ""
        string += "Ingredient : " + self.ingredient + emoji.emojize(":red_apple:", use_aliases=True) + "\n"
        string += "Quantity : " + self.quantity + "\n"
        string += "Mesure : " + self.unit

        return string


if __name__ == '__main__':
    print(parserIngredient("10 kg apples"))
