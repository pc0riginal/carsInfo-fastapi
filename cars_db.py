from pymongo import MongoClient

client = MongoClient(
    "mongodb+srv://msm98:paras123@cluster0.4gnmc.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"
)

db = client["CarsDB"]

collection = db["cars"]
