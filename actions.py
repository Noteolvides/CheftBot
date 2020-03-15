import logging

# Activamos el Logger y decimos que el output sea debug.log
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO, filename="debug.log")

logger = logging.getLogger(__name__)


# Comando de inicio siempre pasa, aqui es la introduccion el bot
def start(update, context):
    update.message.reply_text('Hi!')


# por si alguien se pierde puede decir help y hacer lo que quiera
def help(update, context):
    update.message.reply_text('Help!')


# Por defecto hace echo
def echo(update, context):
    update.message.reply_text(update.message.text)


def error(update, context):
    # Si hay alguno error se lo enviamos al logger
    logger.warning('Update "%s" caused error "%s"', update, context.error)
