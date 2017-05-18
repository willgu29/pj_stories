from textblob import TextBlob
import requests
import json
import random

#used to fetch more gifs if user sentence is short or can't find any
fill_phrases = ["You got it.", "Freedom", "Take that!", "I am god.", "That's enough already."];
#give more variety to emotional responses
positive_res = ["Nice", "Woo!", "Hell yeah"]
negative_res = ["Damn", "We're fucked", "Not like this"]
neutral_res = ["Huh", "I don't get it", "Okay"]

#break sentence into parts of speech and return relevant words and phrases
def getPartsFromSentence(sentence):
    blob = TextBlob(sentence)
    #nounList = []
    translateList = []
    responseList = []

    # get parts of speech from sentence then add to array
    for word, pos in blob.tags:
        print word, pos
        if "VB" in pos:
            translateList.append(word)
        if "NN" in pos:
            translateList.append(word)
        if "JJ" in pos:
            translateList.append(word)

    polarity =  blob.sentiment.polarity
    subjectivity = blob.sentiment.subjectivity

    print "Polarity,Subjectivity: ", polarity, subjectivity

    # add an emotional reaction word to array
    if polarity > 0.25:
        responseList.append(random.choice(positive_res))
    elif polarity < -0.25:
        responseList.append(random.choice(negative_res))
    else:
        responseList.append(random.choice(neutral_res))


    combinedList = translateList + responseList
    print combinedList

    return combinedList

#return random number of items from array
def getRandomNumberFromArray(array, number):
    if (len(array) >= number):
        pick_from_list = number
    else:
        pick_from_list = len(array)
    randomList = random.sample(array, pick_from_list)
    print randomList
    return randomList


def getGifsFromSentence(sentence, count):
    combinedList = getPartsFromSentence(sentence)
    randomList = getRandomNumberFromArray(combinedList, count)

    giphyURLS = []
    giphyMP4 = []

    #Giphy API search these phrases and add gifs to array
    for phrase in randomList:
        url, mp4 = getGifFromPhrase(phrase)
        if (url == ""):
            continue
        giphyURLS.append(url)
        giphyMP4.append(mp4)

    #Get some more gifs if they have less than 3
    exitCase = 0
    while len(giphyURLS) < count or exitCase > 5:
        phrase = random.choice(fill_phrases)
        print "Random phrase: " + phrase
        url, mp4 = getGifFromPhrase(phrase)
        if (url == ""):
            continue
        giphyURLS.append(url)
        giphyMP4.append(mp4)
        exitCase = exitCase + 1


    return randomList, giphyURLS, giphyMP4,


def getGifFromPhrase(phrase):
    giphyRequest = requests.get("http://api.giphy.com/v1/gifs/translate?s="+phrase+"&api_key=dc6zaTOxFJmzC")
    raw = json.loads(giphyRequest.text)
    data = raw['data']
    #When user enters nonexistent words (aslkdjlw1), will return a list so return
    if isinstance(data, list):
        return "", ""
    images = data.get('images')
    url = images.get('original').get('url')
    mp4 = images.get('original').get('mp4')
    return url, mp4
