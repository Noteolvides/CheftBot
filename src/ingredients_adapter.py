from chatterbot.conversation import Statement
from chatterbot.comparisons import JaccardSimilarity
from chatterbot.logic import LogicAdapter


class addIngredient(LogicAdapter):

    def __init__(self, chatbot, **kwargs):
        super().__init__(chatbot, **kwargs)

    def can_process(self, statement):
        # TODO(DATABASE) CALL DATABASE TO SEE IF I AM IN THE CORRECT STATE FOR NOW, SEARCH WORD INGREDIENT
        lower_string = statement.text
        if "ingredient" in lower_string.lower():
            return True
        return False

    def process(self, statement, additional_response_selection_parameters=None):
        response_statement = Statement(text="Great", id=12)
        response_statement.confidence = JaccardSimilarity().compare(statement, Statement(text="add ingredient"))
        return response_statement
