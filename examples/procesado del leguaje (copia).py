import spacy


if __name__ == '__main__':
    # Create the nlp object
    nlp = spacy.load('es_core_news_sm')

    # Process a text
    doc = nlp('Hola, que tal')

    # Iterate over the tokens
    for token in doc:
        # Print the text and the predicted part-of-speech tag
        print(token.text, token.pos_)

