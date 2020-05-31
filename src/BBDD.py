from pymongo import MongoClient


class MongoDB:
    def __init__(self):
        self.client = MongoClient(port=27017)
        self.db = self.client["ChefBot"]
        self.collection = self.db["CB_User"]
        # self.collection = self.db["CB_Recipies"] TODO: ver como tratar dos colecciones a la vez

    # User querys______________________________
    # Con esta función se puedo conocer el usuario con detalle (estado, teclado, ingredientes, etc)
    def search_user_by_id(self, token):
        self.collection = self.db["CB_User"]
        return self.collection.find_one({"_id": token})

    def new_user(self, user):
        if self.search_user_by_id(user.token) is None:
            self.collection.insert_one(
                {
                    "_id": user.token,
                    "username": user.username,
                    "status": user.status,
                    "possible_ingredient": ""
                }
            )

    def update_user_status(self, token, status):
        self.collection = self.db["CB_User"]
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
    def new_ingredient(self, user_id, ingredientInput):
        self.collection.find_one_and_update(
            {"_id": user_id},
            {"$push":
                {
                    "ingredients":
                        {
                            "ingredient_name": ingredientInput.ingredient,
                            "quantity": ingredientInput.quantity,
                        }
                },
            {"_id": user_id}:
            {
                "$push":
                    {
                        "ingredients": ingredientInput
                    }
            }
            }
        )

    def search_ingredient(self, user, ingredient):
        # fixme: no encuetra nah de nah
        print("jajas")

    def get_ingredients(self, id):
        user = self.search_user_by_id(id)
        return user["ingredients"]

    def get_ingredient_by_name(self, user_id, name):
        return self.collection.find_one(
            {"_id": user_id, "ingredients": [{"ingredient_name": name}]}
        )

    def get_ingredient_by_id(self, id, ingredient_id):
        return self.collection.find_one(
            {"_id": id, "ingredients": [{"id": ingredient_id}]}
        )

    # def update_ingredient(self, user, ingredient):
    #     self.collection.update(
    #         {"_id": user.token, "ingredient": ingredient.ingredient},
    #         {"$set":
    #             {
    #                 "_id": user.token,  # Codigo id único en mongo db
    #                 "ingredients": {
    #                     "ingredient_name": [ingredient.ingredient],
    #                     "quantity": ingredient.quantity
    #                 }
    #             }
    #         }
    #     )

    def update_ingredient(self, id, ingredient):
        return self.collection.update(
            {"_id": id, "ingredients.name": ingredient["name"]},
            {"$inc": {"ingredients.$.amount": ingredient["amount"]}}
        )

    # ShoppingList Querys_______________________
    def search_list(self, user_id):
        self.collection = self.db["CB_SPList"]
        return self.collection.find_one({"_id": user_id})

    def add_item(self, user_id, item):
        self.collection = self.db["CB_SPList"]
        shopping_list = self.search_list(user_id)

        if shopping_list is None:
            self.collection.insert_one({"_id": user_id, "items": []})
        else:
            for e in shopping_list["items"]:
                if e["item"] == item.name and e["unit"] == item.unit:
                    item.quantity += e["quantity"]
                    self.delete_item_list(user_id, item)
                    break

        self.collection.find_one_and_update(
            {"_id": user_id},
            {"$push":
                {"items": {
                    "item": item.name,
                    "quantity": item.quantity,
                    "unit": item.unit,
                }
                }
            }
        )

    def delete_item_list(self, user_id, item):
        self.collection = self.db["CB_SPList"]
        self.collection.update_one(
            {"_id": user_id, "items.item": item.name, "items.unit": item.unit}, {"$unset": {"items.$": 1}}
        )
        return self.collection.update({"_id": user_id}, {"$pull": {"items": None}})

    # Recipies API______________________________

    def insert_new_recipie(self, recipie):
        # TODO: hace falta controlar que no repiten las recipies
        self.collection = self.db["CB_Recipies"]
        self.collection.insert({recipie})
        pass

    def delete_item(self, user_id, item):
        pass

    def delete_ingredient_by_name(self, id, nameIngredient):
        self.collection.update_one({"_id": id, "ingredients.name": nameIngredient}, {"$unset": {"ingredients.$": 1}})
        why = self.collection.update({"_id": id}, {"$pull": {"ingredients": None}})

    # ShoppingList Querys_______________________

    # Recipies API______________________________

    def update_actual_recipe(self, token, recipe):
        self.collection.find_one_and_update(
            {"_id": token},
            {"$set": {"actual_recipe": recipe}}
        )

    def get_actual_recipe(self, id):
        user = self.search_user_by_id(id)
        return user["actual_recipe"]

    def update_actual_steps(self, token, steps):
        self.collection.find_one_and_update(
            {"_id": token},
            {"$set": {"actual_steps": steps}}
        )

    def get_actual_steps(self, id):
        user = self.search_user_by_id(id)
        return user["actual_steps"]

    def update_number_step(self, id, number_step):
        self.collection.find_one_and_update(
            {"_id": id},
            {"$set": {"number_step": number_step}}
        )

    def get_number_step(self, id):
        user = self.search_user_by_id(id)
        return user["number_step"]

    def push_choose_recipe(self, token, recipe):
        self.collection.find_one_and_update(
            {"_id": token},
            {"$push": {"choose_recipes": {"$each": [
                {"recipe_id": recipe.recipe_id,
                 "title": recipe.title,
                 "img": recipe.img}
            ]}}}, upsert=True
        )

    def new_choose_recipe(self, token, recipe):
        self.collection.find_one_and_update(
            {"_id": token},
            {"$push": {"choose_recipes": recipe}
             }
        )

    def delete_choose_recipes(self, id):
        self.collection.update_one({"_id": id}, {"$unset": {"choose_recipes": 1}})
        why = self.collection.update({"_id": id}, {"$pull": {"choose_recipes": None}})

    def get_choose_recipes(self, id):
        user = self.search_user_by_id(id)
        return user["choose_recipes"]

    def find(self, param):
        return self.collection.find({})
