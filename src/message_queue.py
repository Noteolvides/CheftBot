import time
from collections import deque
import telegram
import threading


class DelayQueue(object):
    def __init__(self, bot):
        self.queues = dict()
        self.bot = bot

    def addMessage(self, chat_id, message, image):
        bundle = [chat_id, message, image]
        if chat_id not in self.queues:
            self.queues[chat_id] = deque(maxlen=20)
        self.queues[chat_id].append(bundle)

    def startQueue(self):
        t2 = threading.Thread(target=self.sendMessage)
        t2.start()

    def sendMessage(self):
        while True:
            for key in self.queues:
                if len(self.queues[key]) > 0:
                    bundle = self.queues[key].popleft()
                    if not bundle[2]:
                        # Mensage
                        self.bot.send_message(bundle[0], bundle[1])
                    else:
                        # imagen
                        self.bot.send_photo(bundle[0], bundle[1])
                    if len(self.queues[key]) > 0:
                        self.bot.send_chat_action(chat_id=bundle[0], action=telegram.ChatAction.TYPING)
            time.sleep(1)
