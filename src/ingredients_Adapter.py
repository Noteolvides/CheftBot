import emoji
from chatterbot.conversation import Statement
from chatterbot.comparisons import JaccardSimilarity
from chatterbot.logic import LogicAdapter
from telebot.types import InlineKeyboardMarkup
from telegram import InlineKeyboardButton


class ingredientChosser(object):
    def __init__(self, **kwargs):
        pass

    @staticmethod
    def can_process(statement, state, mongo):
        if state == 0:
            return True
        return False

    @staticmethod
    def can_process(statement, state, mongo):
        return JaccardSimilarity().compare(Statement(statement.text), Statement("ingredient"))

    @staticmethod
    def response(statement, bot, mongo):
        # change state of user
        markup = InlineKeyboardMarkup()
        markup.row_width = 2
        markup.add(InlineKeyboardButton("Add ingredient", callback_data="add_ingredient"),
                   InlineKeyboardButton("List ingredient", callback_data="list_ingredient"))
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
    def can_process(statement, state, mongo):
        return JaccardSimilarity().compare(Statement(statement.text), Statement("list ingredient"))

    @staticmethod
    def response(statement, bot, mongo):
        mongo.update_user_status(statement.id, 21)
        ingredients = mongo.search_user_by_id(statement.id)["ingredients"]
        for ingredient in ingredients:
            bot.send_message(statement.id, print(ingredient))
        else:
            bot.send_message(statement.id, "Seems like you have any ingredients")
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
    def can_process(statement, state, mongo):
        return JaccardSimilarity().compare(Statement(statement.text), Statement("add ingredient"))

    @staticmethod
    def response(statement, bot):
        bot.send_message(statement.id, "Great")
        bot.send_message(statement.id, "You can take a picture, or add it manually.")
        # change state of user


class addIngredientNameManually(object):

    @staticmethod
    def can_process(statement):
        # TODO(DATABASE) CALL DATABASE TO SEE IF I AM IN THE CORRECT STATE FOR NOW, SEARCH WORD INGREDIENT
        lower_string = statement.text
        if "add" in lower_string.lower():
            return True
        return False

    @staticmethod
    def can_process(statement, state, mongo):
        return 1

    @staticmethod
    def response(statement, bot):
        # Ask database to see if the ingredient exist
        if True:
            bot.send_message(statement.id, "Nice, now add the cuantity")
            # Save pending ingredient --> to the database
            # change state of user
        else:
            bot.send_message(statement.id, "This not seem like an ingredient")
            bot.send_message(statement.id, "Could you repeat?")


class addIngredientNameManually(object):

    @staticmethod
    def can_process(statement):
        # TODO(DATABASE) CALL DATABASE TO SEE IF I AM IN THE CORRECT STATE FOR NOW, SEARCH WORD INGREDIENT
        # Check the state of to add quantity of indredient
        return True

    @staticmethod
    def can_process(statement, state, mongo):
        return 1

    @staticmethod
    def response(statement, bot):
        # Parse ingredients and save them to the database
        if True:
            bot.send_message(statement.id, emoji.emojize("Nice, item added to you list of ingredients thumbs_up:"), use_aliases=True)
            # change state of user
        else:
            bot.send_message(statement.id, "This not seem like a cuantity")
            bot.send_message(statement.id, "Could you repeat?")
