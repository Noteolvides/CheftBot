import re

import telebot
import emoji
from telebot import types
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton

from src.BBDD import MongoDB
from src.Model.User import User
from src.food_recon import predict_photo
from src.general_adapter import StopOption
from src.logger import startLogger
from src.ingredients_Adapter import addIngredient, ingredientChosser, addIngredientNameManually, listIngredient
from src.message_queue import QueueGestor
from src.recipe_adapter import SeeRecipes, NavigationReciepe, ChooseRecipe, MoreInfoRecipe, CookingRecipe, MealRating
from src.chatter import Chatter
from src.chatter import Statement

API_TOKEN = '1037754398:AAEKk_zp4e686AmN2s8ZcHqPhPDoTxULB58' # '1037754398:AAEKk_zp4e686AmN2s8ZcHqPhPDoTxULB58'
bot = telebot.TeleBot(API_TOKEN)
logger = startLogger()
mongo = MongoDB()
chatter = Chatter(
    [addIngredientNameManually, ingredientChosser, listIngredient, addIngredient,
     SeeRecipes, ChooseRecipe, MoreInfoRecipe, CookingRecipe, MoreInfoRecipe, NavigationReciepe, MealRating,
     StopOption],
    mongo)

commands = {  # command description used in the "help" command
    'start': 'Start the bot',
}
message_queue = QueueGestor(bot)
# message_queue.startQueue()

if __name__ == '__main__':
    @bot.message_handler(commands=['start'])
    def send_welcome(message):
        mongo.new_user(User(message.chat.id, "", 0, ""))
        mongo.update_user_status(message.chat.id, 0)
        chat_id = message.chat.id
        bot.send_message(chat_id, "This is Chefbot")
        markup = types.ReplyKeyboardMarkup(one_time_keyboard=True)
        markup.add('Shopping list', 'Ingredients', 'Recipes')
        bot.reply_to(message, 'What would you like to do', reply_markup=markup)


    @bot.message_handler(commands=['help'])
    def command_help(m):
        cid = m.chat.id
        help_text = "The following commands are available: \n"
        for key in commands:  # generate help text out of the commands dictionary defined at the top
            help_text += "/" + key + ": "
            help_text += commands[key] + "\n"
        bot.send_message(cid, help_text)


    @bot.message_handler(content_types=['text'])
    def generic_text(message):
        try:
            s = Statement(message.text, message.chat.id)
            can_answer = chatter.checkIfMatch(statement=s)
            chatter.generateResponse(can_answer, s, bot)
        except:
            bot.send_message(message.chat.id, "Could you repeat?")


    @bot.callback_query_handler(func=lambda call: True)
    def callback_query(call):
        # Check the state and change to state if not or yes
        if call.data == "cb_yes":
            bot.answer_callback_query(call.id, "Answer is Yes")
            bot.send_message(call.message.chat.id, "Nice, i am a genius")
        elif call.data == "cb_no":
            bot.answer_callback_query(call.id, "Answer is No")
            bot.send_message(call.message.chat.id, emoji.emojize("Sorry, you will have to add it by hand "
                                                                 ":disappointed_face:"))
        elif call.data == "add_ingredients":
            bot.delete_message(call.message.chat.id, call.message.message_id)
            addIngredient.response(Statement("", call.message.chat.id), bot, mongo)
        elif call.data == "list_ingredients":
            listIngredient.response(Statement("", call.message.chat.id), bot, mongo)
        elif call.data == ""


    @bot.message_handler(content_types=['photo'])
    def photo(message):
        bot.send_message(message.chat.id, "Are you trying to add an ingredient, lest see if our system can figure out "
                                          "what it is")
        file_id = message.photo[0].file_id
        file_info = bot.get_file(file_id)
        downloaded_file = bot.download_file(file_info.file_path)
        text = emoji.emojize("Humm..., let me think :thinking_face:")
        bot.send_message(message.chat.id, text)
        ingredient = predict_photo(downloaded_file)
        item = 'It might be an ' + ingredient
        bot.reply_to(message, item)
        markup = InlineKeyboardMarkup()
        markup.row_width = 2
        markup.add(InlineKeyboardButton("Yes", callback_data="yes_add_ingredient"),
                   InlineKeyboardButton("No", callback_data="no_add_ingredient"))
        bot.send_message(message.chat.id, "Am i right bro?", reply_markup=markup)
        posible_ingredient = {"name": ingredient, "amount": 0, "unit": ""}
        mongo.possible_ingredient(message.chat.id, posible_ingredient)


    bot.polling()
