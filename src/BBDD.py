from pymongo import MongoClient


class MongoDB:
    def __init__(self):
        self.client = MongoClient(port=27017)
        self.db = self.client["ChefBot"]
        self.collection = self.db["CB_User"]
        # self.collection = self.db["CB_Recipies"] TODO: ver como tratar dos colecciones a la vez

    # User querys______________________________
    # Con esta función se puedo conocer el usuario con detalle (estado, teclado, ingredientes, etc)
    def search_user(self, user):
        return self.collection.find_one(
            {"_id": user.token}
        )

    def search_user_by_id(self, token):
        return self.collection.find_one(
            {
                "_id": token
            }
        )

    def new_user(self, user):
        if self.search_user(user) is None:
            self.collection.insert_one(
                {
                    "_id": user.token,
                    "username": user.username,
                    "status": user.status,
                    "current_keyboard": user.current_keyboard
                }
            )

    def update_user_status(self, token, status):
        self.collection.find_one_and_update(
            {"_id": token},
            {"$set": {"status": status}}
        )

    # Pantry Querys_____________________________
    # TODO: comprobar antes si el ingrediente que se quiere añadir existe
    def new_ingredient(self, id, ingredient):
        # TODO: Falta imagen
        self.collection.find_one_and_update(
            {"_id": id},
            {
                "$push":
                    {
                        "ingredients": [
                            {
                                "ingredient_name": ingredient.ingredient,
                                "quantity": ingredient.quantity,
                                "measure": ingredient.unit
                            }
                        ]
                    }
            }
        )

    # fixme: no encuetra nah de nah
    def search_ingredient(self, user, ingredient):
        return self.collection.find_one(
            {"_id": user.token, "ingredient": ingredient.ingredient}
        )

    def update_ingredient(self, user, ingredient):
        self.collection.update(
            {"_id": user.token, "ingredient": ingredient.ingredient
             },
            {
                "$set":
                    {
                        "_id": user.token,  # Codigo id único en mongo db
                        "ingredients": {
                            "ingredient_name": [ingredient.ingredient],
                            "quantity": ingredient.quantity
                        }
                    }
            }
        )

    # ShoppingList Querys_______________________
    def new_ingredient(self, user, ingredient):
        return 0

    def show_shopping_list(self, user, ingredient):
        return 0

    def update_ingredient_shopping_list(self, user, ingredient):
        return 0

    # Recipies API______________________________

    def insert_new_recipie(self, recipie):
        #TODO: hace falta controlar que no repiten las recipies
        self.collection.insert({recipie})
