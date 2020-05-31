import json
from difflib import SequenceMatcher

import emoji
import spoonacular as sp

from telebot import types
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton

from src.test import EsperaQueue
from src.general_adapter import initial_menu

ESTADO_MENU = 0
ESTADO_RECETAS = 1
ESTADO_CHOOSING = 12
ESTADO_COOKING = 13
ESTADO_RATING = 14

POSSIBLE_RECIPIES = "These are the recipies that you can cook with the ingredients that you have"
NONE_RECIPE = "None of the above"
MORE_RECIPE = "See more recipes"
EXCELENT_CHOICE = "Excellent choice"
READY_RECIPE = "Let's prepare what we will need :)"
COOKWARE_RECIPE = "For this recipie you will need the following items:"
INGREDIENTS_RECIPE = "For this recipie you will need the following ingredients:"
START_COOKING = "Tell me when you are ready to start cooking"
ALL_STEPS = "Here are all the steps of your current recipe"
ALL_COOKWARE = "Here are all te utensils/cookware you will need for your current recipe"
ALL_INGREDIENTS = "Here are all the ingredients you will need for your current recipe"
RATE_MEAL = "How would you rate this meal?"

NUMBER_RECIPES = 3

api = sp.API("bba58a1c79234e139e3785c6fbceb313")
min = 0.7


def similar(a, b):
    return SequenceMatcher(None, a, b).ratio()


class Aux(object):
    state = ESTADO_MENU
    recipes = None
    steps = None
    paso_actual = -1


# Para ir a la opcion general de recetas, ver recetas posibles segun los ingredientes del user
# Siempre disponible porque es una de las opciones importantes
class SeeRecipes(object):
    def __init__(self, **kwargs):
        pass

    @staticmethod
    def can_process(statement, status, mongo):
        # lower_string = statement.text
        # if "recipe" in lower_string.lower():  # Aux.state == ESTADO_MENU:
        #     return True
        return True

    @staticmethod
    def process(statement, status, mongo):
        return similar(statement.text.lower(), "recipe")

    @staticmethod
    def response(statement, bot, mongo):
        bot.send_message(statement.id, "Great")
        bot.send_message(statement.id, POSSIBLE_RECIPIES)

        # TODO borrar el choose que hubiera antes

        ingredients_string = ""
        ingredients = mongo.get_ingredients(statement.id)
        for ingredient in ingredients:
            ingredients_string += ingredient["name"]
            ingredients_string += ","

        a = ingredients_string[:-1]
        recipes = api.search_recipes_by_ingredients(ingredients_string[:-1], fillIngredients=True,
                                                    number=NUMBER_RECIPES,
                                                    ranking=2).json()

        queue = EsperaQueue(burst_limit=1, time_limit_ms=100)
        markup = InlineKeyboardMarkup()
        markup.row_width = 1
        markup.add(InlineKeyboardButton("Cook this recipie", callback_data="cook"))
        for recipe in recipes:
            queue(bot.send_message, chat_id=statement.id, text=recipe["title"], reply_markup=markup)
            queue(bot.send_photo, chat_id=statement.id, photo=recipe["image"])
            mongo.new_choose_recipe(statement.id, recipe)

        # bot.send_message(statement.id, NONE_RECIPE)
        # bot.send_message(statement.id, MORE_RECIPE)

        queue(bot.send_message, chat_id=statement.id, text="Which one do you like?")
        # bot.send_message(statement.id, "Wich one do you like?")
        # queue.add_message(statement.id, "Wich one do you like?", DELAY_TYPE_TEXT)

        Aux.state = ESTADO_CHOOSING
        mongo.update_user_status(statement.id, ESTADO_CHOOSING)


# Escoger receta de las que ha devuelto la api
# Solo isponible si estas en el estado de escoger, ya has pasado por el general de recetas
class ChooseRecipe(object):
    def __init__(self, **kwargs):
        pass

    @staticmethod
    def can_process(statement, status, mongo):
        if status == ESTADO_CHOOSING:
            return True
        return False

    @staticmethod
    def process(statement, status, mongo):
        max = -1

        recipes = mongo.get_choose_recipes(statement.id)
        for recipe in recipes:
            actual = similar(statement.text.lower(), recipe["title"].lower())
            if actual > max:
                max = actual
                selected_recipe = recipe

        mongo.update_actual_recipe(statement.id, selected_recipe)
        return max

    @staticmethod
    def response(statement, bot, mongo):
        bot.send_message(statement.id, EXCELENT_CHOICE)
        bot.send_message(statement.id, READY_RECIPE)
        bot.send_message(statement.id, COOKWARE_RECIPE)

        selected_recipe = mongo.get_actual_recipe(statement.id)
        steps = api.get_analyzed_recipe_instructions(selected_recipe["id"], stepBreakdown=True).json()
        mongo.update_actual_steps(statement.id, steps)
        mongo.update_number_step(statement.id, -1)

        # TODO revisar/plantear otra manera de ver los pasos para que no sea tan tocho seguido
        for process in steps:
            for step in process["steps"]:
                for equipment in step["equipment"]:
                    bot.send_message(statement.id, equipment["name"])

        bot.send_message(statement.id, "Lets take a look to the ingredients")
        bot.send_message(statement.id, INGREDIENTS_RECIPE)

        for process in steps:
            for step in process["steps"]:
                for ingredient in step["ingredients"]:
                    bot.send_message(statement.id, ingredient["name"])

        # Todo ¿Se puede poner negrita en los mensajes, para dar enfasis a la palabra exacta que tiene que escribir?
        bot.send_message(statement.id, START_COOKING)
        Aux.state = ESTADO_COOKING
        mongo.update_user_status(statement.id, ESTADO_COOKING)


# Para cuando se esta cocinando una receta
# Solo se puede acceder si estas en el status de cocinando, ya esta bien para que no se confuda con otras cosas que
# usen next
class CookingRecipe(object):
    def __init__(self, **kwargs):
        pass

    @staticmethod
    def can_process(statement, status, mongo):
        if status == ESTADO_COOKING:
            return True
        return False

    @staticmethod
    def process(statement, status, mongo):
        lower_string = statement.text.lower()
        v1 = similar(statement.text, "next step")
        v2 = similar(statement.text, "next")
        v3 = similar(statement.text, "start cooking")
        v4 = similar(statement.text, "ready")
        v5 = similar(statement.text, "yes")
        v6 = similar(statement.text, "no")
        return max(v1, v2, v3, v4, v5)

    @staticmethod
    def response(statement, bot, mongo):
        if similar(statement.text.lower(), "no") < 0.7:
            paso_actual = mongo.get_number_step(statement.id)
            paso_actual = paso_actual + 1
            steps = mongo.get_actual_steps(statement.id)

            if paso_actual == len(steps[0]["steps"]) - 1:
                bot.send_message(statement.id, "You are almost done!")

            if paso_actual != len(steps[0]["steps"]):
                # gran variedad de nombres la verdad :(
                # TODO Plantearse poner el calculo de step en una func porque se repite mucho
                i = 0
                paso_aux = paso_actual
                while i < len(steps):
                    if paso_aux >= len(steps[i]["steps"]):
                        paso_aux -= len(steps[i]["steps"])
                        i = i + 1
                    else:
                        break
                markup = types.ReplyKeyboardMarkup(one_time_keyboard=True)
                markup.add('prev', 'next')
                bot.send_message(statement.id, steps[i]["steps"][paso_aux]["step"], reply_markup=markup)

            else:
                bot.send_message(statement.id,
                                 emoji.emojize("Congratulations you have finished the recipe :clap:", use_aliases=True))
                # todo sad porque no he encontrado chef https://www.webfx.com/tools/emoji-cheat-sheet/
                bot.send_message(statement.id, emoji.emojize("Bon apettite :ok_hand:", use_aliases=True))
                bot.send_message(statement.id, RATE_MEAL)

                Aux.state = ESTADO_RATING
                mongo.update_user_status(statement.id, ESTADO_RATING)
                mongo.delete_choose_recipes(statement.id)
                recipe = mongo.get_actual_recipe(statement.id)

                for recipe_ingredient in recipe["usedIngredients"]:
                    # todo, parece que no me encuentra el ingrediente :(
                    user_ingredient = mongo.get_ingredient_by_name(statement.id, recipe_ingredient["name"])
                    if user_ingredient is not None and user_ingredient["unit"] == recipe_ingredient["unit"] \
                            and user_ingredient["amount"] > recipe_ingredient["amount"]:
                        user_ingredient["amount"] -= recipe_ingredient["amount"]
                        mongo.update_ingredient(statement.id, user_ingredient)
                    else:
                        mongo.delete_ingredient_by_name(statement.id, recipe_ingredient["name"])

            mongo.update_number_step(statement.id, paso_actual)
        else:
            Aux.state = ESTADO_MENU
            mongo.update_user_status(statement.id, ESTADO_MENU)

            bot.send_message(statement.id, "You stopped cooking the recipe")
            initial_menu(statement.id, bot)


# Para poder tirar hacia atras en un paso de receta
# Solo cuando se esta cocinando asi no coincidira con otras cosas
# TODO pensar que mas funcionaclidades de navegacion pueden venir bien
class NavigationReciepe(object):
    def __init__(self, **kwargs):
        pass

    @staticmethod
    def can_process(statement, status, mongo):
        if status == ESTADO_COOKING:
            return True
        return False

    @staticmethod
    def process(statement, status, mongo):
        value1 = similar(statement.text.lower(), "previous step")
        value2 = similar(statement.text.lower(), "prev")
        return max(value1, value2)

    @staticmethod
    def response(statement, bot, mongo):
        paso_actual = mongo.get_number_step(statement.id)
        steps = mongo.get_actual_steps(statement.id)

        if paso_actual > 0:
            paso_actual = paso_actual - 1
            i = 0
            paso_aux = paso_actual
            while i < len(steps):
                if paso_aux >= len(steps[i]["steps"]):
                    paso_aux -= len(steps[i]["steps"])
                    i = i + 1
                else:
                    break
            markup = types.ReplyKeyboardMarkup(one_time_keyboard=True)
            markup.add('prev', 'next')
            bot.send_message(statement.id, "This was the previous step")
            bot.send_message(statement.id, steps[i]["steps"][paso_aux]["step"], reply_markup=markup)
            mongo.update_number_step(statement.id, paso_actual)

        else:
            i = 0
            paso_aux = paso_actual
            while i < len(steps):
                if paso_aux >= len(steps[i]["steps"]):
                    paso_aux -= len(steps[i]["steps"])
                    i = i + 1
                else:
                    break
            markup = types.ReplyKeyboardMarkup(one_time_keyboard=True)
            markup.add('prev', 'next')
            bot.send_message(statement.id, "You are in the first step")
            bot.send_message(statement.id, steps[i]["steps"][paso_aux]["step"], reply_markup=markup)


# Get todos los datos de la receta que se esta preparando, solo si se esta cocinando:
# ver steps
# ver utensilios
# ver ingredientes
# TODO ver como formatear bonito toda esta info
class MoreInfoRecipe(object):
    def __init__(self, **kwargs):
        pass

    @staticmethod
    def can_process(statement, status, mongo):
        return status == ESTADO_COOKING

    @staticmethod
    def process(statement, status, mongo):
        see_steps = similar(statement.text.lower(), "see steps")
        see_cookware = similar(statement.text.lower(), "see cookware")
        see_ingredients = similar(statement.text.lower(), "see ingredients")
        return max(see_steps, see_cookware, see_ingredients)

    @staticmethod
    def response(statement, bot, mongo):
        see_steps = similar(statement.text.lower(), "see steps")
        see_cookware = similar(statement.text.lower(), "see cookware")
        see_ingredients = similar(statement.text.lower(), "see ingredients")
        opcion = max(see_steps, see_cookware, see_ingredients)

        steps = mongo.get_actual_steps(statement.id)
        paso_actual = mongo.get_number_step(statement.id)

        if opcion == see_steps:
            bot.send_message(statement.id, ALL_STEPS)
            for process in steps:
                for step in process["steps"]:
                    bot.send_message(statement.id, step["step"])

        if opcion == see_cookware:
            bot.send_message(statement.id, ALL_COOKWARE)
            for process in steps:
                for step in process["steps"]:
                    for equipment in step["equipment"]:
                        bot.send_message(statement.id, equipment["name"])

        if opcion == see_ingredients:
            bot.send_message(statement.id, ALL_INGREDIENTS)
            for process in steps:
                for step in process["steps"]:
                    for ingredient in step["ingredients"]:
                        bot.send_message(statement.id, ingredient["name"])

        bot.send_message(statement.id, "Your currently step is:")
        # Para recetas con varios procesos
        i = 0
        paso_aux = paso_actual
        while i < len(steps):
            if paso_aux >= len(steps[i]["steps"]):
                paso_aux -= len(steps[i]["steps"])
                i += 1
            else:
                break
        bot.send_message(statement.id, Aux.steps[i]["steps"][paso_aux]["step"])


# Para pedir al user que nos puntue la receta que acaba de preparar
class MealRating(object):
    def __init__(self, **kwargs):
        pass

    @staticmethod
    def can_process(statement, status, mongo):
        return status == ESTADO_RATING

    @staticmethod
    def process(statement, status, mongo):
        lower_string = statement.text
        if lower_string.isnumeric():
            return 1
        return -1

    @staticmethod
    def response(statement, bot, mongo):
        bot.send_message(statement.id, "Thanks for your review, I'll keep it in my HDD for your next meals! :)")
        # TODO (OPCIONAL) guardar valoraciones de receta para recomendaciones
        initial_menu(statement.id, bot)

        # TODO restar cantidadaes de los ingredientes
        Aux.state = ESTADO_MENU
        mongo.update_user_status(statement.id, ESTADO_MENU)
