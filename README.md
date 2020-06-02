# ChefBot
Chefbot ideal para ayudarte en las tareas de la cocina y en la organización.
El token que esta, es un token vinculado a el siguiente chatbot en telegram @Noteolvidesbot
Si quieres resetear el Bot comand /start @NoteolvidesBot

Animo cocinando
### Authors
* Gerard Melgares
* Gustavo Gómez López De San Román
* Albert Colinas

### Configuration
Language: python 

Version: python3 

Project program: pyCharm

#### Libraries:
* telebot
* emoji
* re
* json
* pymongo
* clarifai
* difflib
* spoonacular
* logging
* telegram
* itertools
* random
* bisect
* unicodedata
### Running the program
####Menu
```
1. Shopping list: enter shopping list menu
2. Ingredients: enter ingredients menu
3. Recipes: enter recipes menu
```
####Shopping list
```
1. Add item: add item to your shopping list 
2. Delete item: delete item from shopping list
3. Mark Purcharsed: purcharsed from the list and add it to your available ingredient
4. Delete item list: delete all items of your shopping list
```
####Ingredients
```
1. Add ingredient: add a new ingredient to your list manually or sending a photo to identify it automatically
2. List ingredients: you can see all ingredients you have and delete them
```
####Recipes
```
1. Cook new recipe: Chefbot will suggest you some recipes with your ingredients
2. Resume previous recipe (if you didn't finish yout last recipe): you will jump to cooking the previous recipe you had
```
#####Recipe suggestion
```
1. Type or push the button of teh recipe: you will select the recipe to cook
2. after 1, you can add the missing ingredients to your shopping list or start cooking
```
#####Cooking recipe
```
1. Type next or prev (or use the buttons) to navigate in the steps of the recipe 
2. See all information of the recipe with see steps/ingredients/cookware
3. In this moment you can also use the rest of the functionalities of Chefbot, your current step will be waiting for you
4. When you finish the ingredients will be removed from yout list
5. Remenber to Rate the recipe and bon apettite :)
```

