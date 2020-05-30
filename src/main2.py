from src.BBDD import MongoDB
from src.Model.Ingredient import Ingredient
from src.Model.Item import Item
from src.Model.User import User


def main():
    mongo = MongoDB()
    user = User("token_aleatorio", "Test", 0.0, "Spanish")

    '''
    ingredient = Ingredient("Ous", 11, None)
    mongo.new_user(user)
    mongo.new_ingredient(user.token, ingredient)
    #mongo.update_user_status("token_aleatorio", 1.0)
    find = mongo.search_user_by_id(user.token)
    print(find["ingredients"][0])
    v = mongo.search_ingredient(user, ingredient)
    print(v)
    '''

    item = Item("Bacon", 1, "unidad")
    #mongo.add_item(user.token, item)

    shopping_list = mongo.search_list(user.token)
    if shopping_list is not None:
        print(mongo.delete_item_list(user.token, item))
        return
    mongo.client.close()


if __name__ == '__main__':
    main()
