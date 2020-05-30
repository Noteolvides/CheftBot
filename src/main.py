import telebot
import emoji
from telebot import types
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton

from src.BBDD import MongoDB
from src.Model.User import User
from src.food_recon import predict_photo
from src.general_adapter import StopOption
from src.logger import startLogger
from src.ingredients_Adapter import addIngredient, ingredientChosser, addIngredientNameManually, listIngredient, \
    yesIngredient, noIngredient, removeIngredient
from src.message_queue import QueueGestor
from src.recipe_adapter import SeeRecipes, NavigationReciepe, ChooseRecipe, MoreInfoRecipe, CookingRecipe, MealRating
from src.chatter import Chatter
from src.chatter import Statement
from src.test2 import getGif
from src.shoppingList import DeleteItem, AddItem, ListItems

API_TOKEN = '852896929:AAHJJVUoUMO6hTxYV3fEaqn2tjNOn_wmzfs'
bot = telebot.TeleBot(API_TOKEN)
logger = startLogger()
mongo = MongoDB()
chatter = Chatter(
    [addIngredientNameManually, ingredientChosser,listIngredient, addIngredient, SeeRecipes, ChooseRecipe, MoreInfoRecipe,
     CookingRecipe, MoreInfoRecipe, NavigationReciepe, MealRating, AddItem, DeleteItem, ListItems], mongo)

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
        bot.send_message(chat_id,
                         "<b>Welcome to chefbot</b>\nIn this chatbot you can find a set of tools to develop your culinary abilities\n<i>Shopping list : You can add the missing products.</i>\n<i>Ingredients : You can add the products that you already have.</i>\n<i>Recepies : You can choose a lot of recipies to make :).</i>\n<u>Come on, what are you waiting for</u>",
                         parse_mode="HTML")
        markup = types.ReplyKeyboardMarkup(one_time_keyboard=True)
        markup.add('Shopping list', 'Ingredients', 'Recipes')
        bot.send_animation(chat_id, "https://media1.tenor.com/images/3e4d211cd661a2d7125a6fa12d6cecc6/tenor.gif")
        bot.reply_to(message, 'What would you like to do?', reply_markup=markup)


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
            s = Statement(message.text, message.chat.id, message)
            can_answer = chatter.checkIfMatch(statement=s)
            chatter.generateResponse(can_answer, s, bot)
        except:
            bot.send_message(message.chat.id, "Could you repeat?")


    @bot.callback_query_handler(func=lambda call: True)
    def callback_query(call):
        try:

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
                addIngredient.response(Statement("", call.message.chat.id, None), bot, mongo)
            elif call.data == "list_ingredients":
                listIngredient.response(Statement("", call.message.chat.id, None), bot, mongo)
            elif call.data == "no_add_ingredient":
                bot.delete_message(call.message.chat.id, call.message.message_id)
                bot.delete_message(call.message.chat.id, call.message.message_id - 1)
                bot.send_message(call.message.chat.id, "Ouch,could you repeat again?")
                addIngredient.response(Statement("", call.message.chat.id, None), bot, mongo)
                mongo.update_user_status(call.message.chat.id, 22)
            elif call.data == "yes_add_ingredient":
                bot.delete_message(call.message.chat.id, call.message.message_id)
                bot.send_message(call.message.chat.id, "Yeah,knew it, i am a hungry genius,:P")
                posible_ingredient = mongo.get_possible_ingredient(call.message.chat.id)
                bot.send_animation(call.message.chat.id, getGif(posible_ingredient["name"]))
                if mongo.get_ingredient_by_name(call.message.chat.id, posible_ingredient["name"]) is None:
                    mongo.new_ingredient(call.message.chat.id, posible_ingredient)
                else:
                    mongo.update_ingredient(call.message.chat.id, posible_ingredient)
                bot.send_message(call.message.chat.id, "You can add another one, or do other things")
                mongo.update_user_status(call.message.chat.id, 22)
            elif call.data == "remove_ingredient":
                regex = r"(?<=Ingredient : )(.*)(?=Quantity : )"
                test_str = call.message.text.replace('\n', '')
                matches = re.search(regex, test_str, re.MULTILINE)
                ingredient_en = matches.group().encode("ascii", "ignore")
                ingredient_de = ingredient_en.decode()
                mongo.delete_ingredient_by_name(call.message.chat.id, ingredient_de)
                bot.delete_message(call.message.chat.id, call.message.message_id)
                bot.send_message(call.message.chat.id, ingredient_de + " removed")
        except:
            mongo.update_user_status(call.message.chat.id, 0)
            bot.send_message(call.message.chat.id, "Could you repeat")


    @bot.message_handler(content_types=['photo'])
    def photo(message):
        try:
            bot.send_message(message.chat.id,
                             "Are you trying to add an ingredient, lest see if our system can figure out "
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
        except:
            mongo.update_user_status(message.chat.id, 0)
            bot.send_message(message.chat.id, "Could you repeat")


    bot.polling()
