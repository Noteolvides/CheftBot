from pymongo import MongoClient


class MongoDB:
    def __init__(self):
        self.client = MongoClient(port=27017)
        self.db = self.client["ChefBot"]
        self.collection = self.db["CB_User"]
        # self.collection = self.db["CB_Recipies"]

    # User querys______________________________
    def update_user_status(self, token, status):
        self.collection.find_one_and_update(
            {"_id": token},
            {"$set": {"status": status}}
        )

    # Con esta función se puedo conocer el usuario con detalle (estado, teclado, etc)
    def search_user(self, user):
        return self.collection.find_one(
            {"_id": user.token}
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

    # Pantry Querys_____________________________
    # TODO: comprobar antes si el ingrediente que se quiere añadir existe
    def new_ingredient(self, user, ingredient):
        # TODO: Falta imagen
        self.collection.find_one_and_update(
            {
                "_id": user.token
            },
            {
                "$push":
                    {
                        "ingredients": [
                            {
                                "ingredient_name": ingredient.ingredient,
                                "quantity": ingredient.quantity
                            }
                        ]
                    }
            }
        )

    #fixme: no encuetra nah de nah
    def search_ingredient(self, user, ingredient):
        return self.collection.find_one(
            {
                "_id": user.token,
                "ingredient": ingredient.ingredient
            }
        )

    def update_ingredient(self, user, ingredient):
        self.collection.update(
            {
                "_id": user.token,
                "ingredient": ingredient.ingredient
            },
            {"$set":
                {
                    "_id": user.token,  # Codigo id único en mongo db
                    "ingredients": {
                        "ingredient_name": [ingredient.ingredient],
                        "quantity": ingredient.quantity
                    }
                }
            }
        )

    # TODO: search all ingredients

    # ShoppingList Querys_______________________

    # TODO: insert recipies from api and create collection
