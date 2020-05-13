import spoonacular as sp

from chatterbot.conversation import Statement
from chatterbot.comparisons import JaccardSimilarity
from chatterbot.logic import LogicAdapter
from telebot.types import InlineKeyboardMarkup
from telegram import InlineKeyboardButton

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

api = sp.API("aa9cc6861144497a9ce2ab7ffa864984")
min = 0.7


class Aux(object):
    state = ESTADO_MENU
    recipes = None
    steps = None
    paso_actual = 0


class SeeRecipes(object):
    def __init__(self, **kwargs):
        pass

    @staticmethod
    def can_process(statement, status):
        lower_string = statement.text
        if Aux.state == ESTADO_MENU:  # and "recipe" in lower_string.lower():
            return True
        return False

    @staticmethod
    def process(statement, status):
        return JaccardSimilarity().compare(Statement(statement.text), Statement("recipe"))

    @staticmethod
    def response(statement, bot, mongo):
        bot.send_message(statement.id, "Great")
        bot.send_message(statement.id, POSSIBLE_RECIPIES)

        # TODO pedir INGREDIENTES de la BBDD para pasarle a la api
        Aux.recipes = api.search_recipes_by_ingredients("spaghetti, cheese, egg", fillIngredients=True, number=3,
                                                    ranking=1).json()
        # list1 = recipes[:len(recipes)//2]
        # list2 = recipes[:len(recipes)//2]

        for recipe in Aux.recipes:
            bot.send_message(statement.id, recipe["title"])

        # bot.send_message(statement.id, NONE_RECIPE)
        # bot.send_message(statement.id, MORE_RECIPE)
        bot.send_message(statement.id, "Wich one do you like?")

        # TODO cambio de estado en bbdd
        Aux.state = ESTADO_CHOOSING


class ChooseRecipe(object):
    def __init__(self, **kwargs):
        pass

    @staticmethod
    def can_process(statement, status):
        # TODO RECETAS de la BBDD
        if Aux.state == ESTADO_CHOOSING:
            # recipes = api.search_recipes_by_ingredients("spaghetti, cheese, egg", fillIngredients=True, number=3, ranking=1).json()
            # if "none" in statement.text.lower:
            #    return 1

            for recipe in Aux.recipes:
                if statement.text.lower() in recipe["title"].lower():
                    return True

        return False

    @staticmethod
    def process(statement, status):
        max = -1
        # if JaccardSimilarity().compare(Statement(statement.text), Statement(MORE_RECIPE)) > min:
        #    return 1

        # TODO recipes vendra de la BBDD
        # recipes = api.search_recipes_by_ingredients("spaghetti, cheese, egg", fillIngredients=True, number=3, ranking=1).json()
        for recipe in Aux.recipes:
            actual = JaccardSimilarity().compare(Statement(statement.text), Statement(recipe["title"]))
            if actual > max:
                max = actual
                selected_recipe = recipe

        # TODO meter la selected recipe en la BBDD y pasar al estado cooking
        return max

    @staticmethod
    def response(statement, bot, mongo):
        if "none" not in statement.text.lower():
            bot.send_message(statement.id, EXCELENT_CHOICE)
            bot.send_message(statement.id, READY_RECIPE)
            bot.send_message(statement.id, COOKWARE_RECIPE)

            Aux.steps = api.get_analyzed_recipe_instructions(1115141, stepBreakdown=False).json()
            # TODO guardar STEPS enla BBDD y el progresp, el step actual (el 0)

            # list1 = recipes[:len(recipes)//2]
            # list2 = recipes[:len(recipes)//2]
            # TODO comprobar que la estructura del json de los steps es la correcta --> el steps[0] puede ser de varios!!
            for step in Aux.steps[0]["steps"]:
                for equipment in step["equipment"]:
                    bot.send_message(statement.id, equipment["name"])

            bot.send_message(statement.id, "Lets take a look to the ingredients")
            bot.send_message(statement.id, INGREDIENTS_RECIPE)
            for step in Aux.steps[0]["steps"]:
                for ingredient in step["ingredients"]:
                    bot.send_message(statement.id, ingredient["name"])

            # Todo ¿Se puede poner negrita en los mensajes, para dar enfasis a la palabra exacta que tiene que escribir la persona?
            bot.send_message(statement.id, START_COOKING)


class CookingRecipe(object):
    def __init__(self, **kwargs):
        pass

    @staticmethod
    def can_process(statement, status):
        lower_string = statement.text
        # TODO cambiar estado a Viendo recetas
        if "start cooking" in lower_string.lower():
            return True
        if "next step" in lower_string.lower():
            return True
        return False

    @staticmethod
    def process(statement, status):
        lower_string = statement.text
        if "next step" in lower_string.lower():
            return JaccardSimilarity().compare(Statement(statement.text), Statement("next step"))
        if "start cooking" in lower_string.lower():
            return JaccardSimilarity().compare(Statement(statement.text), Statement("start cooking"))
        return -1

    @staticmethod
    def response(statement, bot, mongo):

        if Aux.paso_actual == len(Aux.steps[0]["steps"]) - 1:
            bot.send_message(statement.id, "You are almost done!")

        if Aux.paso_actual != len(Aux.steps[0]["steps"]):
            # gran variedad de nombres la verdad :(
            bot.send_message(statement.id, Aux.steps[0]["steps"][Aux.paso_actual]["step"])
        else:
            bot.send_message(statement.id, "Congratulations you have finished the recipe (icono de celebracion)")
            bot.send_message(statement.id, "Bon apettite (icono de chef)")
            bot.send_message(statement.id, RATE_MEAL)
            Aux.state = ESTADO_RATING

        # Todo usar BBDD para los pasos
        Aux.paso_actual = Aux.paso_actual + 1


class NavigationReciepe(object):
    def __init__(self, **kwargs):
        pass

    @staticmethod
    def can_process(statement, status):
        if Aux.state == ESTADO_COOKING:
            return True
        return False

    @staticmethod
    def process(statement, status):
        return JaccardSimilarity().compare(Statement(statement.text), Statement("previous step"))

    @staticmethod
    def response(statement, bot, mongo):
        Aux.paso_actual = Aux.paso_actual - 1

        if Aux.paso_actual > 0:
            bot.send_message(statement.id, "This was the previous step")
            bot.send_message(statement.id, Aux.steps[0]["steps"][Aux.paso_actual]["step"])
        # Todo usar BBDD para los pasos


class MoreInfoRecipe(object):
    def __init__(self, **kwargs):
        pass

    @staticmethod
    def can_process(statement, status):
        if "see steps" in statement.text.lower():
            return True
        if "see cookware" in statement.text.lower():
            return True
        if "see ingredients" in statement.text.lower():
            return True

        return False

    @staticmethod
    def process(statement, status):
        if "see steps" in statement.text.lower():
            return JaccardSimilarity().compare(Statement(statement.text), Statement("see steps"))

        if "see cookware" in statement.text.lower():
            return JaccardSimilarity().compare(Statement(statement.text), Statement("see cookware"))

        if "see ingredients" in statement.text.lower():
            return JaccardSimilarity().compare(Statement(statement.text), Statement("see ingredients"))

    @staticmethod
    def response(statement, bot, mongo):
        if "see steps" in statement.text.lower():
            bot.send_message(statement.id, ALL_STEPS)
            for step in Aux.steps[0]["steps"]:
                bot.send_message(statement.id, step["step"])

        if "see cookware" in statement.text.lower():
            bot.send_message(statement.id, ALL_COOKWARE)
            for step in Aux.steps[0]["steps"]:
                for equipment in step["equipment"]:
                    bot.send_message(statement.id, equipment["name"])

        if "see ingredients" in statement.text.lower():
            bot.send_message(statement.id, ALL_INGREDIENTS)
            for step in Aux.steps[0]["steps"]:
                for ingredient in step["ingredients"]:
                    bot.send_message(statement.id, ingredient["name"])

        bot.send_message(statement.id, "Your currently step is:")
        bot.send_message(statement.id, Aux.steps[0]["steps"][0]["step"])


class MealRating(object):
    def __init__(self, **kwargs):
        pass

    @staticmethod
    def can_process(statement, status):
        lower_string = statement.text
        # TODO Controlar que estemos en modo de rating
        return lower_string.isnumeric()

    @staticmethod
    def process(statement, status):
        lower_string = statement.text
        if lower_string.isnumeric():
            return 1
        return -1

    @staticmethod
    def response(statement, bot, mongo):
        bot.send_message(statement.id, "Thanks for your review, I'll keep it in my HDD for your next meals! :)")
        # todo, se puede llamar a la del main ¿?
        Aux.state = ESTADO_MENU
