from wit import Wit

import re

if __name__ == '__main__':
    # coding=utf8
    # the above tag defines encoding for this document and is for Python 2.x compatibility

    regex = r"(?<=Ingredient : )(.*)(?=Quantity : )"

    test_str = "Ingredient : Fish \n Quantity : 20 cacas"
    test_str = test_str.replace('\n', '')
    matches = re.search(regex, test_str, re.MULTILINE)
    print(matches.group())
