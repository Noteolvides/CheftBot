import logging

from telegram import ReplyKeyboardMarkup, ReplyKeyboardRemove, Bot

from Recipe import huevoFrito, huevoDuro
from User import User
from main import MENU, LISTA_DE_LA_COMPRA, ACTION, RECEPIE_YES_OR_NO, RECEPIE_STEPS, RECEPIE_FINISH

# Start
ENTRY_POINT = "Hola soy chefBot tu pinche en la cocina."
ENTRY_POINT_2 = "Tienes diferentes opcciones para elegir que te gustaria hacer hoy?"

# Error
INPUT_ERROR = "Te qeuivocaste gueiy"

# Menu
MENU_OPTIONS = "Con los ingredientes que ya has comprado puedes hacer las siguientes recetas"

# Receta
RECEPIE_START = "Perfecto, para esta receta vas a necesitar:"
RECEPIE_READY = "¿Estas listo para empezar?, lo tienes todo \U0001F923"
RECEPIE_START_STEPS = "Comencemos \U0001F92E"
RECEPIE_STEPS_FINISH = "POLLASSSS de postre"

# Activamos el Logger y decimos que el output sea debug.log
from telegram.ext import ConversationHandler

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO, filename="debug.log")

logger = logging.getLogger(__name__)

# State definitions for top level conversation
SELECTING_ACTION, ADDING_MEMBER, ADDING_SELF, DESCRIBING_SELF = map(chr, range(4))
# State definitions for second level conversation
SELECTING_LEVEL, SELECTING_GENDER = map(chr, range(4, 6))
# State definitions for descriptions conversation
SELECTING_FEATURE, TYPING = map(chr, range(6, 8))
# Meta states
STOPPING, SHOWING = map(chr, range(8, 10))
# Shortcut for ConversationHandler.END
END = ConversationHandler.END


def start(update, context):
    update.message.reply_text(text=ENTRY_POINT)
    reply_keyboard = [["MENU"], ["LISTA_DE_LA_COMPRA"]]

    update.message.reply_text(ENTRY_POINT_2, reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True))

    context.bot.sendPhoto(chat_id=update.message.chat_id, photo='https://telegram.org/img/t_logo.png')
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

    #reply_keyboard = [["Si :)"]]
    #update.message.reply_text(text='La has liado', reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True))
    #start(update, context)


def listPurchase(update, context):
    return LISTA_DE_LA_COMPRA


listOfPosibleRecipies = [huevoFrito, huevoDuro]


def menu(update, context):
    # LLAMADA A LA BASE DE DATOS PARA Obtener que 2 platos
    reply_keyboard = [[listOfPosibleRecipies[0].title], [listOfPosibleRecipies[1].title], ["Añadir ingredientes"]]

    update.message.reply_text(MENU_OPTIONS, reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True))

    print(update.message)

    return MENU


def stop(update, context):
    update.message.reply_text("Estas en stop, volvamos a empezar")
    start(update, context)
    return ACTION


def noMatch(update, context):
    update.message.reply_text(text=INPUT_ERROR)


def recepie(update, context):
    update.message.reply_text(RECEPIE_START, reply_markup=ReplyKeyboardRemove())

    for ingredient in listOfPosibleRecipies[0].ingredients:
        update.message.reply_text(ingredient)

    reply_keyboard = [["Si"]]

    update.message.reply_text(text=RECEPIE_READY,
                              reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True))

    return RECEPIE_YES_OR_NO


def addIngredient():
    return ACTION


def recepie_yes(update, context):
    reply_keyboard = [["Si"]]
    update.message.reply_text(text=RECEPIE_START_STEPS,
                              reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True))
    return RECEPIE_STEPS


juanjo = User(0, ["huevo", "sal", "aceite"])


def steps(update, context):
    update.message.reply_text(listOfPosibleRecipies[0].instructions[juanjo.step_counter])
    juanjo.step_counter += 1

    if len(listOfPosibleRecipies[0].instructions) == juanjo.step_counter:
        reply_keyboard = [["Gracias!"]]
        update.message.reply_text(text="Bon apetit",
                                  reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True))
        return RECEPIE_FINISH

    reply_keyboard = [["SI!"]]
    update.message.reply_text(text="¿Lo tienes ya?",
                              reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True))

    return RECEPIE_STEPS


def stepsFinish(update, context):
    juanjo.step_counter = 0
    update.message.reply_text(RECEPIE_STEPS_FINISH)
    start(update, context)
    return ACTION
