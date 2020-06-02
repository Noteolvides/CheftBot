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

api = sp.API("96597bf47b244aeaa828714933232af4")
min = 0.7


def similar(a, b):
    return SequenceMatcher(None, a, b).ratio()


# Para ir a la opcion general de recetas, ver recetas posibles segun los ingredientes del user
# Siempre disponible porque es una de las opciones importantes
def newRecipies(statement, bot, mongo):
    bot.send_message(statement.id, "Great")
    bot.send_message(statement.id, POSSIBLE_RECIPIES)
    mongo.set_cooking_recipe(statement.id, False)

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
        queue(bot.send_photo, chat_id=statement.id, photo=recipe["image"])
        queue(bot.send_message, chat_id=statement.id, text=recipe["title"], reply_markup=markup)
        mongo.new_choose_recipe(statement.id, recipe)

    queue(bot.send_message, chat_id=statement.id, text="Which one do you want to cook?")
    mongo.update_user_status(statement.id, ESTADO_CHOOSING)


class SeeRecipes(object):
    def __init__(self, **kwargs):
        pass

    @staticmethod
    def can_process(statement, status, mongo):
        return True

    @staticmethod
    def process(statement, status, mongo):
        return similar(statement.text.lower(), "recipe")

    @staticmethod
    def response(statement, bot, mongo):
        cooking = mongo.get_cooking_recipe(statement.id)
        if cooking:
            recipe = mongo.get_actual_recipe(statement.id)
            markup = InlineKeyboardMarkup()
            markup.row_width = 1
            markup.add(InlineKeyboardButton("Resume cooking", callback_data="resume_cooking"))
            markup.add(InlineKeyboardButton("New recipie", callback_data="new_recipies"))
            bot.send_message(statement.id, "Would you like to finish cooking " + recipe["title"] + "?",
                             reply_markup=markup)

        else:
            newRecipies(statement, bot, mongo)


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
        # bot.send_message(statement.id, READY_RECIPE)

        selected_recipe = mongo.get_actual_recipe(statement.id)
        steps = api.get_analyzed_recipe_instructions(selected_recipe["id"], stepBreakdown=True).json()
        mongo.update_actual_steps(statement.id, steps)
        mongo.update_number_step(statement.id, -1)

        if len(steps) == 0:
            bot.send_message(statement.id, emoji.emojize("Sorry this recipe is not available :cry:", use_aliases=True))
            bot.send_message(statement.id, emoji.emojize("One of our chefs has put a banana in the CD player :monkey:",
                                                         use_aliases=True))
            initial_menu(statement.id, bot)
            mongo.update_user_status(statement.id, ESTADO_MENU)
            return None

        # TODO revisar/plantear otra manera de ver los pasos para que no sea tan tocho seguido
        # bot.send_message(statement.id, "Lets take a look to the ingredients")
        bot.send_message(statement.id, INGREDIENTS_RECIPE)
        ingredients = mongo.get_ingredients(statement.id)

        string_ingredients = ""
        for ingredient in selected_recipe["usedIngredients"]:
            string_ingredients += emoji.emojize(":white_check_mark: ", use_aliases=True) + ingredient[
                "originalString"] + "\n"

        missing = False
        for missed_ingredient in selected_recipe["missedIngredients"]:
            found = False
            for ingredient in ingredients:
                if similar(missed_ingredient["name"], ingredient["name"]) > 0.8:
                    string_ingredients += emoji.emojize(":white_check_mark: ", use_aliases=True) + ingredient[
                        "originalName"] + "\n"
                    found = True

                    break
            if not found:
                string_ingredients += emoji.emojize(":negative_squared_cross_mark: ", use_aliases=True) + missed_ingredient["original"] + "\n"
                mongo.add_missing_ingredient(statement.id, missed_ingredient)
                missing = True


        # for ingredient in selected_recipe["missedIngredients"]:
        #     string_ingredients += emoji.emojize(":negative_squared_cross_mark: ", use_aliases=True) + ingredient[
        #         "originalString"] + "\n"
        #     mongo.add_missing_ingredient(statement.id, ingredient)

        if not missing:
            bot.send_message(statement.id, string_ingredients)
        else:
            markup = InlineKeyboardMarkup()
            markup.row_width = 1
            markup.add(
                InlineKeyboardButton("Add missing ingredients to shopping list", callback_data="add_missing_shopping"))
            bot.send_message(statement.id, string_ingredients, reply_markup=markup)

        bot.send_message(statement.id, START_COOKING)
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
            mongo.set_cooking_recipe(statement.id, True)

            paso_actual = mongo.get_number_step(statement.id)
            paso_actual = paso_actual + 1
            steps = mongo.get_actual_steps(statement.id)

            i = 0
            paso_aux = paso_actual
            while i < len(steps):
                if paso_aux > len(steps[i]["steps"]):
                    paso_aux -= len(steps[i]["steps"])
                    i = i + 1
                else:
                    break

            if paso_aux == len(steps[i]["steps"]) - 1:
                bot.send_message(statement.id, "You are almost done!")

            if paso_aux != len(steps[i]["steps"]):
                # gran variedad de nombres la verdad :(
                # TODO Plantearse poner el calculo de step en una func porque se repite mucho

                markup = types.ReplyKeyboardMarkup(one_time_keyboard=True)
                markup.add('prev', 'next')
                bot.send_message(statement.id, str(paso_aux + 1) + ". " + steps[i]["steps"][paso_aux]["step"],
                                 reply_markup=markup)

            else:
                bot.send_message(statement.id,
                                 emoji.emojize("Congratulations you have finished the recipe :clap:", use_aliases=True))
                # todo sad porque no he encontrado chef https://www.webfx.com/tools/emoji-cheat-sheet/
                bot.send_message(statement.id, emoji.emojize("Bon apettite :ok_hand:", use_aliases=True))
                bot.send_animation(statement.id,
                                   "https://tenor.com/view/delicious-gif-7851132")
                bot.send_message(statement.id, RATE_MEAL)

                mongo.update_user_status(statement.id, ESTADO_RATING)
                mongo.delete_choose_recipes(statement.id)
                recipe = mongo.get_actual_recipe(statement.id)

                user_ingredients = mongo.get_ingredients(statement.id)

                for recipe_ingredient in recipe["usedIngredients"]:
                    for user_ingredient in user_ingredients:
                        if similar(user_ingredient["name"], recipe_ingredient["name"]) > 0.6:
                            if user_ingredient["unit"] == recipe_ingredient["unit"] \
                                    and user_ingredient["amount"] > recipe_ingredient["amount"]:
                                user_ingredient["amount"] -= recipe_ingredient["amount"]
                                print(mongo.use_ingredient(statement.id, user_ingredient))
                            else:
                                print(mongo.delete_ingredient_by_name(statement.id, recipe_ingredient["name"]))

                            break
                            # user_ingredients.remove(user_ingredient)

                mongo.set_cooking_recipe(statement.id, False)

            mongo.update_number_step(statement.id, paso_actual)

        else:
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
            bot.send_message(statement.id, str(paso_aux + 1) + ". " + steps[i]["steps"][paso_aux]["step"],
                             reply_markup=markup)
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
            bot.send_message(statement.id, str(paso_aux + 1) + ". " + steps[i]["steps"][paso_aux]["step"],
                             reply_markup=markup)


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

        message = ""
        if opcion == see_steps:
            cnt = 1
            bot.send_message(statement.id, ALL_STEPS)
            for process in steps:
                for step in process["steps"]:
                    message += str(cnt) + ". " + step["step"] + "\n"
                    cnt += 1

        if opcion == see_cookware:
            bot.send_message(statement.id, ALL_COOKWARE)
            for process in steps:
                for step in process["steps"]:
                    for equipment in step["equipment"]:
                        message += equipment["name"] + "\n"

        if opcion == see_ingredients:
            selected_recipe = mongo.get_actual_recipe(statement.id)
            for ingredient in selected_recipe["usedIngredients"]:
                message += emoji.emojize(":white_check_mark: ", use_aliases=True) + ingredient[
                    "originalString"] + "\n"

            for ingredient in selected_recipe["missedIngredients"]:
                message += emoji.emojize(":negative_squared_cross_mark: ", use_aliases=True) + ingredient[
                    "originalString"] + "\n"

        bot.send_message(statement.id, message)
        # Para recetas con varios procesos
        i = 0
        paso_aux = paso_actual
        while i < len(steps):
            if paso_aux >= len(steps[i]["steps"]):
                paso_aux -= len(steps[i]["steps"])
                i += 1
            else:
                break
        bot.send_message(statement.id,
                         "Your currently step is:\n" + str(paso_aux + 1) + ". " + steps[i]["steps"][paso_aux]["step"])


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
        initial_menu(statement.id, bot, mongo)

        # TODO restar cantidadaes de los ingredientes
        mongo.update_user_status(statement.id, ESTADO_MENU)
