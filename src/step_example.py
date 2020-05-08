
import telebot
from chatterbot import ChatBot
from chatterbot.conversation import Statement
from chatterbot.trainers import ChatterBotCorpusTrainer
from telebot import types

API_TOKEN = '852896929:AAHJJVUoUMO6hTxYV3fEaqn2tjNOn_wmzfs'

bot = telebot.TeleBot(API_TOKEN)

chatBot = ChatBot(
    'Chefbot',
    logic_adapters=[
        {
            'import_path': 'food_Adapter.ShoppingChosser',
        },
        {
            'import_path': 'food_Adapter.AddItemShopping',
        },
        {
            'import_path': 'food_Adapter.ShowListShopping',
        },
        {
            'import_path': 'ingredients_adapter.addIngredient',
        },
    ],
)


def chooseLogic(input_statement, additional_response_selection_parameters):
    results = []
    result = None
    max_confidence = -1
    winer = -1

    for i, adapter in enumerate(chatBot.logic_adapters):
        if adapter.can_process(input_statement):

            output = adapter.process(input_statement, additional_response_selection_parameters)
            results.append(output)

            if output.confidence > max_confidence:
                winer = i
                result = output
                max_confidence = output.confidence

    print(winer)
    return result


if __name__ == '__main__':

    # Handle '/start' and '/help'
    @bot.message_handler(commands=['help', 'start'])
    def send_welcome(message):
        chat_id = message.chat.id

        bot.send_message(chat_id, "This is Chefbot")
        markup = types.ReplyKeyboardMarkup(one_time_keyboard=True)
        markup.add('Shopping list', 'Ingredients', 'Recipes')
        msg = bot.reply_to(message, 'What would you like to do', reply_markup=markup)
        bot.register_next_step_handler(msg, process_message)


    def process_message(message):
        chat_id = message.chat.id
        try:
            response_statement = Statement(text=message.text, id=chat_id)
            bot_response = chatBot.generate_response(response_statement)
            chooseLogic(response_statement)
        except AttributeError:
            bot_response = Statement(text="Sry could you repeat")

        if bot_response.text != "":
            bot.send_message(chat_id, bot_response.text)
        bot.register_next_step_handler(message, process_message)


    # Enable saving next step handlers to file "./.handlers-saves/step.save".
    # Delay=2 means that after any change in next step handlers (e.g. calling register_next_step_handler())
    # saving will hapen after delay 2 seconds.
    bot.enable_save_next_step_handlers(delay=2)

    # Load next_step_handlers from save file (default "./.handlers-saves/step.save")
    # WARNING It will work only if enable_save_next_step_handlers was called!

    bot.polling()
