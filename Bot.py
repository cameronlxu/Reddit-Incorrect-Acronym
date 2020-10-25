import praw
import json
import random
import Settings as botInfo


# set english dictionary json file as variable "words"
with open('./words_dictionary.json') as dictionary:
    words = json.load(dictionary)

# Create reddit instance
reddit = praw.Reddit(
    client_id       = botInfo.Settings.client_id,
    client_secret   = botInfo.Settings.client_secret,
    username        = botInfo.Settings.username,
    password        = botInfo.Settings.password,
    user_agent      = botInfo.Settings.user_agent
)


# Specify which subreddit the bot will look at
subreddit = reddit.subreddit('incorrectacronym')
full_definition = {}


# Iterate through all comments in subreddit
for comment in subreddit.stream.comments():
    goingToReply = False
    viewComment = comment.body.split()      # comment.body is one string, use .split() to separate each word into an array
    for word in viewComment:
        if word.lower() in words:
            continue
        else:
            goingToReply = True
            definition = ""
            for letter in word:
                found = False
                while found == False:
                    randomWord = random.choice(list(words.keys()))      # selects random word from list of words
                    if randomWord[0] == letter.lower():
                        definition += randomWord + " "
                        found = True
            full_definition[word] = definition      # key = acronym, value = newly created definition
    
    if goingToReply == True:
        if len(full_definition) == 1:
            reply = "I found " + str(len(full_definition)) + " acronym that can be defined.\n"
        else:
            reply = "I found " + str(len(full_definition)) + " acronyms that can be defined.\n"
        count = 1
        for word in full_definition.keys():
            reply += str(count) + " - " + word + ": " + full_definition[word] + "\n"
            count += 1
        comment.reply(reply)
        goingToReply = False
        print("posted!")