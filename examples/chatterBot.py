from chatterbot import ChatBot
from chatterbot.trainers import ChatterBotCorpusTrainer, UbuntuCorpusTrainer

if __name__ == '__main__':
    # Uncomment the following lines to enable verbose logging
    # import logging
    # logging.basicConfig(level=logging.INFO)

    # Create a new instance of a ChatBot
    bot = ChatBot(
        'Terminal'
    )

    trainer = ChatterBotCorpusTrainer(bot)

    trainer.train(
        "chatterbot.corpus.english"
    )



    # Now let's get a response to a greeting

    print('Type something to begin...')

    # The following loop will execute each time the user enters input
    while True:
        try:
            user_input = input()

            bot_response = bot.get_response(user_input)

            print(bot_response)

        # Press ctrl-c or ctrl-d on the keyboard to exit
        except (KeyboardInterrupt, EOFError, SystemExit):
            break
