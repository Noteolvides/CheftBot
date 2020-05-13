from pymongo import MongoClient
import json


class MongoDB(object):
    def __init__(self):
        self.client = MongoClient(port=27017)
        self.db = self.client["db_scraping"]
        self.collection = self.db["sources"]

    # User querys______________________________
    def newUser(self, user):
        self.collection.insert_one(
            {
                "_id": user.token,  # Codigo id único en mongo db
                "username": user.username,
                "status": user.status,
                "current_keyboard": user.current_keyboard
            }
        )

    #TODO: Actualizar valores de un usuario
    def updateUser(self, user):
        self.collection.update()

    def searchUser(self, user):
        return self.collection.find(
            {
                "_id": user.token
            }
        ).pretty()

    # Pantry Querys_____________________________
    def newIngredient(self, user, pantry, ingredient):
        #TODO: Falta imagen
        self.collection.insert_one(
            {
                "_id": user.token,  # Codigo id único en mongo db
                "ingredient": user.username,
                "quantity": user.status,
            }
        )

    def searchIngredient(self, user, ingredient):
        return self.collection.find(
            {
                "_id": user.token,
                "ingredient": ingredient
            }
        ).pretty()

    def updateIngredient(self, user, ingredient):
        self.collection.update(
            {
                "_id": user.token,
                "ingredient": ingredient
            }
        )

    # ShoppingList Querys_______________________
