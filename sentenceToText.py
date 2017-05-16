from textblob import TextBlob
import requests
import json
import random


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
        responseList.append("Nice")
    elif polarity < -0.25:
        responseList.append("Damn")
    else:
        responseList.append("Huh")


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

    return randomList, giphyURLS, giphyMP4,


def getGifFromPhrase(phrase):
    giphyRequest = requests.get("http://api.giphy.com/v1/gifs/translate?s="+phrase+"&api_key=dc6zaTOxFJmzC")
    raw = json.loads(giphyRequest.text)
    data = raw['data']
    images = data.get('images')
    url = images.get('original').get('url')
    mp4 = images.get('original').get('mp4')
    return url, mp4
