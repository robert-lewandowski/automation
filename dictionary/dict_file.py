import json
import difflib 
from difflib import SequenceMatcher, get_close_matches

data = json.load(open("data.json"))

# function to provide a definition for a word

def translate(w):
    w = w.lower()
    if w in data:
        return data[w]
    elif len(get_close_matches(w, data.keys())) > 0:
        return "Did you mean %s instead? " % get_close_matches(w,data.keys())[0]
    else:
        return "The word does not exist. Please double check it."

word = input("Enter a word: ")
print(translate(word))

