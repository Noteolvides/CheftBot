from pymongo import MongoClient
import json


class MongoDB:
    def __init__(self):
        self.client = MongoClient(port=27017)
        self.db = self.client["ChefBot"]
        self.collection = self.db["CB_User"]
        # self.collection = self.db["CB_Recipies"]

    # User querys______________________________
    def new_user(self, user):
        self.collection.insert(
            {
                "token": user.token,
                "username": user.username,
                "status": user.status,
                "current_keyboard": user.current_keyboard
            }
        )

    # TODO: Actualizar valores de un usuario
    def update_user(self, user):
        self.collection.update()

    # Con esta función se puedo conocer el usuario con detalle (estado, teclado, etc)
    def search_user(self, user):
        return self.collection.find(
            {
                "_id": user.token
            }
        )

    # Pantry Querys_____________________________
    def new_ingredient(self, user, ingredient):
        # TODO: Falta imagen
        self.collection.update(
            {
                "_id": user.token
            },
            {
                "_id": user.token,  # Codigo id único en mongo db
                "ingredient": [ingredient],
                "quantity": user.status,
            }
        )

    def search_ingredient(self, user, ingredient):
        return self.collection.find(
            {
                "_id": user.token,
                "ingredient": ingredient
            }
        )

    def update_ingredient(self, user, ingredient):
        self.collection.update(
            {
                "_id": user.token,
                "ingredient": ingredient
            }
        )

    # ShoppingList Querys_______________________
