from textblob import TextBlob
import requests
import json
import random
import sentenceToText

root_url = 'https://pixabay.com/api/'

api_key = '1259450-dcca116316f88d68614be5596'

#TODO: Make arrays of urls into sets. (app will crash if same word is in array twice)

def getPicturesFromSentence(sentence):
    phrases = sentenceToText.getPartsFromSentence(sentence)
    picURLS = []
    webLinks = []
    for phrase in phrases:
            url, webLink = getPictureFromPhrase(phrase)
            if (url == ""):
                continue
            picURLS.append(url)
            webLinks.append(webLink)

    return phrases, picURLS, webLinks

def getPictureFromPhrase(phrase):
    pixabayRequest = requests.get(root_url+"?q="+phrase+"&key="+ api_key)
    raw = json.loads(pixabayRequest.text)
    data = raw["hits"]
    #no results :O
    if (len(data) <= 0 ):
        return "", ""
    # defaults 20 photos, get random one
    randomNumber = random.randint(0,(len(data) - 1))
    randomPhoto = data[randomNumber]
    url = randomPhoto.get('webformatURL')
    webLink = randomPhoto.get("webformatURL")
    return url, webLink

def getVideosFromSentence(sentence):
    phrases = sentenceToText.getPartsFromSentence(sentence)
    videoURLS = []
    downloadLinks = []
    for phrase in phrases:
        videoURL, downloadURL = getVideoFromPhrase(phrase)
        if (videoURL == ""):
            continue
        videoURLS.append(videoURL)
        downloadLinks.append(downloadURL)
    return phrases, videoURLS, downloadLinks

def getVideoFromPhrase(phrase):
    pixabayRequest = requests.get(root_url+"/videos/?q="+phrase+"&key="+api_key)
    raw = json.loads(pixabayRequest.text)
    data = raw["hits"]
    #no results :O
    if (len(data) <= 0 ):
        return "", ""
    # defaults 20 photos, get random one
    randomNumber = random.randint(0,(len(data) - 1))
    randomVideo = data[randomNumber]
    videoSizes = randomVideo.get("videos")
    #tiny, small, medium, large sizes
    videoURL = videoSizes.get('tiny').get("url")
    downloadURL = videoSizes.get('medium').get('url')
    return videoURL, downloadURL
