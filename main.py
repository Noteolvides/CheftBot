import actions

from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, ConversationHandler, CallbackQueryHandler

MENU, LISTA_DE_LA_COMPRA, ACTION, RECEPIE_YES_OR_NO, RECEPIE_STEPS, RECEPIE_FINISH = map(chr, range(6))


def main():
    # Empezamos el porgrama añadimos nuestro token dado por telegram y añadimos use context para versiones nuevas de
    # Telegram Bot
    updater = Updater("852896929:AAHJJVUoUMO6hTxYV3fEaqn2tjNOn_wmzfs", use_context=True)

    # Para seleccionar el comando enviado activamos el dispacher
    dp = updater.dispatcher
    conv_handler = ConversationHandler(
        # Cada uno de estos comandos enviados con /comando llamara a la funcion
        entry_points=[CommandHandler("start", actions.start),
                      MessageHandler(Filters.regex('^Hola$'), actions.start)],

        states={
            ACTION: [MessageHandler(Filters.regex('^Menu$'), actions.menu),
                     MessageHandler(Filters.regex('^Ver la lista de la compra'), actions.menu)],
            MENU: [
                MessageHandler(Filters.text, actions.recepie),
            ],
            RECEPIE_YES_OR_NO: [
                MessageHandler(Filters.regex('^Si$'), actions.recepie_yes),
                MessageHandler(Filters.regex('^No$'), actions.start),
            ],
            RECEPIE_STEPS: [
                MessageHandler(Filters.text, actions.steps),
            ],
            RECEPIE_FINISH: [
                MessageHandler(Filters.text, actions.stepsFinish),
            ]
        },

        fallbacks=[CommandHandler("stop", actions.stop),
                   CommandHandler("start", actions.start),
                   MessageHandler(Filters.text, actions.noMatch)]
    )

    dp.add_handler(conv_handler)

    # si hay error pues funcion de error
    dp.add_error_handler(actions.error)

    # Miramos si tenemos algun mensaje
    updater.start_polling()

    # Nos quedamos esperando el ctrl o finalizacion de programa
    updater.idle()


if __name__ == '__main__':
    main()
