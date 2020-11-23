# Reddit-Incorrect-Acronym

The Reddit Incorrect Acronym bot is a bot that searches for words not in the english dictionary (which will most likely be acronyms) and provides a completely incorrect definiton! Additionally, the bot has its own custom dictionary where an acronym's definition within the dictionary is prioritized and outputted.

In the "Data" folder there are 3 JSON files:
- Custom_Dictionary - custom Acronym-Definiton pairs
- Posts_Replied_To - encrypted post/comment IDs, which are later decrypted for comparison
- Words_Dictionary - all words in the English dictionary

Subreddit Link: https://www.reddit.com/r/IncorrectAcronym/

## Installation

Use the package manager [pip](https://pip.pypa.io/en/stable/) to install the Reddit API (praw) and Cryptography.

```bash
pip install praw
```

```bash
pip install cryptography
```

## Usage

### Defining Acronyms
1. Reply to a post on subreddit r/IncorrectAcronym with an acronym that is not in the English dictionary
2. Run the Bot.py script

![Defining](https://i.imgur.com/7wKiuKml.png)

### Custom Dictionary
1. Reply to a post with the format of: !Suggest ACRONYM DEFINITION
2. Run the Bot.py script

![Suggest function & Defining](https://i.imgur.com/ZgUdEr4l.png)

## Support

If there are any issues with this bot, please feel free to contact me at: cameron.lau@sjsu.edu!
