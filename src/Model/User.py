class User(object):
    def __init__(self, token, username, status, current_keyboard):
        self.token = token
        self.username = username
        self.status = status
        self.current_keyboard = current_keyboard