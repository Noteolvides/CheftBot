class Chatter(object):

    def __init__(self, adapters, mongo, **kwargs):
        self.logic_adapters = adapters
        self.mongo = mongo

    def checkIfMatch(self, statement):
        max_confidence = -1
        win_adapter = -1

        # TODO igual no hace falta hacer el can process y el processm ¿quizas con 1 solo ya basta?
        state = self.mongo.search_user_by_id(statement.id)["state"]
        for i, adapter in enumerate(self.logic_adapters):
            if adapter.can_process(statement, state):
                confidence = adapter.process(statement, state)

                if confidence > max_confidence:
                    win_adapter = i
                    max_confidence = confidence

        return win_adapter

    def generateResponse(self, win, statement, bot):
        # TODO la respuesta tambien cambiaria segun el estado de la conversacion
        self.logic_adapters[win].response(statement, bot, self.mongo)


class Statement(object):
    def __init__(self, statement, id):
        self.text = statement
        self.id = id
