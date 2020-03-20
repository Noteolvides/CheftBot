import logging

from telegram import ReplyKeyboardMarkup, ReplyKeyboardRemove

from Recipe import huevoFrito, huevoDuro
from main import MENU, LISTA_DE_LA_COMPRA, ACTION, RECEPIE_YES_OR_NO, RECEPIE_STEPS, RECEPIE_FINISH

# Start
ENTRY_POINT = "Hola soy chefBot tu pinche en la cocina."
ENTRY_POINT_2 = "Tienes diferentes opcciones para elegir que te gustaria hacer hoy?"

# Menu
MENU_OPTIONS = "Con los ingredientes que ya has comprado puedes hacer las siguientes recetas"

# Receta

RECEPIE_START = "Perfecto, para esta receta vas a necesitar:"
RECEPIE_READY = "¿Estas listo para empezar?, lo tienes todo \U0001F923"
RECEPIE_START_STEPS = "Comencemos \U0001F92E"
RECEPIE_STEPS_FINISH = "POLLASSSS"

# Activamos el Logger y decimos que el output sea debug.log
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO, filename="debug.log")

logger = logging.getLogger(__name__)


def start(update, context):
    update.message.reply_text(ENTRY_POINT)
    reply_keyboard = [["MENU"], ["LISTA_DE_LA_COMPRA"]]

    update.message.reply_text(ENTRY_POINT_2, reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True))

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
    return LISTA_DE_LA_COMPRA


listOfPosibleRecipies = [huevoFrito, huevoDuro]


def menu(update, context):
    # LLAMADA A LA BASE DE DATOS PARA Obtener que 2 platos
    reply_keyboard = [[listOfPosibleRecipies[0].title], [listOfPosibleRecipies[1].title], ["Añadir ingredientes"]]

    update.message.reply_text(MENU_OPTIONS, reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True))

    return MENU


def stop(update, context):
    update.message.reply_text("Estas en stop")


def recepie(update, context):
    update.message.reply_text(RECEPIE_START, reply_markup=ReplyKeyboardRemove())

    for ingredient in listOfPosibleRecipies[0].ingredients:
        update.message.reply_text(ingredient)

    update.message.reply_text(RECEPIE_READY)

    return RECEPIE_YES_OR_NO


def addIngredient():
    return ACTION


def recepie_yes(update, context):
    update.message.reply_text(RECEPIE_START_STEPS)
    return RECEPIE_STEPS


contador = 0


def steps(update, context):
    global contador
    update.message.reply_text(listOfPosibleRecipies[0].instructions[contador])
    contador += 1
    if len(listOfPosibleRecipies[0].instructions) == contador:
        return RECEPIE_FINISH
    update.message.reply_text("¿Lo tienes ya?")
    print(contador)
    return RECEPIE_STEPS


def stepsFinish(update, context):
    global contador
    update.message.reply_text(RECEPIE_STEPS_FINISH)
    contador = 0
    start(update, context)
