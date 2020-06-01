from clarifai.rest import ClarifaiApp


def predict_photo(photo):
    app = ClarifaiApp(api_key='e1f4f037491d42d298b6b7c80ee778e4')
    model = app.public_models.food_model
    response = model.predict_by_bytes(photo)
    print(response)
    return response["outputs"][0]["data"]["concepts"][0]["name"]