from pydantic import BaseModel
from typing import List

# Define models
class MenuItem(BaseModel):
    name: str
    description: str
    price: float
    category: str

class OrderItem(BaseModel):
    menu_item_id: str
    quantity: int

class Order(BaseModel):
    table_id: str
    items: List[OrderItem]
    status: str = "pending"

class Table(BaseModel):
    table_number: int
    seats: int
