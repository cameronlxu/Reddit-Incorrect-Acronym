import praw
import json
import random
import Settings as botInfo


# Open json files and assign them to variables
with open('./words_dictionary.json') as dictionary:
    words = json.load(dictionary)

with open('./custom_dictionary.json') as cust_dictionary:
    custom_words = json.load(cust_dictionary)

with open('./posts_replied_to.json') as posts_replied_to:
    posts_replied = json.load(posts_replied_to)

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
keyword = "!Suggest"


def main():
    # Iterate through all comments in subreddit
    for comment in subreddit.stream.comments(skip_existing = False):
        viewComment = comment.body.split()              # comment.body is one string, use .split() to separate each word into an array

        # Check if we have already replied to a comment by checking the comment ID
        if str(comment) in posts_replied:
            print("I have already replied to this post! ID:", comment)
            continue
        
        # Check if the comment is using command !Suggest
        if viewComment[0] == keyword:
            if viewComment[1].lower() not in custom_words:
                key = viewComment[1].lower()            # Key = word.lower, Value = All words after the 1st index then subtract last index (whitespace)
                value = ""
                for index in range(2, len(viewComment)):
                    value += viewComment[index] + " "
                value = value [:-1]
                custom_words[key] = value
                posts_replied[str(comment)] = 1         # Cast comment ID into string and add it to post_replied, using dummy value 1

                # Serializing and writing to custom_dictionary.json  
                json_custom_words = json.dumps(custom_words, indent = 4) 
                with open("custom_dictionary.json", "w") as outfile: 
                    outfile.write(json_custom_words)

                # Serializing and writing to posts_replied_to.json
                json_posts_replied = json.dumps(posts_replied, indent = 4) 
                with open("posts_replied_to.json", "w") as outfiles:
                    outfiles.write(json_posts_replied)

                # Format and send reply comment
                key = key.upper()
                reply = """I added a new acronym to my personal dictionary!\n\n
                Word: {}\n
                Defintion: {}\n\n^(Thanks for making the Incorrect Acronym Bot even more incorrect! xD)""".format(key, value)
                comment.reply(reply)
                print("Added [" + key + "] [" + value + "] to custom dictionary!")
            else:
                reply = "This acronym already exists in my personal dictionary!"
                comment.reply(reply)
                print("[" + viewComment[1] + "] already exists in the custom dictionary!")
        else: 
            goingToReply = False
            for word in viewComment:
                if word.lower() in words:
                    continue
                else:
                    goingToReply = True
                    definition = ""
                    for letter in word:
                        found = False
                        while found == False:
                            randomWord = random.choice(list(words.keys()))  # Selects random word from list of words
                            if randomWord[0] == letter.lower():
                                definition += randomWord + " "
                                found = True
                    full_definition[word] = definition                      # Key = acronym, value = newly created definition
            
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


if __name__ == "__main__":
    main()