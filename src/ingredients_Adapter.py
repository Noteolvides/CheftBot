from chatterbot.conversation import Statement
from chatterbot.comparisons import JaccardSimilarity
from chatterbot.logic import LogicAdapter


class addIngredient(object):
    def __init__(self, **kwargs):
        pass

    @staticmethod
    def can_process(statement):
        # TODO(DATABASE) CALL DATABASE TO SEE IF I AM IN THE CORRECT STATE FOR NOW, SEARCH WORD INGREDIENT
        lower_string = statement.text
        if "ingredient" in lower_string.lower():
            return True
        return False

    @staticmethod
    def process(statement):
        return JaccardSimilarity().compare(Statement(statement.text), Statement("add ingredient"))

    @staticmethod
    def response(statement, bot):
        bot.send_message(statement.id, "This is Chefbot")
