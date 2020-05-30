import time
from collections import deque
import telegram
import threading

from telegram.ext import DelayQueue

from src.test import EsperaQueue

DELAY_TYPE_TEXT = 0
DELAY_TYPE_PHOTO = 1


# DELAY_TYPE_TEXT = 0
# DELAY_TYPE_TEXT = 0

class QueueGestor(object):
	def __init__(self, bot):
		self.queues = dict()
		self.bot = bot

	def add_message(self, chat_id, message, type):
		if chat_id not in self.queues:
			self.queues[chat_id] = EsperaQueue(burst_limit=1, time_limit_ms=1000)

		if type == DELAY_TYPE_TEXT:
			self.queues[chat_id](self.bot.send_message, chat_id, message)

		if type == DELAY_TYPE_PHOTO:
			self.queues[chat_id](self.bot.send_photo, chat_id, message)

		self.queues[chat_id](self.bot.send_chat_action, chat_id=chat_id, action=telegram.ChatAction.TYPING)

	#
	# def startQueue(self):
	#     t2 = threading.Thread(target=self.sendMessage)
	#     t2.start()
	#
	# def sendMessage(self):
	#     while True:
	#         for key in self.queues:
	#             if len(self.queues[key]) > 0:
	#                 bundle = self.queues[key].popleft()
	#                 if not bundle[2]:
	#                     # Mensage
	#                     self.bot.send_message(bundle[0], bundle[1])
	#                 else:
	#                     # imagen
	#                     self.bot.send_photo(bundle[0], bundle[1])
	#                 if len(self.queues[key]) > 0:
	#                     self.bot.send_chat_action(chat_id=bundle[0], action=telegram.ChatAction.TYPING)
	#         time.sleep(1)
