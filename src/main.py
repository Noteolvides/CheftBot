import telebot

from telebot import types
from src.logger import startLogger
from src.ingredients_Adapter import addIngredient
from src.chatter import Chatter
from src.chatter import Statement

API_TOKEN = '852896929:AAHJJVUoUMO6hTxYV3fEaqn2tjNOn_wmzfs'
bot = telebot.TeleBot(API_TOKEN)
logger = startLogger()
chatter = Chatter([addIngredient])

if __name__ == '__main__':
    @bot.message_handler(commands=['start'])
    def send_welcome(message):
        chat_id = message.chat.id
        bot.send_message(chat_id, "This is Chefbot")
        markup = types.ReplyKeyboardMarkup(one_time_keyboard=True)
        markup.add('Shopping list', 'Ingredients', 'Recipes')
        bot.reply_to(message, 'What would you like to do', reply_markup=markup)


    @bot.message_handler(content_types=['text'])
    def generi_text(message):
        s = Statement(message.text, message.chat.id)
        can_answer = chatter.checkIfMatch(statement=s)
        if can_answer != -1:
            chatter.generateResponse(can_answer, s,bot)


    bot.polling()
