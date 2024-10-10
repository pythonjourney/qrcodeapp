from fastapi import FastAPI, HTTPException
from model import Order, OrderItem, Table
from database import menu_collection, orders_collection, tables_collection
from bson import ObjectId
import logging
import qrcode
from fastapi.responses import StreamingResponse
from io import BytesIO

# Configure logging
logging.basicConfig(level=logging.INFO)

app = FastAPI()

from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods (GET, POST, etc.)
    allow_headers=["*"],  # Allows all headers
)


# QR Code Generation Endpoint
@app.get("/generate_qr/{table_id}")
async def generate_qr(table_id: str):
    # Data to encode in the QR code (this could be a table ID or a URL pointing to the table)
    data = f"http://localhost:3000/table/{table_id}"  # This could be the link where table info can be fetched

    # Generate QR code
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    qr.add_data(data)
    qr.make(fit=True)

    img = qr.make_image(fill='black', back_color='white')

    # Convert the image to a byte stream
    img_io = BytesIO()
    img.save(img_io, 'PNG')
    img_io.seek(0)

    return StreamingResponse(img_io, media_type="image/png")

@app.get("/table/{table_id}")
async def get_table_info(table_id: str):
    table = await tables_collection.find_one({"_id": ObjectId(table_id)})
    if table:
        return table
    raise HTTPException(status_code=404, detail="Table not found")



# GET route to fetch the menu
@app.get("/menu")
async def get_menu():
    try:
        # Fetch all the menu items from the menu collection
        menu_items = await menu_collection.find().to_list(100)  # Fetch up to 100 items
        # Convert ObjectId to string for each menu item
        for item in menu_items:
            item["_id"] = str(item["_id"])
        return menu_items

    except Exception as e:
        logging.error(f"Failed to fetch menu: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to fetch menu")


# POST route to create a new table
@app.post("/table")
async def create_table(table: Table):
    try:
        # Insert the new table into the tables collection
        table_dict = table.dict()
        result = await tables_collection.insert_one(table_dict)
        return {"message": "Table created successfully", "table_id": str(result.inserted_id)}

    except Exception as e:
        logging.error(f"Failed to create table: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

# GET route to retrieve an order by order_id
@app.get("/order/{order_id}")
async def get_order(order_id: str):
    try:
        # Convert order_id to ObjectId
        order_object_id = ObjectId(order_id)

        # Fetch the order from the orders collection
        order = await orders_collection.find_one({"_id": order_object_id})
        if not order:
            raise HTTPException(status_code=404, detail="Order not found")

        # Convert ObjectId to string
        order["_id"] = str(order["_id"])

        return order

    except Exception as e:
        logging.error(f"Failed to fetch order: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

# GET route to retrieve a table by table_id
@app.get("/table/{table_id}")
async def get_table(table_id: str):
    try:
        # Convert table_id to ObjectId
        table_object_id = ObjectId(table_id)

        # Fetch the table from the tables collection
        table = await tables_collection.find_one({"_id": table_object_id})
        if not table:
            raise HTTPException(status_code=404, detail="Table not found")

        # Convert ObjectId to string
        table["_id"] = str(table["_id"])

        return table

    except Exception as e:
        logging.error(f"Failed to fetch table: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

# POST route to place an order
@app.post("/order")
async def place_order(order: Order):
    try:
        logging.info(f"Received order: {order.dict()}")

        # Convert table_id to ObjectId
        try:
            table_id = ObjectId(order.table_id)
        except Exception:
            logging.warning(f"Invalid table_id format: {order.table_id}")
            raise HTTPException(status_code=400, detail="Invalid table_id format.")

        # Check if the table exists
        table = await tables_collection.find_one({"_id": table_id})
        if not table:
            logging.warning(f"Table with ID {order.table_id} not found.")
            raise HTTPException(status_code=404, detail="Table not found")

        # Prepare the order data
        order_dict = order.dict()
        order_dict["items"] = [item.dict() for item in order.items]

        # Insert the order into the orders collection
        result = await orders_collection.insert_one(order_dict)
        logging.info(f"Order placed successfully with ID: {str(result.inserted_id)}")

        return {"message": "Order placed successfully", "order_id": str(result.inserted_id)}

    except Exception as e:
        logging.error(f"Failed to place order: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
