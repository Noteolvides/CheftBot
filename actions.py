import logging

from telegram import InlineKeyboardButton, InlineKeyboardMarkup

from main import MENU, RECETAS, LISTA_DE_LA_COMPRA, ACTION

ENTRY_POINT = "Hola soy chefBot tu pinche en la cocina."
ENTRY_POINT_2 = "Tienes diferentes opcciones para elegir que te gustaria hacer hoy?"

# Activamos el Logger y decimos que el output sea debug.log
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO, filename="debug.log")

logger = logging.getLogger(__name__)


# Comando de inicio siempre pasa, aqui es la introduccion el bot
# def start(update, context):
#     # update.message.reply_text(ENTRY_POINT)
#     text = 'Ysadasdou may add a familiy member, yourself show the gathered data or end the ' \
#           'conversation. To abort, simply type /stop.'
#     buttons = [[
#         InlineKeyboardButton(text='MENU', callback_data=str("B")),
#         InlineKeyboardButton(text='RECETAS', callback_data=str("A")),
#         [InlineKeyboardButton(text='LISTA DE LA COMPRA', callback_data=str("C"))]
#     ]]
#     keyboard = InlineKeyboardMarkup(buttons)
#     # Send gif
#     update.message.reply_text(text=text, reply_markup=keyboard)


def start(update, context):
    """Select an action: Adding parent/child or show data."""
    update.message.reply_text(ENTRY_POINT)
    buttons = [[
        InlineKeyboardButton(text='Menu', callback_data=str(MENU)),
        InlineKeyboardButton(text='Recetas', callback_data=str(RECETAS))
    ], [
        InlineKeyboardButton(text='Lista de la compra', callback_data=str(LISTA_DE_LA_COMPRA))
    ]]
    keyboard = InlineKeyboardMarkup(buttons)

    update.message.reply_text(text=ENTRY_POINT_2, reply_markup=keyboard )
    update.message.reply_text(text=" ")

    return ACTION

# por si alguien se pierde puede decir help y hacer lo que quiera
def help(update, context):
    update.message.reply_text('Help!')


# Por defecto hace echo
def echo(update, context):
    update.message.reply_text(update.message.text)


def error(update, context):
    # Si hay alguno error se lo enviamos al logger
    logger.warning('Update "%s" caused error "%s"', update, context.error)


def listPurchase(update, context):
    update.message.reply_text("Estas en la lista de la compra")


def recetas(update, context):
    update.callback_query.edit_message_text(text="Estas en recetas")


def menu(update, context):
    """update.message.reply_text("Estas en menu")"""
    update.callback_query.edit_message_text(text="Estas en menu")


def stop(update, context):
    update.message.reply_text("Estas en stop")
