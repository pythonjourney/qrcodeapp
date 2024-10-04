
import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { QrReader } from 'react-qr-reader';

const API_URL = 'http://localhost:8000'; // Update this URL if your FastAPI server runs on a different port or domain.

const App = () => {
  const [menuItems, setMenuItems] = useState([]);
  const [cart, setCart] = useState([]);
  const [tableId, setTableId] = useState('');
  const [orderId, setOrderId] = useState(null);
  const [isScanning, setIsScanning] = useState(true);

  useEffect(() => {
    fetchMenu();
  }, []);

  const fetchMenu = async () => {
    try {
      const response = await axios.get(`${API_URL}/menu`);
      setMenuItems(response.data);
    } catch (error) {
      console.error("Error fetching menu:", error);
    }
  };

  const handleScan = (result) => {
    if (result) {
      setTableId(result?.text);
      setIsScanning(false);
    }
  };

  const handleError = (error) => {
    console.error("QR Reader Error:", error);
  };

  const addToCart = (item) => {
    const existingItem = cart.find(cartItem => cartItem._id === item._id);
    if (existingItem) {
      updateQuantity(item._id, existingItem.quantity + 1);
    } else {
      setCart([...cart, { ...item, quantity: 1 }]);
    }
  };

  const updateQuantity = (itemId, newQuantity) => {
    setCart(cart.map(item => 
      item._id === itemId ? { ...item, quantity: newQuantity } : item
    ));
  };

  const placeOrder = async () => {
    try {
      const orderItems = cart.map(item => ({
        menu_item_id: item._id,
        quantity: item.quantity
      }));

      const response = await axios.post(`${API_URL}/order`, {
        table_id: tableId,
        items: orderItems
      });

      setOrderId(response.data.order_id);
      setCart([]);
    } catch (error) {
      console.error("Error placing order:", error);
    }
  };

  if (isScanning) {
    return (
      <div className="container mx-auto p-4">
        <h1 className="text-2xl font-bold mb-4">Scan Table QR Code</h1>
        <QrReader
          delay={300}
          onError={handleError}
          onResult={handleScan}
          style={{ width: '100%' }}
        />
      </div>
    );
  }

  return (
    <div className="container mx-auto p-4">
      <h1 className="text-2xl font-bold mb-4">Restaurant Menu - Table {tableId}</h1>
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        {menuItems.map(item => (
          <div key={item._id} className="border p-4 rounded">
            <h2 className="text-xl font-semibold">{item.name}</h2>
            <p>{item.description}</p>
            <p className="font-bold">${item.price.toFixed(2)}</p>
            <button 
              onClick={() => addToCart(item)}
              className="mt-2 bg-blue-500 text-white px-4 py-2 rounded"
            >
              Add to Cart
            </button>
          </div>
        ))}
      </div>

      <div className="mt-8">
        <h2 className="text-2xl font-bold mb-4">Your Order</h2>
        {cart.map(item => (
          <div key={item._id} className="flex items-center justify-between mb-2">
            <span>{item.name} - ${item.price.toFixed(2)}</span>
            <input 
              type="number" 
              min="1" 
              value={item.quantity}
              onChange={(e) => updateQuantity(item._id, parseInt(e.target.value))}
              className="w-16 px-2 py-1 border rounded"
            />
          </div>
        ))}
        <button 
          onClick={placeOrder}
          className="mt-4 bg-green-500 text-white px-4 py-2 rounded"
          disabled={cart.length === 0}
        >
          Place Order
        </button>
      </div>

      {orderId && (
        <div className="mt-8">
          <h2 className="text-2xl font-bold mb-4">Order Placed!</h2>
          <p>Your order ID is: {orderId}</p>
          <p>Your order will be delivered to table {tableId}</p>
        </div>
      )}
    </div>
  );
};

export default App;

