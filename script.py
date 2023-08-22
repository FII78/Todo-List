### Importing necessary libraries

import configparser # pip install configparser
from telethon import TelegramClient, events # pip install telethon
from datetime import datetime
from pymongo import MongoClient # pip install pymongo[srv]
from bson.objectid import ObjectId # pip install bson
import certifi
### Initializing Configuration
print("Initializing configuration...")
config = configparser.ConfigParser()
config.read('config.ini')

# Read values for Telethon and set session name
API_ID = config.get('default','api_id') 
API_HASH = config.get('default','api_hash')
BOT_TOKEN = config.get('default','bot_token')
session_name = "sessions/Bot"

# Read values for Mongodb
USERNAME = config.get('default', 'username')
PASSWORD = config.get('default', 'password')
DATABASE_NAME = config.get('default', "db_name")
COLLECTION_NAME = config.get('default', "collection_name")

# Start the Client (telethon)
client = TelegramClient(session_name, API_ID, API_HASH).start(bot_token=BOT_TOKEN)



# Start the Client (MongoDB)
url = "mongodb+srv://"+USERNAME+":"+PASSWORD+"@todo.nufiovh.mongodb.net/?retryWrites=true&w=majority"
cluster = MongoClient(url, tlsCAFile=certifi.where())
 

### START COMMAND
@client.on(events.NewMessage(pattern="(?i)/start"))
async def start(event):
    # Get sender
    sender = await event.get_sender()
    SENDER = sender.id

    # send notification message
    text = """Hello there! Let's plan your day ahead 
    If you're new here, check out this tips to seemlessly use this bot: 
        1. To add a task simply type /insert [ Your task description] [D - if your task is Done | N - if you're Not done with the Task]
        2. To see all of your tasks type /select
        3. To update your task:
            -> First get the id of the task you want to update using the /select command
            -> Then type /update [The id of the task] [ Your task description] [D - if your task is Done | N - if you're Not done with the Task]
        4. To delete your task:
            -> First get the id of the task you want to update using the /select command
            -> Then type /delete [The id of the task you want to delete]"""
    await client.send_message(SENDER, text)


### Insert command
#/insert [task_name] [status]
@client.on(events.NewMessage(pattern="(?i)/insert"))
async def insert(event):
    # Get the sender of the message
    sender = await event.get_sender()
    SENDER = sender.id

    # Split the inserted text and create a List
    list_of_words = event.message.text.split(" ")

    task = " ".join(list_of_words[1:-1]) # the second (1) item is the task description
    status = list_of_words[-1] # the fourth (3) item is the status: "D" for Done, "N" for Not done
    dt_string = datetime.now().strftime("%d-%m-%y") # Use the datetime library to the get the date (and format it as DAY/MONTH/YEAR)
    post_dict = {"task_desc": task, "status": status, "LAST_UPDATE": dt_string}

    # Execute insert query
    todolist.insert_one(post_dict)
    
    # send notification message
    text = "Task correctly added!"
    await client.send_message(SENDER, text, parse_mode='html')
        

### SELECT COMMAND
# Print function
def create_message_select_query(ans):
    text = ""
    for res in ans:
        if(res != []):
            id = res["_id"]
            task = res["task_desc"]
            status = res["status"]
            if status == "N":
                status = "Not done"
            else:
                status = "Done"
            creation_date = res["LAST_UPDATE"]
            text += "<b>"+ str(id) +"</b> | " + "<b>"+ str(task) +"</b> | "  + "<b>"+ str(status) +"</b> | " + "<b>"+ str(creation_date)+"</b>\n"
    message = "<b>Received 📖 </b> Information about todo list:\n\n"+text
    return message


# Command
@client.on(events.NewMessage(pattern="(?i)/select"))
async def select(event):
    # Get the sender of the message
    sender = await event.get_sender()
    SENDER = sender.id

    # Split the inserted text and create a List
    list_of_words = event.message.text.split(" ")

    if(len(list_of_words) > 1):
        task = list_of_words[1] # the second (1) item is the task description

        # Execute find query
        results = todolist.find({"task_desc":task})

        # send notification message
        text = create_message_select_query(results)
        await client.send_message(SENDER, text, parse_mode='html')
        
    else:
        # Execute find query
        results = todolist.find({})

        # send notification message
        text = create_message_select_query(results)
        await client.send_message(SENDER, text, parse_mode='html')



### UPDATE COMMAND
# /update [_id] [new_task_desc] 
@client.on(events.NewMessage(pattern="(?i)/update"))
async def update(event):
    # Get the sender
    sender = await event.get_sender()
    SENDER = sender.id

    # Split the inserted text and create a List
    list_of_words = event.message.text.split(" ")

    _id = ObjectId(list_of_words[1]) # The second (1) item is the _id.  We must cast the string to ObjectId 

    task = " ".join(list_of_words[2:-1]) # the second (1) item is the task desc
    status = list_of_words[-1] # the fourth (3) item is the status: "D" for Done, "N" for Not done
    dt_string = datetime.now().strftime("%d-%m-%y") # Use the datetime library to the get the date (and format it as DAY/MONTH/YEAR)
    new_post_dict = {"task_desc": task, "status": status, "LAST_UPDATE": dt_string}
    
    # Execute update query
    todolist.update_one({"_id":_id}, {"$set": new_post_dict})

    # send notification message
    text = "Task with _id {} correctly updated".format(_id)
    await client.send_message(SENDER, text, parse_mode='html')


### DELETE COMMAND
@client.on(events.NewMessage(pattern="(?i)/delete"))
async def delete(event):

    # Get the sender
    sender = await event.get_sender()
    SENDER = sender.id

    # Split the inserted text and create a List
    list_of_words = event.message.text.split(" ")
    _id = ObjectId(list_of_words[1]) # The second (1) item is the _id. We must cast the string to ObjectId 

    # Execute delete query
    todolist.delete_one({"_id": _id})

    # send notification message
    text = "Task with _id {} correctly deleted".format(_id)
    await client.send_message(SENDER, text, parse_mode='html')




# Command

# /selectIn state D N
@client.on(events.NewMessage(pattern="(?i)/in"))
async def select(event):
    # Get the sender of the message
    sender = await event.get_sender()
    SENDER = sender.id

    # Split the inserted text and create a List
    list_of_words = event.message.text.split(" ")

    if(len(list_of_words) > 1):
        field = list_of_words[1] # the second (1) item is the task
        values_to_check = list_of_words[2:]
        
        params = {field: {"$in": values_to_check}}
        results = todolist.find(params)
        print(results)

        # send notification message
        text = create_message_select_query(results)
        await client.send_message(SENDER, text, parse_mode='html')







##### MAIN
if __name__ == '__main__':
    try:
        print("Initializing Database...")
        # Define the Database using Database name
        db = cluster[DATABASE_NAME]
        # Define collection
        todolist = db[COLLECTION_NAME]

        print("Bot Started...")
        client.run_until_disconnected()

    except Exception as error:
        print('Cause: {}'.format(error))