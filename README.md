
# 🛒 E-commerce API with Flask, SQLAlchemy, and Marshmallow

This project is a RESTful API for an e-commerce platform built using Flask, SQLAlchemy, and Marshmallow. It manages Customers, Products, and Orders, including many-to-many relationships between Orders and Products.

---

## 🚀 Features

- Full CRUD operations for:
  - Customers
  - Products
  - Orders
- Associate multiple products with orders
- View orders for a customer
- View products in an order
- Pagination for product and customer listings
- Order updates and deletions

---

## 📦 Tech Stack

- Python 3.13
- Flask
- Flask-SQLAlchemy
- Marshmallow
- MySQL Connector
- MySQL (Database)

---

## 🔧 Setup Instructions

1. **Clone the repository**

```bash
git clone https://github.com/yourusername/ecommerce-api.git
cd ecommerce-api
```

2. **Create virtual environment and activate it**

```bash
python3 -m venv venv
source venv/bin/activate  # macOS/Linux
venv\Scripts\activate   # Windows
```

3. **Install dependencies**

```bash
pip install -r requirements.txt
```

4. **Configure MySQL**

Ensure you have a MySQL database created. Update the following line in `app.py`:

```python
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+mysqlconnector://root:YOUR_PASSWORD@localhost/ecommerce_api'
```

5. **Run the app**

```bash
python app.py
```

Visit `http://127.0.0.1:5000` to start using the API.

---

## 🧪 Example Endpoints

- `GET /customers?page=1&limit=10`
- `POST /products` with JSON body:
```json
{
  "product_name": "Laptop",
  "price": 999.99
}
```
- `PUT /orders/1` to update an order's date or customer
- `GET /orders/1/products` to view all products in an order

---

## 📌 Notes

- Dates must be passed in `YYYY-MM-DD` format.
- Use Postman or curl to test endpoints.
- Ensure the MySQL service is running before starting the app.

---

## 🙌 Contributing

Feel free to fork the repo and submit pull requests. All improvements are welcome!

