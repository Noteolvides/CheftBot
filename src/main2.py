from src.BBDD import MongoDB
from src.Model.Ingredient import Ingredient
from src.Model.User import User
from bson.json_util import dumps

def main():
    mongo = MongoDB()
    user = User("token_aleatorio", "Test", "List", "Spanish")
    ingredient = Ingredient("Huevos", 12, None)

    #mongo.new_user(user)
    #mongo.new_ingredient(user, ingredient)

    find = mongo.search_user(user)
    dumps(find)

    mongo.client.close()


if __name__ == '__main__':
    main()
