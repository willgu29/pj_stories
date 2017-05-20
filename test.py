from flask import Flask, render_template, request, jsonify, make_response

app = Flask(__name__)


#TODO: Convert stories to video format *** priority 1 ****
#TODO: machinelearning time?

#TODO: AI speak text? Easier "movie" watching experience
#TODO: Still need to handle all unicode 128 + edge-cases... currently only deals with left and right quote
#TODO: downloadLink https vs http and giphy-downsized-large problems
#TODO: Allow users to refresh gif choices (also correct array when user clicks back to repick)
#TODO: User profiles for saved non-public stories and option to make public
#TODO: Mobile optimize
#TODO: Next or previous button for next video or story when done
#TODO: Giphy blocks download on "originals" that they've made as part of a campaign... they are rare but yah.

from ast import literal_eval
import HTMLParser
import json
import os
import urllib
import sentenceToText
import pixabayAPI
import convertToStory
import StringConversion
logo_gif_url = "https://media.giphy.com/media/VkMV9TldsPd28/giphy.gif"


#DATABASE_MONGODB
from mongoengine import *
from mongoengine import connect
from datetime import *
connect("storyV0", host="mongodb://penguinjeffrey:penguinsfly12@ds137141.mlab.com:37141/heroku_c8gh7l20")

class Story(Document):
    title = StringField(required=True, max_length=200, default="")
    sentences = ListField(StringField(), required=True, default=list)
    gifURLS = ListField(URLField(), required=True, default=list)
    #optional urls for additional ways to consume the information
    videoURL = StringField(default="")
    articleURL = StringField(default="")
    #downloadURLS are simply gifURLS by replacing .gif with .mp4, so we don't save them
    isPublic = BooleanField(default=False)
    views = IntField(default=0)
    created = DateTimeField(default=datetime.now())
    genre = StringField(required=True, default="FICTION")
    location = StringField(required=True, default="UNDEFINED")
    meta = {'allow_inheritance': True}

@app.route("/")
def hello():
    stories = []
    for story in Story.objects:
        if story.isPublic:
            stories.append(story)
    return render_template('home.html', stories = stories)

@app.route('/watch')
def watch():
    stories = []
    for story in Story.objects:
        stories.append(story)
    return render_template('home.html', stories = stories)



@app.route("/story/<id>/<page>")
def story(id, page):
    storyArray = Story.objects(id=id)
    story = storyArray[0]
    page = int(page)
    views = story.views
    length = len(story.sentences)
    print story.videoURL
    if (page >= len(story.sentences)):
        content = logo_gif_url
        sentence = "The End."
        page = -1
        story.views = story.views + 1
        story.save()
    else:
        content = story.gifURLS[page]
        sentence = story.sentences[page]

    shareData = {
        "link" : "https://text-to-gif.herokuapp.com/story/" + id + "/" + "0",
        "gif" : story.gifURLS[0],
        "sentence" : story.sentences[0]
    }

    return render_template("viewStory.html", story = story, content = content, sentence = sentence,
    count = page, views = views, length = length, shareData = shareData)

@app.route("/story/<id>")
def videoStory(id):
    storyArray = Story.objects(id=id)
    story = storyArray[0]
    videoURL = story.videoURL
    shareLink = "https://text-to-gif.herokuapp.com/story/" + id + "/" + "0"
    return render_template("viewVideoStory.html", story = story, videoURL = videoURL, shareLink = shareLink)



@app.route("/createGIFStory/<int:page>", methods=["POST"])
def createGIFStory(page):
    story = request.form['story']
    sentences = convertToStory.convertToStoryToArray(story)

    if (page >= len(sentences)):
        page = -1
    else:
        sentence = sentences[page]
        #get rid of left and right hanging quotes for utf-8
        sentenceParts, gifURLS, gifMP4S =  sentenceToText.getGifsFromSentence(sentence.raw, 3)

    if (page == -1):
        sentence = "End Story."
        gifURLS = [logo_gif_url]

    resp = make_response(render_template('createGIFStory.html', story = story, contents = gifURLS,
        sentence = sentence, count = page))
    if (page == 0):
        #no saved gifs yet
        resp.set_cookie('savedGIFS', "[]")
    else:
        savedGIFS = literal_eval(request.cookies.get('savedGIFS'))
        selectedGIF = request.form['selectedGIF']
        savedGIFS.append(selectedGIF)
        resp.set_cookie('savedGIFS', jsonify(savedGIFS).get_data())

    return resp


#TODO: Replace /giphy-downsized-large.mp4 with giphy.mp4 reference [catchy title] for download fail case
@app.route('/downloadStory/<id>', methods=["GET"])
def downloadStory(id):
    storyArray = Story.objects(id=id)
    story = storyArray[0]
    gifURLS = story.gifURLS;
    downloadLinks = []
    for url in gifURLS:
        downloadLink = url.replace('.gif', '.mp4', 1)
        downloadLinks.append(downloadLink)
    return render_template('downloadStory.html', downloadLinks = downloadLinks, id = id)


@app.route("/createStory", methods=["POST"])
def createStory():
    parser = HTMLParser.HTMLParser()
    story = request.form['story']
    count = int(request.form['count'])
    sentences = convertToStory.convertToStoryToArray(story)
    selected = parser.unescape(request.form['selected'])
    selection = parser.unescape(request.form['selection'])

    print "Selection: ", selection

    if selected == "" or selected == None:
        selected = []
    else:
        selected = literal_eval(selected) #required otherwise thinks array is string

    if selection == "" or selection == None :
        error = "Please select an image :( "
    else:
        selected.append(selection)

    if (count == 0):
        selected = []

    if (count >= len(sentences)):
        count = -1
        sentence = "Congrats your done! Look below for directions."
        contents = []
        parsedData = ""
    elif (count < len(sentences)):
        sentence = sentences[count]
        phrases = sentenceToText.getRandomNumberFromArray(sentenceToText.getPartsFromSentence(str(sentence)), 3)
        contents = []
        for phrase in phrases:
            content = convertToStory.getContentFromPhrase(phrase)
            contents.append(content.serialize())
        data = jsonify(contents)
        parsedData = data.get_data()


    return render_template('createStory.html', story = story, sentence = sentence,
    count = count, contents = contents, selected = selected, data = parsedData)



@app.route("/saveStory", methods=["GET", "POST"])
def saveStory():
    if (request.method == "GET"):
        story = request.args.get("story")
        savedGIFS = literal_eval(request.cookies.get('savedGIFS'))
        sentences = convertToStory.convertToStoryToArray(story)
        return render_template("saveStory.html", story = story, sentences = sentences, contents = savedGIFS)


    print "saving story"
    genre = request.form['genre']
    location = request.form['location']
    story = request.form['story']
    isPublic = int(request.form["isPublic"])
    urls = literal_eval(request.form['urls'])
    sentences = convertToStory.convertToStoryToArray(story)

    stringArray = []
    for sentence in sentences:
        #we're stuck in ascii currently, so we get rid of common english unicode
        sentence = StringConversion.replaceUnicode(sentence.raw)
        stringArray.append(sentence)

    story = Story(  title=stringArray[0],
                    sentences=stringArray,
                    gifURLS=urls,
                    location=location,
                    isPublic=isPublic,
                    genre = genre )
    story.save()
    return render_template('savedStory.html', isPublic = isPublic, storyID = story.id)

@app.route("/gifs")
def gifs():
    q = request.args.get('q') or ''
    randomList, giphyURLS, giphyMP4 = sentenceToText.getGifsFromSentence(q, 4)
    return render_template('gifs.html', results = giphyURLS, q = q, phrases = randomList,
    links = giphyMP4)

@app.route("/pics")
def pics():
    q = request.args.get('q') or ''
    phrases, pictureURLS, webLinks  = pixabayAPI.getPicturesFromSentence(q)
    return render_template('pics.html', results = pictureURLS, q = q, phrases = phrases ,
    links = webLinks)

@app.route("/videos")
def videos():
    q = request.args.get('q') or ''
    phrases, videoURLS, downloadLinks  = pixabayAPI.getVideosFromSentence(q)
    return render_template('videos.html', results = videoURLS, q = q, phrases = phrases ,
    links = downloadLinks)

#Experimental routes

class Tracker(object):
    def __init__(self, startLetter, startCount):
        self.letter = startLetter
        self.count = startCount
    def increment(self):
        if (self.count == 26):
            self.count = 1
            self.letter = chr(ord(self.letter) + 1)
        else:
            self.count += 1



@app.route("/render/<id>")
def render(id):
    storyArray = Story.objects(id=id)
    if storyArray == []:
        return render_template('home.html')
    story = storyArray[0]


    #Each file must be uniquely named an in alphabetical order
    tracker = Tracker('a', 1)
    errorFiles = []
    fileRoot = "../Auto/" +  str(story.id)
    if not os.path.isdir(fileRoot):
        os.mkdir(fileRoot)

    #This loop supports up to 650 unique names
    for idx, url in enumerate(story.gifURLS):
        fileName = tracker.letter * tracker.count
        tracker.increment()
        downloadLink = url.replace('-downsized-large', '', 1).replace('.gif', '.mp4', 1)
        f, headers = urllib.urlretrieve(downloadLink, (fileRoot + "/" +fileName + ".mp4"))
        print f

    if (errorFiles == []):
        filePath = fileRoot + ".json"
    else:
        filePath = "../Staging/" + str(story.id)+ ".json"
    #Write json to Auto folder
    parsed = json.loads(story.to_json())
    pretty = json.dumps(parsed, indent=4, sort_keys=True)

    f = open(filePath, 'w')
    f.write(pretty)
    f.close()



    return render_template('render.html', filePath = filePath, errors = errorFiles)

@app.route("/generateStory", methods=["GET", "POST"])
def generateStory():
    if (request.method == "GET"):
        return render_template("test.html")

    story = request.form['story']
    sentences = convertToStory.convertToStoryToArray(story)
    selectedGIFS = []

    for sentence in sentences:
        sentenceParts, gifURLS, gifMP4S =  sentenceToText.getGifsFromSentence(sentence.raw, 1)
        gifURL = gifURLS[0]
        selectedGIFS.append(gifURL)

    return render_template("saveStory.html", story = story, sentences = sentences, contents = selectedGIFS)


if __name__ == "__main__":
    app.run()
