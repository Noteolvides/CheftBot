from difflib import SequenceMatcher

import emoji
import spacy
from chatterbot.comparisons import JaccardSimilarity
from chatterbot.conversation import Statement
import spoonacular as sp


if __name__ == '__main__':
    api = sp.API("aa9cc6861144497a9ce2ab7ffa864984")
    haha = api.parse_ingredients("20 kg of fish")
    print(haha)
