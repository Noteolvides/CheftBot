import types

from chatterbot.conversation import Statement
from chatterbot.comparisons import JaccardSimilarity
from chatterbot.logic import LogicAdapter


class ShoppingChosser(LogicAdapter):

    def __init__(self, chatbot, **kwargs):
        super().__init__(chatbot, **kwargs)

    def can_process(self, statement):
        lower_string = statement.text
        if "shopping" in lower_string.lower():
            return True
        return False

    def process(self, statement, additional_response_selection_parameters=None):
        response_statement = Statement(text="What would you like to do now")
        response_statement.confidence = JaccardSimilarity().compare(statement, Statement(text="Shopping list"))
        return response_statement


class AddItemShopping(LogicAdapter):

    def __init__(self, chatbot, **kwargs):
        super().__init__(chatbot, **kwargs)

    def can_process(self, statement):
        lower_string = statement.text
        if "shopping" in lower_string.lower():
            return True
        return False

    def process(self, statement, additional_response_selection_parameters=None):
        response_statement = Statement(text="Add item shopping list baby")
        response_statement.confidence = JaccardSimilarity().compare(statement, Statement(text="Add item Shopping list"))
        return response_statement


class ShowListShopping(LogicAdapter):

    def __init__(self, chatbot, **kwargs):
        super().__init__(chatbot, **kwargs)

    def can_process(self, statement):
        lower_string = statement.text
        if "shopping" in lower_string.lower():
            return True
        return False

    def process(self, statement, additional_response_selection_parameters=None):
        response_statement = Statement(text="List item shopping list baby")
        response_statement.confidence = JaccardSimilarity().compare(statement,
                                                                    Statement(text="List items Shopping list"))
        return response_statement
