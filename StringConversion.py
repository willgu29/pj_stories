from textblob import TextBlob
import requests
import json
import random

replace_array = [(u"\u2018", "'"), (u"\u2019", "'"),
                (u"\u201c", "\""), (u"\u201d", "\""),
                (u"\u2014", "-"), (u"\u2011", "-"),
                (u"\u2026", "..."),
                ("\r", " "), ("\n", " ")]

#we're stuck on ascii boys... After Effects also seems to have problems with unicode, not sure.
def replaceUnicode(string):
    for code in replace_array:
        string = string.replace(code[0], code[1])
    print string
    return string
