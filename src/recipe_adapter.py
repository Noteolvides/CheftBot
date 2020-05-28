import emoji
import spoonacular as sp

from chatterbot.conversation import Statement
from chatterbot.comparisons import JaccardSimilarity
from chatterbot.logic import LogicAdapter
from telebot import types
from telebot.types import InlineKeyboardMarkup
from telegram.ext import MessageQueue as mq

from src.message_queue import QueueGestor, DELAY_TYPE_TEXT, DELAY_TYPE_PHOTO

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


# Para ir a la opcion general de recetas, ver recetas posibles segun los ingredientes del user
# Siempre disponible porque es una de las opciones importantes
class SeeRecipes(object):
	def __init__(self, **kwargs):
		pass

	@staticmethod
	def can_process(statement, status, mongo):
		lower_string = statement.text
		if "recipe" in lower_string.lower():  # Aux.state == ESTADO_MENU:
			return True
		return False

	@staticmethod
	def process(statement, status, mongo):
		return JaccardSimilarity().compare(Statement(statement.text), Statement("recipe"))

	@staticmethod
	def response(statement, bot, mongo):
		bot.send_message(statement.id, "Great")
		bot.send_message(statement.id, POSSIBLE_RECIPIES)

		# TODO get INGREDIENTES de la BBDD para pasarle a la api
		Aux.recipes = api.search_recipes_by_ingredients("spaghetti, cheese, egg", fillIngredients=True, number=3,
														ranking=1).json()
		# TODO guardar RECETAS POSIBLE de la api en BBDD
		# queue = MessageQueue()
		queue = QueueGestor(bot)
		for recipe in Aux.recipes:
			queue.add_message(statement.id, recipe["title"], DELAY_TYPE_TEXT)
			queue.add_message(statement.id, recipe["image"], DELAY_TYPE_PHOTO)

		# queue.startQueue()
		# bot.send_message(statement.id, recipe["title"])
		# bot.send_photo(statement.id, recipe["image"])

		# bot.send_message(statement.id, NONE_RECIPE)
		# bot.send_message(statement.id, MORE_RECIPE)

		wait = input("waiting:")

		bot.send_message(statement.id, "Wich one do you like?")
		# TODO set status en bbdd
		Aux.state = ESTADO_CHOOSING


# Escoger receta de las que ha devuelto la api
# Solo isponible si estas en el estado de escoger, ya has pasado por el general de recetas
class ChooseRecipe(object):
	def __init__(self, **kwargs):
		pass

	@staticmethod
	def can_process(statement, status, mongo):
		if Aux.state == ESTADO_CHOOSING or status == ESTADO_CHOOSING:
			return True
		return False

	@staticmethod
	def process(statement, status, mongo):
		max = -1
		# if JaccardSimilarity().compare(Statement(statement.text), Statement(MORE_RECIPE)) > min:
		#    return 1

		# TODO get RECETAS POSIBLES del mongo
		# recipes = api.search_recipes_by_ingredients("spaghetti, cheese, egg", fillIngredients=True, number=3, ranking=1).json()
		for recipe in Aux.recipes:
			actual = JaccardSimilarity().compare(Statement(statement.text), Statement(recipe["title"]))
			if actual > max:
				max = actual
				selected_recipe = recipe

		# TODO guardar la SELECTED RECIPE en la BBDD
		return max

	@staticmethod
	def response(statement, bot, mongo):
		bot.send_message(statement.id, EXCELENT_CHOICE)
		bot.send_message(statement.id, READY_RECIPE)
		bot.send_message(statement.id, COOKWARE_RECIPE)

		# TODO get RECETA ACTUAL para tener el id
		Aux.steps = api.get_analyzed_recipe_instructions(1115141, stepBreakdown=False).json()
		# TODO guardar STEPS enla BBDD y el progresp, el step actual (el 0)

		# TODO revisar/plantear otra manera de ver los pasos para que no sea tan tocho seguido
		for process in Aux.steps:
			for step in process["steps"]:
				for equipment in step["equipment"]:
					bot.send_message(statement.id, equipment["name"])

		bot.send_message(statement.id, "Lets take a look to the ingredients")
		bot.send_message(statement.id, INGREDIENTS_RECIPE)

		for process in Aux.steps:
			for step in process["steps"]:
				for ingredient in step["ingredients"]:
					bot.send_message(statement.id, ingredient["name"])

		# Todo ¿Se puede poner negrita en los mensajes, para dar enfasis a la palabra exacta que tiene que escribir?
		bot.send_message(statement.id, START_COOKING)
		Aux.state = ESTADO_COOKING


# Para cuando se esta cocinando una receta
# Solo se puede acceder si estas en el status de cocinando, ya esta bien para que no se confuda con otras cosas que
# usen next
class CookingRecipe(object):
	def __init__(self, **kwargs):
		pass

	@staticmethod
	def can_process(statement, status, mongo):
		if Aux.state == ESTADO_COOKING or status == ESTADO_COOKING:
			return True
		return False

	@staticmethod
	def process(statement, status, mongo):
		lower_string = statement.text.lower()
		if lower_string in "next step":
			return JaccardSimilarity().compare(Statement(statement.text), Statement("next step"))
		if lower_string in "start cooking":
			return JaccardSimilarity().compare(Statement(statement.text), Statement("start cooking"))
		return -1

	@staticmethod
	def response(statement, bot, mongo):

		if Aux.paso_actual == len(Aux.steps[0]["steps"]) - 1:
			bot.send_message(statement.id, "You are almost done!")

		if Aux.paso_actual != len(Aux.steps[0]["steps"]):
			# gran variedad de nombres la verdad :(
			i = 0
			paso_aux = Aux.paso_actual
			while i < len(Aux.steps):
				if Aux.paso_actual >= len(Aux.steps[i]):
					paso_aux -= len(Aux.steps[i])
				else:
					break
			markup = types.ReplyKeyboardMarkup(one_time_keyboard=True)
			markup.add('prev', 'next')
			bot.send_message(statement.id, Aux.steps[i]["steps"][paso_aux]["step"], reply_markup=markup)

		# bot.send_message(statement.id, Aux.steps[0]["steps"][Aux.paso_actual]["step"])
		else:
			bot.send_message(statement.id, emoji.emojize("Congratulations you have finished the recipe :clap:", use_aliases=True))
			# todo sad porque no he encontrado chef https://www.webfx.com/tools/emoji-cheat-sheet/
			bot.send_message(statement.id, emoji.emojize("Bon apettite :ok_hand:", use_aliases=True))
			bot.send_message(statement.id, RATE_MEAL)
			# Todo usar BBDD para el status, ya se ha acabado de cocinar receta
			Aux.state = ESTADO_RATING

		# Todo usar BBDD para los pasos
		Aux.paso_actual = Aux.paso_actual + 1


# Para poder tirar hacia atras en un paso de receta
# Solo cuando se esta cocinando asi no coincidira con otras cosas
# TODO pensar que mas funcionaclidades de navegacion pueden venir bien
class NavigationReciepe(object):
	def __init__(self, **kwargs):
		pass

	@staticmethod
	def can_process(statement, status, mongo):
		if Aux.state == ESTADO_COOKING or status == ESTADO_COOKING:
			return True
		return False

	@staticmethod
	def process(statement, status, mongo):
		value1 = JaccardSimilarity().compare(Statement(statement.text), Statement("previous step"))
		value2 = JaccardSimilarity().compare(Statement(statement.text), Statement("prev"))
		return max(value1, value2)

	@staticmethod
	def response(statement, bot, mongo):

		if Aux.paso_actual > 0:
			# Todo usar BBDD para get pasos, y get y set estado
			Aux.paso_actual = Aux.paso_actual - 1
			bot.send_message(statement.id, "This was the previous step")
			bot.send_message(statement.id, Aux.steps[0]["steps"][Aux.paso_actual]["step"])


# TODO plantearse si separar en 3 casos distintos
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
		if Aux.state == ESTADO_COOKING or status == ESTADO_COOKING:
			return True

		return False

	@staticmethod
	def process(statement, status, mongo):
		see_steps = JaccardSimilarity().compare(Statement(statement.text), Statement("see steps"))
		see_cookware = JaccardSimilarity().compare(Statement(statement.text), Statement("see cookware"))
		see_ingredients = JaccardSimilarity().compare(Statement(statement.text), Statement("see ingredients"))
		return max(see_steps, see_cookware, see_ingredients)

	@staticmethod
	def response(statement, bot, mongo):
		see_steps = JaccardSimilarity().compare(Statement(statement.text), Statement("see steps"))
		see_cookware = JaccardSimilarity().compare(Statement(statement.text), Statement("see cookware"))
		see_ingredients = JaccardSimilarity().compare(Statement(statement.text), Statement("see ingredients"))
		opcion = max(see_steps, see_cookware, see_ingredients)

		# TODO pillar los analyzed_steps de la BBDD
		if opcion == see_steps:
			bot.send_message(statement.id, ALL_STEPS)
			for process in Aux.steps:
				for step in process["steps"]:
					bot.send_message(statement.id, step["step"])

		if opcion == see_cookware:
			bot.send_message(statement.id, ALL_COOKWARE)
			for process in Aux.steps:
				for step in process["steps"]:
					for equipment in step["equipment"]:
						bot.send_message(statement.id, equipment["name"])

		if opcion == see_ingredients:
			bot.send_message(statement.id, ALL_INGREDIENTS)
			for process in Aux.steps:
				for step in process["steps"]:
					for ingredient in step["ingredients"]:
						bot.send_message(statement.id, ingredient["name"])

		bot.send_message(statement.id, "Your currently step is:")
		# Para recetas con varios procesos
		i = 0
		paso_aux = Aux.paso_actual
		while i < len(Aux.steps):
			if Aux.paso_actual >= len(Aux.steps[i]):
				paso_aux -= len(Aux.steps[i])
			else:
				break
		bot.send_message(statement.id, Aux.steps[i]["steps"][paso_aux]["step"])


# Para pedir al user que nos puntue la receta que acaba de preparar
class MealRating(object):
	def __init__(self, **kwargs):
		pass

	@staticmethod
	def can_process(statement, status, mongo):
		return Aux.state == RATE_MEAL or status == RATE_MEAL

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
		# TODO actualizar status en BBDD
		# TODO llamar a funcion de inicio
		Aux.state = ESTADO_MENU
