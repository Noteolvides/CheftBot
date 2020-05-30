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
                    "possible_ingredient": ""
                }
            )

    def update_user_status(self, token, status):
        self.collection.find_one_and_update(
            {"_id": token},
            {"$set": {"status": status}}
        )

    def possible_ingredient(self, token, ingredient):
        self.collection.find_one_and_update(
            {"_id": token},
            {"$set": {"possible_ingredient": ingredient}}
        )

    def get_possible_ingredient(self, token):
        user = self.search_user_by_id(token)
        return user["possible_ingredient"]

    # Pantry Querys_____________________________
    # TODO: comprobar antes si el ingrediente que se quiere añadir existe

    def new_ingredient(self, id, ingredientInput):
        self.collection.find_one_and_update(
            {"_id": id},
            {
                "$push":
                    {
                        "ingredients": ingredientInput
                    }
            }
        )

    # fixme: no encuetra nah de nah
    def get_ingredients(self, id):
        user = self.search_user_by_id(id)
        return user["ingredients"]

    def get_ingredient_by_name(self, id, name):
        return self.collection.find_one(

            {"_id": id, "ingredients.name": name}

        )

    def update_ingredient(self, id, ingredient):
        return self.collection.update(
            {"_id": id, "ingredients.name": ingredient["name"]},
            {"$inc": {"ingredients.$.amount": ingredient["amount"]}}
        )

    # ShoppingList Querys_______________________

    # Recipies API______________________________

    def insert_new_recipie(self, recipie):
        pass

    def delete_ingredient_by_name(self, id, nameIngredient):
        self.collection.update_one({"_id": id, "ingredients.name": nameIngredient}, {"$unset": {"ingredients.$": 1}})
        why = self.collection.update({"_id": id}, {"$pull": {"ingredients": None}})
