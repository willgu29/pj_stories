from textblob import TextBlob
import requests
import json
import random
import sentenceToText
import pixabayAPI


type_picture = 0
type_video = 1
type_gif = 2

class Content(object):
    displayURL = ""
    downloadURL = ""
    formatType = -1 # 0 = pic, 1 = video, 2 = gif

    def __init__(self, displayURL, downloadURL, formatType):
        self.displayURL = displayURL
        self.downloadURL = downloadURL
        self.formatType = formatType
    def serialize(self):
        return {
            'displayURL' : self.displayURL,
            'downloadURL': self.downloadURL,
            'formatType' : self.formatType
        }

def make_content(displayURL, downloadURL, formatType):
    content = Content(displayURL, downloadURL, formatType)
    return content

def convertToStoryToArray(story):
    blob = TextBlob(story)
    return blob.sentences

    

def getContentFromPhrase(phrase):
    videoURL, downloadURL = pixabayAPI.getVideoFromPhrase(phrase)
    pictureURL, viewURL = pixabayAPI.getPictureFromPhrase(phrase)
    gifURL, mp4URL = sentenceToText.getGifFromPhrase(phrase)

    if (videoURL != ""):
        return make_content(videoURL, downloadURL, type_video)
    elif (pictureURL != ""):
        return make_content(pictureURL, viewURL, type_picture)
    elif (gifURL != ""):
        return make_content(gifURL, mp4URL, type_gif)
    else:
        return "No content found", "None"
