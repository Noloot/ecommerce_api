from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy 
from flask_marshmallow import Marshmallow
from sqlalchemy.orm import DeclarativeBase, relationship, Mapped, mapped_column
from sqlalchemy import ForeignKey, Table, Column, String, select, delete
from marshmallow import ValidationError, fields
from typing import List, Optional
from datetime import date

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+mysqlconnector://root:@localhost/ecommerce_api'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

class Base(DeclarativeBase):
    pass

db = SQLAlchemy(model_class=Base)
db.init_app(app)
ma = Marshmallow(app)

class Customer(Base):
    
    __tablename__ = 'Customer'
    
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(db.String(225), nullable=False)
    email: Mapped[str] = mapped_column(db.String(225))
    address: Mapped[str] = mapped_column(db.String(225), unique=True)
    orders: Mapped[List["Orders"]] = db.relationship(back_populates='customer')
    
order_products = db.Table(
    "Order_Products",
    Base.metadata,
    db.Column('order_id', db.ForeignKey('orders.id')),
    db.Column('product_id', db.ForeignKey('products.id'))
)

class Orders(Base):
    __tablename__ = 'orders'
    
    id: Mapped[int] = mapped_column(primary_key=True)
    order_date: Mapped[date] = mapped_column(db.Date, nullable=False)
    customer_id: Mapped[int] = mapped_column(db.ForeignKey('Customer.id'))
    customer: Mapped['Customer'] = db.relationship(back_populates='orders')
    products: Mapped[List['Products']] = db.relationship(secondary=order_products, back_populates="orders")
    
class Products(Base):
    __tablename__ = 'products'
    
    id: Mapped[int] = mapped_column(primary_key=True)
    product_name: Mapped[str] = mapped_column(db.String(255), nullable=False)
    price: Mapped[float] = mapped_column(db.Float, nullable=False)
    orders: Mapped[List['Orders']] = db.relationship(secondary=order_products, back_populates="products")
    
    
class CustomerSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Customer
        
class ProductSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Products
        
class OrderSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Orders
        include_fk = True
        
customer_schema = CustomerSchema()
customers_schema = CustomerSchema(many=True)

product_schema = ProductSchema()
products_schema = ProductSchema(many=True)

order_schema = OrderSchema()
orders_schema = OrderSchema(many=True)

@app.route('/')
def home():
    return "Home"

# ! This is the customer section

@app.route("/customers", methods=['GET'])
def get_customers():
    
    page = int(request.args.get('page', 1))
    limit = int(request.args.get('limit', 10))
    offset = (page - 1) * limit
    
    query = select(Customer).offset(offset).limit(limit)
    result = db.session.execute(query).scalars().all()
    
    return customers_schema.jsonify(result)

@app.route("/customers/<int:id>", methods=['GET'])
def get_customer(id):
    query = select(Customer).where(Customer.id == id)
    result = db.session.execute(query).scalars().first()
    
    if result is None:
        return jsonify({"Error": "Customer not found"}),404
    
    return customer_schema.jsonify(result)

@app.route("/customers", methods=['POST'])
def add_customer():
    try:
        customer_data = customer_schema.load(request.json)
    except ValidationError as e: 
        return jsonify(e.messages),400
    
    new_customer = Customer(name=customer_data['name'], email=customer_data['email'], address=customer_data['address'])
    db.session.add(new_customer)
    db.session.commit()
    
    return jsonify({"Message": "New Customer added successfully!", 
                    "customer": customer_schema.dump(new_customer)}), 201
    
@app.route('/customers/<int:id>', methods=['PUT'])
def update_customer(id):
    customer = db.session.get(Customer, id)
    
    if not customer:
        return jsonify({"message": "Invalid customer id"}),400
    
    try:
        customer_data = customer_schema.load(request.json)
    except ValidationError as e:
        return jsonify(e.messages),400
    
    customer.name = customer_data['name']
    customer.email = customer_data['email']
    customer.address = customer_data['address']
    
    db.session.commit()
    return customer_schema.jsonify(customer),200

@app.route('/customers/<int:id>', methods=['DELETE'])
def delete_customer(id):
    customer = db.session.get(Customer, id)
    
    if not customer:
        return jsonify({"message": "Invalid customer id"}), 400
    
    db.session.delete(customer)
    db.session.commit()
    return jsonify({"message": f"successfully deleted customer {id}"}),200


# ! This is the products section

    
@app.route('/products', methods=['GET'])
def get_products():
    
    page = int(request.args.get('page', 1))
    limit = int(request.args.get('limit', 10))
    offset = (page - 1) * 1
    
    query = select(Products).offset(offset).limit(limit)
    result = db.session.execute(query).scalars().all()
    
    return products_schema.jsonify(result),200

@app.route("/products/<int:id>", methods=['GET'])
def get_product(id):
    query = select(Products).where(Products.id == id)
    result = db.session.execute(query).scalars().first()
    
    if result is None:
        return jsonify({"Error": "Customer not found"}),404
    
    return product_schema.jsonify(result)

@app.route('/products', methods=['POST'])
def create_product():
    try:
        product_data = product_schema.load(request.json)
    except ValidationError as e:
        return jsonify(e.messages),400
    
    new_product = Products(product_name=product_data['product_name'], price=product_data['price'])
    db.session.add(new_product)
    db.session.commit()
    
    return jsonify({"Message": "New Product added",
                    "product": product_schema.dump(new_product)}), 201

@app.route('/products/<int:id>', methods=['PUT'])
def update_product(id):
    product = db.session.get(Products, id)
    
    if not product:
        return jsonify({"message": "Invalid customer id"}),400
    
    try:
        product_data = product_schema.load(request.json)
    except ValidationError as e:
        return jsonify(e.messages),400
    
    product.product_name = product_data['name']
    product.price = product_data['price']
    
    db.session.commit()
    return ProductSchema.jsonify(product),200

@app.route('/products/<int:id>', methods=['DELETE'])
def delete_product(id):
    product = db.session.get(Products, id)
    
    if not product:
        return jsonify({"message": "Invalid customer id"}), 400
    
    db.session.delete(product)
    db.session.commit()
    return jsonify({"message": f"successfully deleted product {id}"}),200

# ! This is the order section

@app.route('/orders', methods=['POST'])
def add_order():
    try:
        order_data = order_schema.load(request.json)
    except ValidationError as e:
        return jsonify(e.messages),400
    
    customer = db.session.get(Customer, order_data['customer_id'])
    
    if customer:
        new_order = Orders(order_date=order_data['order_date'], customer_id = order_data['customer_id'])
        
        db.session.add(new_order)
        db.session.commit()
        
        return jsonify({"Message": "New Order Placed!", 
                        "order": order_schema.dump(new_order)}),201
    else:
        return jsonify({"message": "Invalid customer id"}), 400
    
@app.route('/orders/<int:order_id>/add_product/<int:product_id>', methods=['PUT'])
def add_product(order_id, product_id):
    order = db.session.get(Orders, order_id)
    product = db.session.get(Products, product_id)
    
    if order and product:
        if product not in order.products:
            order.products.append(product)
            db.session.commit()
            return jsonify({"Message": "Successfully added item to order."}),200
        else:
            return jsonify({"Message": "Item is already in this order."}),400
    else:
        return jsonify({"Message": "Invalid order id or product id."}),400
    
@app.route('/orders/<int:order_id>', methods=['PUT'])
def update_order(order_id):
    order = db.session.get(Orders, order_id)
    
    if not order:
        return jsonify({"message": "Order not found"}),404
    
    data = request.json
    
    if 'order_date' in data:
        try:
            order.order_date = date.fromisoformat(data['order_date'])
        except ValueError:
            return jsonify({"message": "Invalid date format. Use YYYY-MM-DD"}),400
        
    if 'customer_id' in data:
        new_customer = db.session.get(Customer, data['customer_id'])
        if not new_customer:
            return jsonify({"message", "New customer ID is invalid"}),400
        order.customer_id = data['customer_id']
        
    db.session.commit()
    
    return jsonify({
        "message": f"Order {order_id} updated successfully",
        "order": order_schema.dump(order)
    }),200
    
@app.route('/orders/<int:order_id>/remove_product/<int:product_id>', methods=['DELETE'])
def remove_order(order_id, product_id):
    order = db.session.get(Orders, order_id)
    product = db.session.get(Products, product_id)
    
    if not order or not product:
        return jsonify({"message": "Invalid order or product ID"}),400
    
    if product in order.products:
        order.products.remove(product)
        db.session.commit()
        return jsonify({"message": "Product order removed from order"}), 200
    else:
        return jsonify({"message": "Product not found in order"}), 404
    
@app.route('/customers/<int:customer_id>/orders', methods=['GET'])
def customer_oders(customer_id):
    query = select(Orders).where(Orders.customer_id == customer_id)
    orders = db.session.execute(query).scalars().all()
    
    return orders_schema.jsonify(orders),200

@app.route('/orders/<int:order_id>/products', methods=['GET'])
def product_orders(order_id):
    order = db.session.get(Orders, order_id)
    
    if not order:
        return jsonify({"message": "Order not found"}),404
    
    return products_schema.jsonify(order.products),200

@app.route('/orders', methods=['GET'])
def customers_orders():
    query = select(Orders)
    orders = db.session.execute(query).scalars().all()
    
    return orders_schema.jsonify(orders),200

if __name__ == '__main__':
    print(app.url_map)
    
    with app.app_context():
        
        db.create_all()
        
    app.run(debug=True)