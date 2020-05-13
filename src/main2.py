from src.BBDD import MongoDB
from src.Model.Ingredient import Ingredient
from src.Model.User import User


def main():
    mongo = MongoDB()
    user = User("token_aleatorio", "Test", 0.0, "Spanish")
    ingredient = Ingredient("Bacon", 11, None)

    # mongo.new_user(user)
    mongo.new_ingredient(user, ingredient)
    mongo.update_user_status("token_aleatorio", 1.0)
    find = mongo.search_user(user)
    print(find["status"])

    mongo.client.close()


if __name__ == '__main__':
    main()
