class Chatter(object):

    def __init__(self, adapters, **kwargs):
        self.logic_adapters = adapters

    def checkIfMatch(self, statement):
        max_confidence = -1
        win_adapter = -1

        for i, adapter in enumerate(self.logic_adapters):
            if adapter.can_process(statement):
                confidence = adapter.process(statement)

                if confidence > max_confidence:
                    win_adapter = i
                    max_confidence = confidence

        return win_adapter

    def generateResponse(self, win, statement,bot):
        self.logic_adapters[win].response(statement,bot)


class Statement(object):
    def __init__(self, statement, id):
        self.text = statement
        self.id = id
