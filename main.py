import actions

from telegram.ext import Updater, CommandHandler, MessageHandler, Filters


def main():
    # Empezamos el porgrama añadimos nuestro token dado por telegram y añadimos use context para versiones nuevas de
    # Telegram Bot
    updater = Updater("852896929:AAHJJVUoUMO6hTxYV3fEaqn2tjNOn_wmzfs", use_context=True)

    # Para seleccionar el comando enviado activamos el dispacher
    dp = updater.dispatcher

    # Cada uno de estos comandos enviados con /comando llamara a la funcion
    dp.add_handler(CommandHandler("start", actions.start))
    dp.add_handler(CommandHandler("help", actions.help))

    # Si nos envian un mensaje que sea texto pues llamamos a la funcion echo
    dp.add_handler(MessageHandler(Filters.text, actions.echo))

    # si hay error pues funcion de erorr
    dp.add_error_handler(actions.error)

    # Miramos si tenemos algun mensaje
    updater.start_polling()

    # Nos quedamos esperando el ctrl o finalizacion de programa
    updater.idle()


if __name__ == '__main__':
    main()
