from faker import Faker
import pandas as pd
import random
from pathlib import Path

# =====================================================
# Configuration
# =====================================================

fake = Faker()

Faker.seed(42)
random.seed(42)

NUM_CUSTOMERS = 1000
NUM_PRODUCTS = 200
NUM_ORDERS = 5000

OUTPUT_DIR = Path(__file__).resolve().parent.parent / "data" / "raw"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


# =====================================================
# Generate Customers
# =====================================================

def generate_customers():

    customers = []

    for customer_id in range(1, NUM_CUSTOMERS + 1):

        customers.append({
            "customer_id": customer_id,
            "first_name": fake.first_name(),
            "last_name": fake.last_name(),
            "email": fake.unique.email(),
            "phone": fake.phone_number(),
            "city": fake.city(),
            "country": fake.country(),
            "signup_date": fake.date_between(
                start_date="-3y",
                end_date="today"
            )
        })

    customers_df = pd.DataFrame(customers)

    customers_df.to_csv(
        OUTPUT_DIR / "customers.csv",
        index=False
    )

    print("✅ customers.csv generated")

    return customers_df


# =====================================================
# Generate Products
# =====================================================

def generate_products():

    categories = [
        "Electronics",
        "Home",
        "Fashion",
        "Sports",
        "Beauty",
        "Books",
        "Toys"
    ]

    brands = [
        "Apple",
        "Samsung",
        "Sony",
        "Dell",
        "HP",
        "Lenovo",
        "Nike",
        "Adidas",
        "Logitech",
        "Philips"
    ]

    product_names = [
        "Laptop",
        "Keyboard",
        "Mouse",
        "Monitor",
        "Headphones",
        "Shoes",
        "Coffee Maker",
        "Smart Watch",
        "Desk",
        "Phone",
        "Tablet",
        "Backpack",
        "Camera",
        "Book",
        "Speaker"
    ]

    products = []

    for product_id in range(1, NUM_PRODUCTS + 1):

        brand = random.choice(brands)

        products.append({

            "product_id": product_id,

            "product_name": f"{brand} {random.choice(product_names)}",

            "category": random.choice(categories),

            "brand": brand,

            "price": round(random.uniform(10, 1500), 2),

            "stock": random.randint(5, 500)

        })

    products_df = pd.DataFrame(products)

    products_df.to_csv(
        OUTPUT_DIR / "products.csv",
        index=False
    )

    print("✅ products.csv generated")

    return products_df


# =====================================================
# Generate Orders
# =====================================================

def generate_orders():

    statuses = [
        "Pending",
        "Processing",
        "Shipped",
        "Delivered",
        "Cancelled"
    ]

    payment_methods = [
        "Credit Card",
        "Debit Card",
        "PayPal",
        "Apple Pay",
        "Google Pay"
    ]

    orders = []

    for order_id in range(1, NUM_ORDERS + 1):

        orders.append({

            "order_id": order_id,

            "customer_id": random.randint(1, NUM_CUSTOMERS),

            "order_date": fake.date_between(
                start_date="-2y",
                end_date="today"
            ),

            "status": random.choice(statuses),

            "payment_method": random.choice(payment_methods)

        })

    orders_df = pd.DataFrame(orders)

    orders_df.to_csv(
        OUTPUT_DIR / "orders.csv",
        index=False
    )

    print("✅ orders.csv generated")

    return orders_df

# =====================================================
# Generate Order Items
# =====================================================

def generate_order_items(products_df):

    order_items = []
    order_item_id = 1

    # Create a lookup dictionary for product prices
    product_prices = (
        products_df
        .set_index("product_id")["price"]
        .to_dict()
    )

    for order_id in range(1, NUM_ORDERS + 1):

        # Each order contains between 1 and 5 products
        num_items = random.randint(1, 5)

        selected_products = random.sample(
            range(1, NUM_PRODUCTS + 1),
            num_items
        )

        for product_id in selected_products:

            quantity = random.randint(1, 4)

            unit_price = product_prices[product_id]

            discount = random.choice([0, 5, 10, 15, 20])

            line_total = round(
                quantity *
                unit_price *
                (1 - discount / 100),
                2
            )

            order_items.append({

                "order_item_id": order_item_id,

                "order_id": order_id,

                "product_id": product_id,

                "quantity": quantity,

                "unit_price": unit_price,

                "discount_percent": discount,

                "line_total": line_total

            })

            order_item_id += 1

    order_items_df = pd.DataFrame(order_items)

    order_items_df.to_csv(
        OUTPUT_DIR / "order_items.csv",
        index=False
    )

    print("✅ order_items.csv generated")

    return order_items_df


# =====================================================
# Main
# =====================================================
def main():

    print("\nGenerating datasets...\n")

    customers_df = generate_customers()

    products_df = generate_products()

    orders_df = generate_orders()

    order_items_df = generate_order_items(products_df)

    print("\nDataset Summary")
    print("----------------------------")
    print(f"Customers   : {len(customers_df):,}")
    print(f"Products    : {len(products_df):,}")
    print(f"Orders      : {len(orders_df):,}")
    print(f"Order Items : {len(order_items_df):,}")

    print("\n🎉 All datasets generated successfully!")
    print(f"\nLocation: {OUTPUT_DIR}")


if __name__ == "__main__":
    main()