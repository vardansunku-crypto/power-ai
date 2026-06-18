import random
from datetime import datetime, timedelta
from faker import Faker
import mysql.connector

fake = Faker("en_IN")

DB_HOST = "localhost"
DB_USER = "root"
DB_PASSWORD = "995910"   # change this
DB_NAME = "sales_db"

CUSTOMERS = 1000
PRODUCTS = 200
ORDERS = 10000
MAX_ITEMS_PER_ORDER = 5


def connect_mysql(database=None):
    return mysql.connector.connect(
        host=DB_HOST,
        user=DB_USER,
        password=DB_PASSWORD,
        database=database
    )


def create_database():
    conn = connect_mysql()
    cur = conn.cursor()
    cur.execute(f"CREATE DATABASE IF NOT EXISTS {DB_NAME}")
    conn.commit()
    cur.close()
    conn.close()


def create_tables():
    conn = connect_mysql(DB_NAME)
    cur = conn.cursor()

    cur.execute("""
    CREATE TABLE IF NOT EXISTS customers (
        customer_id INT PRIMARY KEY AUTO_INCREMENT,
        customer_name VARCHAR(100),
        email VARCHAR(100),
        phone VARCHAR(20),
        city VARCHAR(50),
        state VARCHAR(50),
        created_at DATE
    )
    """)

    cur.execute("""
    CREATE TABLE IF NOT EXISTS products (
        product_id INT PRIMARY KEY AUTO_INCREMENT,
        product_name VARCHAR(100),
        category VARCHAR(50),
        cost_price DECIMAL(10,2),
        selling_price DECIMAL(10,2),
        stock_quantity INT
    )
    """)

    cur.execute("""
    CREATE TABLE IF NOT EXISTS orders (
        order_id INT PRIMARY KEY AUTO_INCREMENT,
        customer_id INT,
        order_date DATE,
        payment_method VARCHAR(30),
        order_status VARCHAR(30),
        FOREIGN KEY (customer_id) REFERENCES customers(customer_id)
    )
    """)

    cur.execute("""
    CREATE TABLE IF NOT EXISTS order_items (
        item_id INT PRIMARY KEY AUTO_INCREMENT,
        order_id INT,
        product_id INT,
        quantity INT,
        unit_price DECIMAL(10,2),
        total_amount DECIMAL(10,2),
        profit DECIMAL(10,2),
        FOREIGN KEY (order_id) REFERENCES orders(order_id),
        FOREIGN KEY (product_id) REFERENCES products(product_id)
    )
    """)

    conn.commit()
    cur.close()
    conn.close()


def clear_old_data():
    conn = connect_mysql(DB_NAME)
    cur = conn.cursor()

    cur.execute("SET FOREIGN_KEY_CHECKS = 0")
    cur.execute("TRUNCATE TABLE order_items")
    cur.execute("TRUNCATE TABLE orders")
    cur.execute("TRUNCATE TABLE products")
    cur.execute("TRUNCATE TABLE customers")
    cur.execute("SET FOREIGN_KEY_CHECKS = 1")

    conn.commit()
    cur.close()
    conn.close()


def insert_customers():
    states = ["Telangana", "Andhra Pradesh", "Karnataka", "Tamil Nadu", "Maharashtra"]
    cities = ["Hyderabad", "Warangal", "Karimnagar", "Bangalore", "Chennai", "Mumbai", "Vijayawada"]

    conn = connect_mysql(DB_NAME)
    cur = conn.cursor()

    for _ in range(CUSTOMERS):
        cur.execute("""
        INSERT INTO customers 
        (customer_name, email, phone, city, state, created_at)
        VALUES (%s, %s, %s, %s, %s, %s)
        """, (
            fake.name(),
            fake.email(),
            fake.phone_number()[:20],
            random.choice(cities),
            random.choice(states),
            fake.date_between(start_date="-2y", end_date="today")
        ))

    conn.commit()
    cur.close()
    conn.close()


def insert_products():
    categories = ["Electronics", "Fashion", "Grocery", "Home Appliances", "Mobiles", "Beauty", "Sports"]

    conn = connect_mysql(DB_NAME)
    cur = conn.cursor()

    for i in range(PRODUCTS):
        cost_price = round(random.uniform(100, 10000), 2)
        selling_price = round(cost_price * random.uniform(1.10, 1.80), 2)

        cur.execute("""
        INSERT INTO products
        (product_name, category, cost_price, selling_price, stock_quantity)
        VALUES (%s, %s, %s, %s, %s)
        """, (
            f"{random.choice(categories)} Product {i+1}",
            random.choice(categories),
            cost_price,
            selling_price,
            random.randint(10, 1000)
        ))

    conn.commit()
    cur.close()
    conn.close()


def insert_orders_and_items():
    payment_methods = ["UPI", "Cash", "Card", "Net Banking"]
    statuses = ["Completed", "Completed", "Completed", "Cancelled", "Returned"]

    conn = connect_mysql(DB_NAME)
    cur = conn.cursor()

    for _ in range(ORDERS):
        customer_id = random.randint(1, CUSTOMERS)
        order_date = fake.date_between(start_date="-2y", end_date="today")
        payment_method = random.choice(payment_methods)
        order_status = random.choice(statuses)

        cur.execute("""
        INSERT INTO orders
        (customer_id, order_date, payment_method, order_status)
        VALUES (%s, %s, %s, %s)
        """, (
            customer_id,
            order_date,
            payment_method,
            order_status
        ))

        order_id = cur.lastrowid

        items_count = random.randint(1, MAX_ITEMS_PER_ORDER)

        for _ in range(items_count):
            product_id = random.randint(1, PRODUCTS)

            cur.execute("""
            SELECT cost_price, selling_price 
            FROM products 
            WHERE product_id = %s
            """, (product_id,))

            cost_price, selling_price = cur.fetchone()

            quantity = random.randint(1, 5)
            total_amount = round(float(selling_price) * quantity, 2)
            profit = round((float(selling_price) - float(cost_price)) * quantity, 2)

            cur.execute("""
            INSERT INTO order_items
            (order_id, product_id, quantity, unit_price, total_amount, profit)
            VALUES (%s, %s, %s, %s, %s, %s)
            """, (
                order_id,
                product_id,
                quantity,
                selling_price,
                total_amount,
                profit
            ))

    conn.commit()
    cur.close()
    conn.close()


def main():
    print("Creating database...")
    create_database()

    print("Creating tables...")
    create_tables()

    print("Clearing old data...")
    clear_old_data()

    print("Inserting customers...")
    insert_customers()

    print("Inserting products...")
    insert_products()

    print("Inserting orders and order items...")
    insert_orders_and_items()

    print("Done! Big test data created successfully.")
    print(f"Database: {DB_NAME}")
    print(f"Customers: {CUSTOMERS}")
    print(f"Products: {PRODUCTS}")
    print(f"Orders: {ORDERS}")


if __name__ == "__main__":
    main()