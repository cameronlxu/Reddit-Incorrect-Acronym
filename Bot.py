import praw
import json
import random
from cryptography.fernet import Fernet
import Settings as botInfo


# Open json files and assign them to variables
with open('./Data/words_dictionary.json') as dictionary:
    words = json.load(dictionary)

with open('./Data/custom_dictionary.json') as cust_dictionary:
    custom_words = json.load(cust_dictionary)

with open('./Data/posts_replied_to.json') as posts_replied_to:
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

        # Ensure bot doesn't reply to itself
        if comment.author.name == "incorrectacronymbot":
            print("This comment is mine! ID:", comment)
            continue

        # Check if we have already replied to a comment
        found = check_commentExists(comment)
        if found == True:
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


def generate_secret_key() -> None:
    """
        Generate a new Fernet key, and write it to ./secret.key
    """
    key = Fernet.generate_key()
    with open("./secret.key", "wb") as key_file:
        key_file.write(key)

def load_secret_key() -> bytes:
    """
        Load the BYTES type key in secret.key.
        If ./secret.key is empty, call generate_secret_key() to generate a new Fernet key. 
    """
    key = open("./secret.key", "rb").read()

    # If the Fernet key doesn't exist, create a Fernet key
    if key == b'':
        generate_secret_key()

    return open("./secret.key", "rb").read()


def check_commentExists(comment) -> bool:
    """
        Decrypt each key in posts_replied_to.json, then compare it to the input comment.
        If equal, return True. Else return False. 
    """
    secret_key = load_secret_key()
    f = Fernet(secret_key)
    for key in posts_replied.keys():
        # Decrypt function only takes in type BYTE, thus need to encode the key
        decrypted_key = f.decrypt(key.encode())

        # To compare the key and comment, cast both to strings
        if str(decrypted_key.decode()) == str(comment):
            print("I have already replied to this post! ID:", comment)
            return True
    return False


def Suggest(comment, viewComment) -> None:
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
    write_posts_replied_to(comment)

    # Serializing and writing to custom_dictionary.json  
    json_custom_words = json.dumps(custom_words, indent = 4) 
    with open("./Data/custom_dictionary.json", "w") as outfile: 
        outfile.write(json_custom_words)
    
    # Format and send reply comment
    key = key.upper()
    reply = """I added a new acronym to my personal dictionary!\n\n
    Word: {}\n
    Defintion: {}\n\n^(Thanks for making the Incorrect Acronym Bot even more incorrect! xD)""".format(key, value)
    comment.reply(reply)
    print("Added [" + key + "] [" + value + "] to custom dictionary!")


def createDefiniton(full_definition, comment, viewComment) -> None:
    """
        Create Definition function:
            - check if word is in custom dictionary
            - check if word is not in words dictionary
            - format & send reply comment
    """
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


def write_posts_replied_to(comment) -> None:
    """
        Replied-To function:
            - Check if comment ID is in replied-to
            - If not then add comment ID to json
    """
    # Load Fernet Secret Key
    secret_key = load_secret_key()
    f = Fernet(secret_key)

    # Encrypt function parameter has to be of type BYTE, so encode the comment to be of type BYTE
    key = str(comment).encode()
    token = f.encrypt(key)

    # A dictionary cannot take BYTE type as key, so cast to string by decoding. Set dummy value of 1
    posts_replied[token.decode()] = 1

    # Serializing and writing to posts_replied_to.json
    json_posts_replied = json.dumps(posts_replied, indent = 4) 
    with open("./Data/posts_replied_to.json", "w") as outfiles:
        outfiles.write(json_posts_replied)


if __name__ == "__main__":
    main()