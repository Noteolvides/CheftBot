from clarifai.rest import ClarifaiApp
import json


if __name__ == '__main__':
    # Instantiate a new Clarifai app by passing in your API key.
    app = ClarifaiApp(api_key='e1f4f037491d42d298b6b7c80ee778e4')

    # Choose one of the public models.
    model = app.public_models.general_model

    # Predict the contents of an image by passing in a URL.

    response = model.predict_by_url(url='https://www.eluniversal.com.mx/sites/default/files/styles/f03-651x400/public/2016/09/07/manzana.jpg?itok=V5_501d_')
    print(response["outputs"][0]["data"]["concepts"][0]["name"])
