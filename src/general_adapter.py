from telebot import types
from difflib import SequenceMatcher


def similar(a, b):
    return SequenceMatcher(None, a, b).ratio()


def initial_menu(chat_id, bot):
    bot.send_message(chat_id, "This is Chefbot")
    markup = types.ReplyKeyboardMarkup(one_time_keyboard=True)
    markup.add('Shopping list', 'Ingredients', 'Recipes')
    bot.send_message(chat_id=chat_id, text='What would you like to do', reply_markup=markup)


class StopOption(object):
    def __init__(self, **kwargs):
        pass

    @staticmethod
    def can_process(statement, status, mongo):
        return True

    @staticmethod
    def process(statement, status, mongo):
        value1 = similar(statement.text.lower(), "stop")
        value2 = similar(statement.text.lower(), "exit")
        return max(value1, value2)

    @staticmethod
    def response(statement, bot, mongo):
        # Todo estado en BBDD
        bot.send_message(statement.id, "You are on start")
        initial_menu(statement.id, bot)
