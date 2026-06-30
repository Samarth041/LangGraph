import json
import os

FILE_NAME="chat_ids.json"

def load_chat_ids():
    if os.path.exists(FILE_NAME):
        with open(FILE_NAME,"r") as f:
            return json.load(f)
        
    return []


def save_chat_ids(chat_ids):
    with open(FILE_NAME,'w') as f:
        json.dump(chat_ids,f)