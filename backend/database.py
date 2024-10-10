import motor.motor_asyncio

# MongoDB connection string

MONGO_DETAILS = ''

# Create an asynchronous MongoDB client
client = motor.motor_asyncio.AsyncIOMotorClient(MONGO_DETAILS)

# Connect to the database
db = client["restaurant_db"]

# Define the collections
menu_collection = db["menu_collection"]
orders_collection = db["orders"]
tables_collection = db["tables"]
