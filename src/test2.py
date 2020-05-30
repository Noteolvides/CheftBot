# set the apikey and limit
import json

import requests


def getGif(search_term):
    apikey = "1ZOT88VE51FT"  # test value
    lmt = 1
    r = requests.get(
        "https://api.tenor.com/v1/random?q=%s&key=%s&limit=%s" % (search_term, apikey, lmt))
    if r.status_code == 200:
        gifs = json.loads(r.content)
        return gifs["results"][0]["url"]
    else:
        gifs = "https://media1.tenor.com/images/335c59743ad925b364bc0615b681c0c0/tenor.gif"


if __name__ == '__main__':
    getGif("food")
