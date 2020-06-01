from telebot import types
from difflib import SequenceMatcher


def similar(a, b):
    return SequenceMatcher(None, a, b).ratio()


def initial_menu(chat_id, bot, mongo):
    bot.send_message(chat_id,
                     "<b>Welcome to chefbot</b>\nIn this chatbot you can find a set of tools to develop your culinary abilities\n<i>Shopping list : You can add the missing products.</i>\n<i>Ingredients : You can add the products that you already have.</i>\n<i>Recepies : You can choose a lot of recipies to make :).</i>\n<u>Come on, what are you waiting for</u>",
                     parse_mode="HTML")
    markup = types.ReplyKeyboardMarkup(one_time_keyboard=True)
    markup.add('Shopping list', 'Ingredients', 'Recipes')
    bot.send_animation(chat_id, "https://media1.tenor.com/images/3e4d211cd661a2d7125a6fa12d6cecc6/tenor.gif")
    bot.send_message(chat_id, 'What would you like to do?', reply_markup=markup)


class StopOption(object):
    def __init__(self, **kwargs):
        pass

    @staticmethod
    def can_process(statement, status, mongo):
        return True

    @staticmethod
    def process(statement, status, mongo):
        value0 = similar(statement.text.lower(), "exit")
        value1 = similar(statement.text.lower(), "menu")
        value2 = similar(statement.text.lower(), "stop")
        return max(value0, value1, value2)

    @staticmethod
    def response(statement, bot, mongo):
        bot.send_message(statement.id, "You are on start")
        initial_menu(statement.id, bot, mongo)
        mongo.set_cooking_recipe(statement.id, False)
        mongo.update_user_status(statement.id, 0)

