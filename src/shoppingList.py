import emoji

from src.Model.Item import Item
from src.general_adapter import initial_menu
from src.ingredients_Adapter import similar, api
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
import json

# Estados Shopping List
ESTADO_ADD_ITEM = 41
ESTADO_DELETE = 42
ESTADO_MARK_ITEM = 43

# Frases de ChatBot
ASK_ITEM_ADD = "Which item would you like to add?"
ASK_ITEM_OR_LIST = "What do you want to delete?"
ASK_ITEM_DELETE = "Which item would you like to delete?"
ASK_ITEM_MARK = "Which item have you bought?"
ITEM_ADDED = "has been added succesfully!"
ITEM_DELETED = "has been deleted"
ITEM_MODIFIED = "has been modified!"
LIST_DELETED = "The list has been deleted"
CANT_DELETE = "This item doesn't exist in the list"
LIST_ITEMS = "These are all the items in the shopping list:\n"
COL = "   Item               |               Amount               |               Unit               \n"
NO_ITEMS = emoji.emojize("There are no items in the shopping list :sob:", use_aliases=True)

# Frases Accion
SP = "Shopping List"
SP_ADD_ITEM = "Add Item"
SP_DELETE_ITEM = "Delete Item"
SP_DELETE_LIST = "Delete Item List"
SP_MARK_ITEM = "Mark Item As Purchased"
SP_LIST_ITEMS = "List Items"

MIN = 0.8
aux_status = 0


class ShoppingListChooser(object):
    def __init__(self, **kwargs):
        pass

    @staticmethod
    def can_process(statement, state, mongo):
        # if similar(statement.text, SP) > MIN:
        #     return True
        # return False
        return True

    @staticmethod
    def process(statement, state, mongo):
        return max(similar(statement.text.lower(), SP), similar(statement.text.lower(), "shopping"))

    @staticmethod
    def response(statement, bot, mongo):
        ListItems.response(statement, bot, mongo)
        markup = InlineKeyboardMarkup()
        markup.row_width = 2
        markup.add(InlineKeyboardButton(SP_ADD_ITEM, callback_data="add_item"),
                   InlineKeyboardButton(SP_MARK_ITEM, callback_data="purchase"),
                   InlineKeyboardButton(SP_DELETE_ITEM, callback_data="delete_item"),
                   InlineKeyboardButton(SP_DELETE_LIST, callback_data="delete_list"))
        bot.send_message(statement.id, "What do you want to do", reply_markup=markup)


class ListItems(object):
    def __init__(self, **kwargs):
        pass

    @staticmethod
    def can_process(statement, state, mongo):
        if similar(statement.text, SP_LIST_ITEMS.lower()) > MIN:
            return True
        return False

    @staticmethod
    def process(statement, state, mongo):
        return similar(statement.text, SP_LIST_ITEMS.lower())

    @staticmethod
    def response(statement, bot, mongo):
        # Devolver todos lo items de lista de un usuario
        global msg
        shopping_list = mongo.search_list(statement.id)
        if shopping_list is not None and len(shopping_list["items"]) > 0:
            msg = LIST_ITEMS + COL
            for e in shopping_list["items"]:
                msg += "   " + e["item"] + "               |                    " + str(e["quantity"]) + \
                       "                  |                 " + e["unit"] + "\n"
            bot.send_message(statement.id, msg)

        else:
            # Lista vacia
            bot.send_message(statement.id, NO_ITEMS)
            return


# Preguntar a l'usuari quin ingredient vol posar
class AddItem(object):
    def __init__(self, **kwargs):
        pass

    @staticmethod
    def can_process(statement, state, mongo):
        if similar(statement.text, SP_ADD_ITEM) > MIN:
            return True
        return False

    @staticmethod
    def process(statement, state, mongo):
        return similar(statement.text, SP_ADD_ITEM)

    @staticmethod
    def response(statement, bot, mongo):
        # Canviar estat usuari
        aux_status = mongo.search_user_by_id(statement.id)["status"]
        mongo.update_user_status(statement.id, ESTADO_ADD_ITEM)
        bot.send_message(statement.id, ASK_ITEM_ADD)


class DeleteItem(object):
    def __init__(self, **kwargs):
        pass

    @staticmethod
    def can_process(statement, state, mongo):
        if similar(statement.text, SP_DELETE_ITEM) > MIN:
            return True
        return False

    @staticmethod
    def process(statement, state, mongo):
        return similar(statement.text, SP_DELETE_ITEM)

    @staticmethod
    def response(statement, bot, mongo):
        # Canviar estat usuari
        aux_status = mongo.search_user_by_id(statement.id)["status"]
        mongo.update_user_status(statement.id, ESTADO_DELETE)
        bot.send_message(statement.id, ASK_ITEM_DELETE)


class DeleteList(object):
    def __init__(self, **kwargs):
        pass

    @staticmethod
    def can_process(statement, state, mongo):
        if similar(statement.text, SP_DELETE_LIST) > MIN:
            return True
        return False

    @staticmethod
    def process(statement, state, mongo):
        return similar(statement.text, SP_DELETE_LIST)

    @staticmethod
    def response(statement, bot, mongo):
        # Canviar estat usuari
        aux_status = mongo.search_user_by_id(statement.id)["status"]
        mongo.update_user_status(statement.id, ESTADO_DELETE)
        mongo.delete_list(statement.id)
        bot.send_message(statement.id, LIST_DELETED)
        do_smth_else(statement, bot)


class MarkItem(object):
    def __init__(self, **kwargs):
        pass

    @staticmethod
    def can_process(statement, state, mongo):
        if similar(statement.text, SP_MARK_ITEM) > MIN:
            return True
        return False

    @staticmethod
    def process(statement, state, mongo):
        return similar(statement.text, SP_MARK_ITEM)

    @staticmethod
    def response(statement, bot, mongo):
        # Canviar estat usuari
        aux_status = mongo.search_user_by_id(statement.id)["status"]
        mongo.update_user_status(statement.id, ESTADO_MARK_ITEM)
        bot.send_message(statement.id, ASK_ITEM_MARK)


class SPAddingItem(object):
    def __init__(self, **kwargs):
        pass

    @staticmethod
    def can_process(statement, state, mongo):
        if state == ESTADO_ADD_ITEM:
            return True
        return False

    @staticmethod
    def process(statement, state, mongo):
        return MIN

    @staticmethod
    def response(statement, bot, mongo):
        # Montar item que es vol afegir a la llista
        try:
            response = api.parse_ingredients(statement.text)
            if response.status_code == 200:
                text = json.loads(response.text)[0]
                item = Item(text["name"], text["amount"], text["unit"], 0)
                # Guardar item a la bbdd de la llista de l'usuari (llista linkada amb l'id de l'usuari)
                mongo.add_item(statement.id, item)
                # Mostrar msg de confirmacio.
                bot.send_message(statement.id, "The " + item.name + " " + ITEM_ADDED)
                do_smth_else(statement, bot)
            else:
                bot.send_message(statement.id, "This not seem like to exists")
                bot.send_message(statement.id, "Could you repeat?")
        except:
            bot.send_message(statement.id, "This not seem like to exists")
            bot.send_message(statement.id, "Could you repeat?")


class SPDeletingItem(object):
    def __init__(self, **kwargs):
        pass

    @staticmethod
    def can_process(statement, state, mongo):
        if state == ESTADO_DELETE:
            return True
        return False

    @staticmethod
    def process(statement, state, mongo):
        return MIN

    @staticmethod
    def response(statement, bot, mongo):
        # Montar item que es vol eliminar de la llista
        try:
            response = api.parse_ingredients(statement.text)
            if response.status_code == 200:
                text = json.loads(response.text)[0]
                item = Item(text["name"], text["amount"], text["unit"], 0)
                # Eliminar item de la bbdd de la llista de l'usuari
                if mongo.delete_item_list(statement.id, item)["nModified"] > 0:
                    bot.send_message(statement.id, "The " + item.name + " " + ITEM_DELETED)
                    do_smth_else(statement, bot)
                else:
                    bot.send_message(statement.id, CANT_DELETE)
            else:
                bot.send_message(statement.id, "This not seems like to exists")
                bot.send_message(statement.id, "Could you repeat?")
        except:
            bot.send_message(statement.id, "This not seems like to exists")
            bot.send_message(statement.id, "Could you repeat?")


class SPMarkItemDone(object):
    def __init__(self, **kwargs):
        pass

    @staticmethod
    def can_process(statement, state, mongo):
        if state == ESTADO_MARK_ITEM:
            return True
        return False

    @staticmethod
    def process(statement, state, mongo):
        return MIN

    @staticmethod
    def response(statement, bot, mongo):
        # Montar item que es vol eliminar de la llista
        try:
            response = api.parse_ingredients(statement.text)
            if response.status_code == 200:
                ingredient = json.loads(response.text)[0]
                item = Item(ingredient["name"], ingredient["amount"], ingredient["unit"], 0)
                # Eliminar item de la bbdd de la llista de l'usuari
                text = mongo.mark_item(statement.id, item)
                if text is not None:
                    mongo.new_ingredient(statement.id, ingredient)
                    bot.send_message(statement.id, "The " + item.name + " " + ITEM_MODIFIED)
                    do_smth_else(statement, bot)
                    return
                else:
                    bot.send_message(statement.id, CANT_DELETE)
                    return

            bot.send_message(statement.id, "This not seems like to exists,\n Could you repeat?")
        except:
            bot.send_message(statement.id, "This not seems like to exists,\n Could you repeat?")


def do_smth_else(statement, bot):
    markup = InlineKeyboardMarkup()
    markup.row_width = 2
    markup.add(InlineKeyboardButton("Yes", callback_data="yes_sp"),
               InlineKeyboardButton("No", callback_data="no_sp"))
    bot.send_message(statement.id, "Do you want to make more changes on the shopping list?", reply_markup=markup)


class SPYes(object):
    @staticmethod
    def response(statement, bot, mongo):
        ShoppingListChooser.response(statement, bot, mongo)


class SPNo(object):
    @staticmethod
    def response(statement, bot, mongo):
        # Volver al estado anterior de la lista
        mongo.update_user_status(statement.id, aux_status)
        bot.send_message(statement.id, "You have left the shopping list")
        initial_menu(statement, bot, mongo)
