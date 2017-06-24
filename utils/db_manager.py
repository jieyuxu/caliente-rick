import pymongo
import datetime
import uuid

server = MongoClient()
db = server["rick"]

def get_time():
    return datetime.datetime.utcnow()

def get_user(email):
    return db.users.find_one({"email" : email})

# user_info: dictionary
# {"email" : "example@gmail.com",
#  "first_name" : "Ex",
#  "last_name" : "Ample"}
#  "password" : "a38jg38vno83oour"
#  "type" : "donor" // "director"
# }
def add_user(user_info):
    db.users.insert_one(user_info)

def get_shelter(shelter_id):
    return db.shelters.find_one({"id" : shelter_id})

# shelter_info: dictionary
# {"name" : "Example Shelter",
#  "description" : "We are a shelter",
#  "id" : 12345,
#  "address_zip_code" : "10282",
#  "address_state" : "NY",
#  "address_city" : "New York"
#  "address_street" : "345 Chambers St.",
#  "phone number" : "2123123800"
#  "directors" : ["dir1@gmail.com", "dir2@gmail.com"],   //email of users
#  "population" : 50,
#  "needs" : {"tampons" : 50,
#             "pads" : 25,
#             "diapers" : 10}
#  "last_updated" : 2017-06-24 12:55     //datetime object
# }
def add_shelter(shelter_info):
    shelter_info["last_updated"] = get_time()
    shelter_info["id"] = uuid.uuid4().int
    db.shelters.insert_one(shelter_info)

def set_shelter_data(shelter_id, field, value):
    db.shelters.update_one({"id" : shelter_id}, {"$set" : {field : value}})
    db.shelters.update_one({"id" : shelter_id}, {"$set" : {"last_updated" : get_time()}})

def authenticate_user(email, hashed_input):
    user = get_user(email)
    if user == None:
        #login failed, does nsetot exist
        return False, "no such user"
    hashed_pw = user["password"]
    if hashed_input == hashed_pw:
        return True, "success"
    else:
        return False, "incorrect password"

def register_user(user_info):
    if db.users.find_one({"email" : user_info["email"]}) != None:
        return False, "account already exists"
    add_user(user_info)
    return True, "success"
