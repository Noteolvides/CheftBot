from difflib import SequenceMatcher

import emoji
from spacy.lang.en import English
from telebot import types
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton

from src.ingredientsParser import parserIngredient, ingredientParser


def similar(a, b):
    return SequenceMatcher(None, a, b).ratio()


class ingredientChosser(object):
    def __init__(self, **kwargs):
        pass

    @staticmethod
    def can_process(statement, state, mongo):
        if state == 0:
            return True
        return False

    @staticmethod
    def process(statement, state, mongo):
        return similar(statement.text, "ingredient")

    @staticmethod
    def response(statement, bot, mongo):
        # change state of user

        markup = InlineKeyboardMarkup()
        markup.row_width = 2
        markup.add(InlineKeyboardButton("Add ingredient", callback_data="add_ingredient"),
                   InlineKeyboardButton("List ingredient", callback_data="list_ingredient"),
                   InlineKeyboardButton("Remove ingredient", callback_data="remove_ingredient"))
        bot.send_message(statement.id, "What do you want to do", reply_markup=markup)
        mongo.update_user_status(statement.id, 2)


class listIngredient(object):
    def __init__(self, **kwargs):
        pass

    @staticmethod
    def can_process(statement, state, mongo):
        if state == 2:
            return True
        return False

    @staticmethod
    def process(statement, state, mongo):
        return similar(statement.text, "list ingredient")

    @staticmethod
    def response(statement, bot, mongo):
        mongo.update_user_status(statement.id, 21)
        ingredients = mongo.search_user_by_id(statement.id)["ingredients"]
        for ingredientList in ingredients:
            ingredient = ingredientList[0]
            ing = ingredientParser(ingredient["quantity"], ingredient["measure"], ingredient["ingredient_name"])
            bot.send_message(statement.id, ing.print())
        else:
            bot.send_message(statement.id, "Seems like you dont have ingredients")
        # change state of user


class addIngredient(object):
    def __init__(self, **kwargs):
        pass

    @staticmethod
    def can_process(statement, state, mongo):
        if state == 2:
            return True
        return False

    @staticmethod
    def process(statement, state, mongo):
        return similar(statement.text, "add ingredient")

    @staticmethod
    def response(statement, bot, mongo):
        bot.send_message(statement.id, "Great")
        bot.send_message(statement.id, "You can take a picture, or add it manually.")
        mongo.update_user_status(statement.id, 22)


class addIngredientNameManually(object):

    @staticmethod
    def can_process(statement, state, mongo):
        if state == 22:
            return True
        return False

    @staticmethod
    def process(statement, state, mongo):
        if parserIngredient(statement.text) is not None:
            return 1
        return 0

    @staticmethod
    def response(statement, bot, mongo):
        ingredient = parserIngredient(statement.text)
        if ingredient is not None:
            bot.send_message(statement.id, "Is this the item that you wanted to add?")
            bot.send_message(statement.id, ingredient.print())
            # Save item to pending atributes for now always it is okey
            mongo.new_ingredient(statement.id, ingredient)
            mongo.update_user_status(statement.id, 0)

        else:
            bot.send_message(statement.id, "This not seem like an ingredient")
            bot.send_message(statement.id, "Could you repeat?")
