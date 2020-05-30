import emoji
from chatterbot.comparisons import JaccardSimilarity
from chatterbot.conversation import Statement
from telebot import types

from src.Model.Item import Item
from src.ingredientsParser import parserIngredient
from src.ingredients_Adapter import similar
from telebot.types import InlineKeyboardMarkup

# Estados Shopping List
ESTADO_SHOPPING_LIST = 4
ESTADO_ADD_ITEM = 41
ESTADO_DELETE_ITEM = 42
ESTADO_LIST_ITEMS = 43

# Frases de ChatBot
ITEM_ADDED = "has been added succesfully!"
ITEM_DELETED = "has been deleted"
CANT_DELETE = "This item doesn't exist in the list"
LIST_ITEMS = "These are all the items in the shopping list:\n"
COLS = "\tItem:\tQuantity:\tUnit:\n"
NO_ITEMS = "There are no items in the shopping list :("

# Frases Accion
SP_ADD_ITEM = "add item"
SP_DELETE_ITEM = "delete item"
SP_LIST_ITEMS = "list items"

MIN = 0.8


class AddItem(object):
    def __init__(self, **kwargs):
        pass

    @staticmethod
    def can_process(statement, state, mongo):
        if state == ESTADO_ADD_ITEM and similar(statement.text, SP_ADD_ITEM) > MIN:
            return True
        return False

    @staticmethod
    def process(statement, state, mongo):
        return similar(statement.text, SP_ADD_ITEM)

    @staticmethod
    def response(statement, bot, mongo):
        # Montar item que es vol afegir a la llista
        parsed = parserIngredient(statement.text)
        item = Item(parsed.ingredient, parsed.quantity, parsed.unit)
        # Guardar item a la bbdd de la llista de l'usuari (llista linkada amb l'id de l'usuari)
        mongo.add_item(statement.id, item)
        # Canviar estat usuari
        mongo.update_user_status(statement.id, ESTADO_ADD_ITEM)
        # Mostrar msg de confirmacio.
        markup = InlineKeyboardMarkup()
        bot.send_message(statement.id, item.name + ITEM_DELETED, reply_markup=markup)


class DeleteItem(object):
    def __init__(self, **kwargs):
        pass

    @staticmethod
    def can_process(statement, state, mongo):
        if state == ESTADO_DELETE_ITEM and similar(statement.text, SP_DELETE_ITEM) > MIN:
            return True
        return False

    @staticmethod
    def process(statement, state, mongo):
        return similar(statement.text, SP_DELETE_ITEM)

    @staticmethod
    def response(statement, bot, mongo):
        # Montar item que es vol afegir a la llista
        parsed = parserIngredient(statement.text)
        item = Item(parsed.ingredient, parsed.quantity, parsed.unit)
        # Eliminar item de la bbdd de la llista de l'usuari
        if mongo.delete_item(statement.id, item)["nModified"] > 0:
            mongo.update_user_status(statement.id, ESTADO_DELETE_ITEM)
            msg = item.name + ITEM_DELETED
        else:
            msg = CANT_DELETE
        markup = InlineKeyboardMarkup()
        bot.send_message(statement.id, msg, reply_markup=markup)


# TODO si no hay ningun item sale un mensaje en la lista o el chatbot dice que la lista esta vacía
class ListItems(object):
    def __init__(self, **kwargs):
        pass

    @staticmethod
    def can_process(statement, state, mongo):
        if state == ESTADO_LIST_ITEMS and similar(statement.text, SP_LIST_ITEMS) > MIN:
            return True
        return False

    @staticmethod
    def process(statement, state, mongo):
        return similar(statement.text, SP_LIST_ITEMS)

    @staticmethod
    def response(statement, bot, mongo):
        # Devolver todos lo items de lista de un usuario
        global msg
        shopping_list = mongo.search_list(statement.id)
        if shopping_list is not None:
            msg = SP_LIST_ITEMS + COLS

            i = 1
            for e in shopping_list["items"]:
                msg += i + ". " + e["item"] + "\t" + e["quantity"] + "\t" + e["unit"] + "\n"
                i += 1

        else:
            # Lista vacia
            msg = NO_ITEMS
        # Canviar estat usuari
        mongo.update_user_status(statement.id, ESTADO_LIST_ITEMS)
        markup = InlineKeyboardMarkup()
        bot.send_message(statement.id, msg, reply_markup=markup)
