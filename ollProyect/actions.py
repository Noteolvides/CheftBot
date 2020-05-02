import logging

from telegram import ReplyKeyboardMarkup, ReplyKeyboardRemove

from ollProyect.Recipe import huevoFrito, huevoDuro
from ollProyect.User import User
from ollProyect.main import MENU, LISTA_DE_LA_COMPRA, ACTION, RECEPIE_YES_OR_NO, RECEPIE_STEPS, RECEPIE_FINISH

# Start
ENTRY_POINT = "Hola soy chefBot tu pinche en la cocina."
ENTRY_POINT_2 = "Tienes diferentes opciones para elegir.\n ¿Qué te gustaria hacer hoy?"

# Error
INPUT_ERROR = "Te qeuivocaste gueiy"

# Menu
MENU_OPTIONS = "Con los ingredientes que ya has comprado puedes hacer las siguientes recetas"

# Receta
RECEPIE_START = "Perfecto, para esta receta vas a necesitar:"
RECEPIE_READY = "¿Estas listo para empezar?, lo tienes todo \U0001F923"
RECEPIE_START_STEPS = "Comencemos \U0001F64C"
RECEPIE_STEPS_FINISH = "Bienn ya lo has hecho \U0001F61C"

# Activamos el Logger y decimos que el output sea debug.log
from telegram.ext import ConversationHandler

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO, filename="../debug.log")

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

users = dict()


def start(update, context):
    if users.get(update.message.chat_id) is None:
        users.update({update.message.chat_id: User()})
    update.message.reply_text(text=ENTRY_POINT)
    reply_keyboard = [["Menu"], ["Ver la lista de la compra"]]

    update.message.reply_text(ENTRY_POINT_2, reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True))
    context.bot.send_animation(chat_id=update.message.chat_id,
                               animation="https://lh6.googleusercontent.com/HM2ZmlN6KE8G47UdhSHUGizt0vtza4RZt0OhFdRJFOWtIXVi2b_SzwNhCAoTDFNQNhSGGa4htzjqJOOSncdw=w683-h696",
                               duration=None,
                               width=None,
                               height=None, thumb=None, caption=None,
                               parse_mode=None, disable_notification=False, reply_to_message_id=None, reply_markup=None,)

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


def steps(update, context):
    update.message.reply_text(listOfPosibleRecipies[0].instructions[users.get(update.message.chat_id).step_counter])
    users.get(update.message.chat_id).step_counter += 1

    if len(listOfPosibleRecipies[0].instructions) == users.get(update.message.chat_id).step_counter:
        reply_keyboard = [["Gracias!"]]
        update.message.reply_text(text="Bon apetit",
                                  reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True))
        context.bot.send_animation(chat_id=update.message.chat_id,
                                   animation="https://lh4.googleusercontent.com/RB6bkEGvGcpTg_T0apxUSxh0Ui6yyPY2Qtz0c_0AtqDeo5UNFXNtnCzZ0Zr0hucSMsoN1JUZJnH96C2KvXRT=w683-h696",
                                   duration=None,
                                   width=None,
                                   height=None, thumb=None, caption=None,
                                   parse_mode=None, disable_notification=False, reply_to_message_id=None,
                                   reply_markup=None,
                                   timeout=20)
        return RECEPIE_FINISH

    reply_keyboard = [["SI!"]]
    update.message.reply_text(text="¿Lo tienes ya?",
                              reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True))
    return RECEPIE_STEPS


def stepsFinish(update, context):
    update.message.reply_text(RECEPIE_STEPS_FINISH)
    users.get(update.message.chat_id).step_counter = 0
    start(update, context)
    return ACTION
