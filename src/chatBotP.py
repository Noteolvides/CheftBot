from chatterbot import ChatBot
from chatterbot.conversation import Statement
from chatterbot.trainers import ChatterBotCorpusTrainer

if __name__ == '__main__':

    # Uncomment the following lines to enable verbose logging
    # import logging
    # logging.basicConfig(level=logging.INFO)

    # Create a new instance of a ChatBot
    bot = ChatBot(
        'Chefbot',
        logic_adapters=[
            {
                'import_path': 'food_Adapter.ResponseAdapter',
            },
        ],
    )


    # The following loop will execute each time the user enters input
    while True:
        try:
            user_input = input()
            # bot_response = bot.get_response(user_input)
            number = {"1": 1}
            response_statement = Statement(text=user_input, id="12")
            bot_response = bot.generate_response(response_statement, number)
            print(bot_response)

        # Press ctrl-c or ctrl-d on the keyboard to exit
        except (KeyboardInterrupt, EOFError, SystemExit,AttributeError):
            print("Shit")
