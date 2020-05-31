import emoji

NOT_UNDERSTAND = "Sorry I didn\'t understand that :confused:"
MINIMUM_CONFIDENCE = 0.2


class Chatter(object):

    def __init__(self, adapters, mongo, **kwargs):
        self.logic_adapters = adapters
        self.mongo = mongo

    def checkIfMatch(self, statement):
        max_confidence = -1
        win_adapter = -1

        # TODO igual no hace falta hacer el can process y el processm ¿quizas con 1 solo ya basta?
        state = self.mongo.search_user_by_id(statement.id)["status"]
        for i, adapter in enumerate(self.logic_adapters):
            if adapter.can_process(statement, state, self.mongo):
                confidence = adapter.process(statement, state, self.mongo)

                if confidence > max_confidence:
                    win_adapter = i
                    max_confidence = confidence

        if max_confidence < MINIMUM_CONFIDENCE:
            return -1
        return win_adapter

    def generateResponse(self, win, statement, bot):
        # TODO la respuesta tambien cambiaria segun el estado de la conversacion
        if win == -1:
            TextNotFound.response(statement, bot, self.mongo)
        else:
            self.logic_adapters[win].response(statement, bot, self.mongo)


class Statement(object):
    def __init__(self, statement, id, message):
        self.text = statement
        self.id = id
        self.message = message


# Para pedir al user que nos puntue la receta que acaba de preparar
class TextNotFound(object):
    def __init__(self, **kwargs):
        pass

    @staticmethod
    def can_process(statement, status, mongo):
        return 1

    @staticmethod
    def process(statement, status, mongo):
        return 1

    @staticmethod
    def response(statement, bot, mongo):
        bot.send_message(statement.id, emoji.emojize(NOT_UNDERSTAND, use_aliases=True))


