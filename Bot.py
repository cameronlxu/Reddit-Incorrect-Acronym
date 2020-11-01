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

def main():
    # Iterate through all comments in subreddit
    for comment in subreddit.stream.comments():
        full_definition = {}

        # comment.body is one string, use .split() to separate each word into an array
        viewComment = comment.body.split()

        # Ensure bot doesn't deal with itself
        if comment.author.name == "incorrectacronymbot":
            print("This comment is mine! ID:", comment)
            continue

        # Check if we have already replied to a comment by checking the comment ID
        if str(comment) in posts_replied:
            print("I have already replied to this post! ID:", comment)
            continue
        
        # Check if the comment is using command !Suggest
        if viewComment[0] == "!Suggest":
            # Check if custom word/definiton already exists
            if viewComment[1].lower() not in custom_words:
                Suggest(comment, viewComment)
            else:
                comment.reply("This acronym already exists in my personal dictionary!")
                print("[" + viewComment[1] + "] already exists in the custom dictionary!")
        else: 
            createDefiniton(full_definition, comment, viewComment)
        
        # Write to post_replied_to since we created a new comment
        write_posts_replied_to(comment)

def Suggest(comment, viewComment):
    """
        Suggest function:
            - add acronym & definiton to custom_dictionary
            - add comment ID to post_replied_to
            - format & send reply comment

        Key = word.lower()
        Value = All words after the 1st index then subtract last index (whitespace)
    """
    key = viewComment[1].lower()
    value = ""
    for index in range(2, len(viewComment)):
        value += viewComment[index] + " "
    
    value = value [:-1]         # Subtract last index due to whitespace
    custom_words[key] = value   # Set key & value in custom_words

    # Cast comment ID into string and add it to post_replied, using dummy value 1
    posts_replied[str(comment)] = 1

    # Serializing and writing to custom_dictionary.json  
    json_custom_words = json.dumps(custom_words, indent = 4) 
    with open("custom_dictionary.json", "w") as outfile: 
        outfile.write(json_custom_words)
    
    # Format and send reply comment
    key = key.upper()
    reply = """I added a new acronym to my personal dictionary!\n\n
    Word: {}\n
    Defintion: {}\n\n^(Thanks for making the Incorrect Acronym Bot even more incorrect! xD)""".format(key, value)
    comment.reply(reply)
    print("Added [" + key + "] [" + value + "] to custom dictionary!")

def createDefiniton(full_definition, comment, viewComment):
    for word in viewComment:
        lowered_word = word.lower()
        # Prioritize words in custom_dictionary.json
        if lowered_word in custom_words:
            full_definition[word] = custom_words[lowered_word]
            continue
        # Check if word is in words_dictionary.json
        if lowered_word not in words:
            definition = ""
            for letter in word:
                # Randomly pick a word in words_dictionary
                # If first letter of the random word matches the letter of acronym, add to defintion and break 
                while True:
                    randomWord = random.choice(list(words.keys()))  # Selects random word from list of words
                    if randomWord[0] == letter.lower():
                        definition += randomWord + " "
                        break
            definition = definition[:-1]                            # Remove last index (whitespace)
            full_definition[word] = definition                      # Key = acronym, value = newly created definition    

    # Format & send reply comment
    if len(full_definition) != 0:
        count = 1
        word_def = """"""
        for word in full_definition.keys():
            word_def += """{} - {}: {}\n""".format(str(count), word, full_definition[word])
            count += 1

        print(word_def)
        reply = """I found """ + str(len(full_definition)) + """ acronym(s) that can be defined.\n\n
        {}\n\n^(Thanks for using the Incorrect Acronym Bot xD)
        """.format(word_def)

        comment.reply(reply)
        print("posted comment ID: {}!".format(comment))

def write_posts_replied_to(comment):
    # Cast comment ID into string and add it to post_replied, using dummy value 1
    posts_replied[str(comment)] = 1

    # Serializing and writing to posts_replied_to.json
    json_posts_replied = json.dumps(posts_replied, indent = 4) 
    with open("posts_replied_to.json", "w") as outfiles:
        outfiles.write(json_posts_replied)


if __name__ == "__main__":
    main()