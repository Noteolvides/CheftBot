import actions

from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, ConversationHandler, CallbackQueryHandler

MENU, RECETAS, LISTA_DE_LA_COMPRA, ACTION = map(chr, range(4))


def main():
    # Empezamos el porgrama añadimos nuestro token dado por telegram y añadimos use context para versiones nuevas de
    # Telegram Bot
    updater = Updater("852896929:AAHJJVUoUMO6hTxYV3fEaqn2tjNOn_wmzfs", use_context=True)

    # Para seleccionar el comando enviado activamos el dispacher
    dp = updater.dispatcher
    conv_handler = ConversationHandler(
        # Cada uno de estos comandos enviados con /comando llamara a la funcion
        entry_points=[CommandHandler("start", actions.start), CommandHandler("help", actions.help)],

        states={
            ACTION: [MessageHandler(Filters.regex('^MENU$'), actions.menu),
                     MessageHandler(Filters.regex('^RECETAS'), actions.recetas),
                     MessageHandler(Filters.regex('^LISTA_DE_LA_COMPRA'), actions.listPurchase)],
        },

        fallbacks=[CommandHandler("stop", actions.stop)]
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
