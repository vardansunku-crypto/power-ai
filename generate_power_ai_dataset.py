import random
from datetime import datetime, timedelta
from pathlib import Path

import pandas as pd
from faker import Faker

fake = Faker("en_IN")

OUTPUT_DIR = Path("power_ai_test_data")
OUTPUT_DIR.mkdir(exist_ok=True)

CUSTOMERS = 5000
PRODUCTS = 500
ORDERS = 50000
MAX_ITEMS_PER_ORDER = 5

states_cities = {
    "Telangana": ["Hyderabad", "Warangal", "Karimnagar", "Nizamabad"],
    "Andhra Pradesh": ["Vijayawada", "Visakhapatnam", "Guntur", "Tirupati"],
    "Karnataka": ["Bangalore", "Mysore", "Hubli", "Mangalore"],
    "Tamil Nadu": ["Chennai", "Coimbatore", "Madurai", "Salem"],
    "Maharashtra": ["Mumbai", "Pune", "Nagpur", "Nashik"],
}

categories = [
    "Electronics", "Fashion", "Grocery", "Mobiles", "Beauty",
    "Sports", "Home Appliances", "Furniture", "Books", "Toys"
]

payment_methods = ["UPI", "Cash", "Card", "Net Banking"]
order_statuses = ["Completed", "Completed", "Completed", "Cancelled", "Returned"]


def random_date(days_back=1095):
    return datetime.today() - timedelta(days=random.randint(0, days_back))


def generate_customers():
    rows = []

    for customer_id in range(1, CUSTOMERS + 1):
        state = random.choice(list(states_cities.keys()))
        city = random.choice(states_cities[state])

        rows.append({
            "customer_id": customer_id,
            "customer_name": fake.name(),
            "email": fake.email(),
            "phone": fake.phone_number()[:20],
            "city": city,
            "state": state,
            "created_at": random_date().date()
        })

    return pd.DataFrame(rows)


def generate_products():
    rows = []

    for product_id in range(1, PRODUCTS + 1):
        category = random.choice(categories)
        cost_price = round(random.uniform(100, 10000), 2)
        selling_price = round(cost_price * random.uniform(1.10, 1.80), 2)

        rows.append({
            "product_id": product_id,
            "product_name": f"{category} Product {product_id}",
            "category": category,
            "cost_price": cost_price,
            "selling_price": selling_price,
            "stock_quantity": random.randint(10, 1000)
        })

    return pd.DataFrame(rows)


def generate_orders_and_sales(products_df):
    orders = []
    sales = []

    for order_id in range(1, ORDERS + 1):
        customer_id = random.randint(1, CUSTOMERS)
        order_date = random_date().date()
        payment_method = random.choice(payment_methods)
        order_status = random.choice(order_statuses)

        orders.append({
            "order_id": order_id,
            "customer_id": customer_id,
            "order_date": order_date,
            "payment_method": payment_method,
            "order_status": order_status
        })

        item_count = random.randint(1, MAX_ITEMS_PER_ORDER)

        for _ in range(item_count):
            product = products_df.sample(1).iloc[0]

            quantity = random.randint(1, 5)
            unit_price = float(product["selling_price"])
            cost_price = float(product["cost_price"])

            total_amount = round(unit_price * quantity, 2)
            profit = round((unit_price - cost_price) * quantity, 2)

            sales.append({
                "order_id": order_id,
                "customer_id": customer_id,
                "product_id": int(product["product_id"]),
                "product_name": product["product_name"],
                "category": product["category"],
                "quantity": quantity,
                "unit_price": unit_price,
                "total_amount": total_amount,
                "profit": profit,
                "order_date": order_date,
                "payment_method": payment_method,
                "order_status": order_status
            })

    return pd.DataFrame(orders), pd.DataFrame(sales)


def create_dirty_file(sales_df):
    dirty_df = sales_df.copy()

    dirty_df["Unnamed: 0"] = range(len(dirty_df))
    dirty_df["empty_column"] = ""

    dirty_df.loc[dirty_df.sample(frac=0.02).index, "profit"] = None
    dirty_df.loc[dirty_df.sample(frac=0.02).index, "category"] = None
    dirty_df.loc[dirty_df.sample(frac=0.01).index, "total_amount"] = None

    duplicate_rows = dirty_df.sample(100)
    dirty_df = pd.concat([dirty_df, duplicate_rows], ignore_index=True)

    return dirty_df


def main():
    print("Generating customers...")
    customers_df = generate_customers()

    print("Generating products...")
    products_df = generate_products()

    print("Generating orders and sales...")
    orders_df, sales_df = generate_orders_and_sales(products_df)

    print("Creating integrated file...")
    sales_integrated_df = (
        sales_df
        .merge(customers_df[["customer_id", "customer_name", "city", "state"]], on="customer_id", how="left")
    )

    print("Creating dirty testing file...")
    dirty_sales_df = create_dirty_file(sales_integrated_df)

    print("Saving files...")

    customers_df.to_csv(OUTPUT_DIR / "customers.csv", index=False)
    products_df.to_csv(OUTPUT_DIR / "products.csv", index=False)
    orders_df.to_csv(OUTPUT_DIR / "orders.csv", index=False)
    sales_df.to_csv(OUTPUT_DIR / "sales.csv", index=False)
    sales_integrated_df.to_csv(OUTPUT_DIR / "sales_integrated.csv", index=False)
    dirty_sales_df.to_csv(OUTPUT_DIR / "dirty_sales_test.csv", index=False)

    with pd.ExcelWriter(OUTPUT_DIR / "power_ai_sales_excel_test.xlsx") as writer:
        customers_df.to_excel(writer, sheet_name="customers", index=False)
        products_df.to_excel(writer, sheet_name="products", index=False)
        orders_df.to_excel(writer, sheet_name="orders", index=False)
        sales_integrated_df.to_excel(writer, sheet_name="sales", index=False)

    print("Done!")
    print(f"Files saved in folder: {OUTPUT_DIR.resolve()}")
    print("Generated files:")
    print("- customers.csv")
    print("- products.csv")
    print("- orders.csv")
    print("- sales.csv")
    print("- sales_integrated.csv")
    print("- dirty_sales_test.csv")
    print("- power_ai_sales_excel_test.xlsx")


if __name__ == "__main__":
    main()