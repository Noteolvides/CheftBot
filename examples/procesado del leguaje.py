from spacy.lang.es import Spanish

if __name__ == '__main__':
    # Create the nlp object
    nlp = Spanish()

    doc = nlp("¿Hola, cómo estas?")
    print("Index:   ", [token.i for token in doc])
    print("Text:    ", [token.text for token in doc])

    print("is_alpha:", [token.is_alpha for token in doc])
    print("is_punct:", [token.is_punct for token in doc])
    print("like_num:", [token.like_num for token in doc])
