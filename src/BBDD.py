import json

from pymongo import MongoClient

from src.Model.Item import Item


class MongoDB:
    def __init__(self):
        self.client = MongoClient(port=27017)
        self.db = self.client["ChefBot"]
        self.collection = self.db["CB_User"]
        self.collection_recipe = self.db["CB_Recipies"]
        self.collection_shopping_list = self.db["CB_SPList"]

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
                    "possible_ingredient": "",
                    "ingredients": []
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

    def use_ingredient(self, id, ingredient):
        return self.collection.update(
            {"_id": id, "ingredients.name": ingredient["name"]},
            {"$set": {"ingredients.$.amount": ingredient["amount"]}}
        )

    # ShoppingList Querys_______________________
    def search_list(self, user_id):
        return self.collection_shopping_list.find_one({"_id": user_id})

    def add_missing_item(self, user_id, item):
        self.collection_shopping_list.find_one_and_update(
            {"_id": user_id},
            {"$push":
                {"items": {
                    "item": item["name"],
                    "quantity": item["amount"],
                    "unit": item["unit"],
                    "done": False
                }
                }
            }, upsert=True
        )

    def add_item(self, user_id, item):
        shopping_list = self.search_list(user_id)

        if shopping_list is None:
            self.collection_shopping_list.insert_one({"_id": user_id, "items": []})
        else:
            for e in shopping_list["items"]:
                if e["done"] == 0 and e["item"] == item.name and e["unit"] == item.unit:
                    item.quantity += e["quantity"]
                    self.delete_item_list(user_id, item)
                    break

        return self.collection_shopping_list.find_one_and_update(
            {"_id": user_id},
            {"$push":
                {"items": {
                    "item": item.name,
                    "quantity": item.quantity,
                    "unit": item.unit,
                    "done": item.done
                }
                }
            }
        )

    def delete_item_list(self, user_id, item):
        self.collection_shopping_list.update_one(
            {"_id": user_id, "items.item": item.name}, {"$unset": {"items.$": 1}}
        )
        return self.collection_shopping_list.update({"_id": user_id}, {"$pull": {"items": None}})

    def delete_list(self, user_id):
        self.collection_shopping_list.remove({"_id": user_id})

    def mark_item(self, user_id, item):
        shopping_list = self.search_list(user_id)

        if shopping_list is not None:
            for e in shopping_list["items"]:
                if e["item"] == item.name and e["done"] == 0:
                    return e
        return None

        # Recipies API______________________________

    def insert_new_recipie(self, recipie):
        # TODO: hace falta controlar que no repiten las recipies
        self.collection_recipe.insert({recipie})
        pass

    def delete_item(self, user_id, item):
        pass

    def delete_ingredient_by_name(self, id, nameIngredient):
        self.collection.update_one({"_id": id, "ingredients.name": nameIngredient}, {"$unset": {"ingredients.$": 1}})
        why = self.collection.update({"_id": id}, {"$pull": {"ingredients": None}})

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

    def new_choose_recipe(self, token, recipe):
        self.collection.find_one_and_update(
            {"_id": token},
            {"$push": {"choose_recipes": recipe}
             }
        )

    def set_cooking_recipe(self, id_user, state):
        self.collection.find_one_and_update(
            {"_id": id_user},
            {"$set": {"cooking": state}}, upsert=True
        )

    def get_cooking_recipe(self, user_id):
        user = self.search_user_by_id(user_id)
        return user["cooking"]

    def add_missing_ingredient(self, user_id, missing_ingredient):
        self.collection.find_one_and_update(
            {"_id": user_id},
            {"$push": {"missing_ingredients": missing_ingredient}}
            , upsert=True
        )

    def get_missing_ingredients(self, user_id):
        user = self.search_user_by_id(user_id)
        return user["missing_ingredients"]

    def delete_missing_ingredients(self, id):
        self.collection.update_one({"_id": id}, {"$unset": {"missing_ingredients": 1}})
        why = self.collection.update({"_id": id}, {"$pull": {"missing_ingredients": None}})

    def delete_choose_recipes(self, id):
        self.collection.update_one({"_id": id}, {"$unset": {"choose_recipes": 1}})
        why = self.collection.update({"_id": id}, {"$pull": {"choose_recipes": None}})

    def get_choose_recipes(self, id):
        user = self.search_user_by_id(id)
        return user["choose_recipes"]

    def find(self, param):
        return self.collection.find({})
