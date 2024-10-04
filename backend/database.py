import motor.motor_asyncio

# MongoDB connection string
MONGO_DETAILS = 'mongodb+srv://pythonjourney:Hitechminds2024@clusterhm.ace4m.mongodb.net/restaurant_db?retryWrites=true&w=majority&tls=true&tlsAllowInvalidCertificates=true'

# Create an asynchronous MongoDB client
client = motor.motor_asyncio.AsyncIOMotorClient(MONGO_DETAILS)

# Connect to the database
db = client["restaurant_db"]

# Define the collections
menu_collection = db["menu"]
orders_collection = db["orders"]
tables_collection = db["tables"]
