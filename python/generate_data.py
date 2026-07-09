from faker import Faker
import pandas as pd
import random
import calendar
from datetime import date, datetime
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

START_ORDER_DATE = date(2023, 1, 1)
END_ORDER_DATE = datetime.now().date()
MONTH_SEASONAL_WEIGHTS = {
    1: 0.75,
    2: 1.00,
    3: 1.00,
    4: 1.00,
    5: 1.00,
    6: 1.00,
    7: 1.00,
    8: 1.00,
    9: 1.00,
    10: 1.10,
    11: 1.40,
    12: 1.60,
}

SIGNUP_START_DATE = date(2021, 1, 1)
SIGNUP_END_DATE = date(2022, 12, 31)


# =====================================================
# Generate Customers
# =====================================================

def generate_customers():

    customers = []

    for customer_id in range(1, NUM_CUSTOMERS + 1):
        signup_date = fake.date_between(
            start_date=SIGNUP_START_DATE,
            end_date=SIGNUP_END_DATE,
        )

        customers.append({
            "customer_id": customer_id,
            "first_name": fake.first_name(),
            "last_name": fake.last_name(),
            "email": fake.unique.email(),
            "phone": fake.phone_number(),
            "city": fake.city(),
            "country": fake.country(),
            "signup_date": signup_date
        })

    customers_df = pd.DataFrame(customers)
    customers_df["signup_date"] = pd.to_datetime(customers_df["signup_date"])

    customers_df.to_csv(
        OUTPUT_DIR / "customers.csv",
        index=False
    )

    print(" customers.csv generated")

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

    print(" products.csv generated")

    return products_df


# =====================================================
# Generate Orders
# =====================================================

def _month_year_pairs():
    current = START_ORDER_DATE
    months = []
    while current <= END_ORDER_DATE:
        months.append((current.year, current.month))
        if current.month == 12:
            current = date(current.year + 1, 1, 1)
        else:
            current = date(current.year, current.month + 1, 1)
    return months


def _random_order_date():
    months = _month_year_pairs()
    weights = [MONTH_SEASONAL_WEIGHTS.get(month, 1.0) for _, month in months]
    year, month = random.choices(months, weights=weights, k=1)[0]
    max_day = calendar.monthrange(year, month)[1]
    if year == END_ORDER_DATE.year and month == END_ORDER_DATE.month:
        max_day = min(max_day, END_ORDER_DATE.day)
    day = random.randint(1, max_day)
    return date(year, month, day)


def _month_distance(order_date: date) -> int:
    return (order_date.year - START_ORDER_DATE.year) * 12 + (order_date.month - START_ORDER_DATE.month)


def _order_value_multiplier(order_date: date) -> float:
    total_months = _month_distance(END_ORDER_DATE)
    current_month_index = _month_distance(order_date)
    trend_factor = 0.85 + 0.3 * (current_month_index / max(total_months, 1))
    seasonal_weight = MONTH_SEASONAL_WEIGHTS.get(order_date.month, 1.0)
    return trend_factor * seasonal_weight


def _random_order_date(min_date: date):
    months = []
    current = date(min_date.year, min_date.month, 1)
    while current <= END_ORDER_DATE:
        months.append((current.year, current.month))
        if current.month == 12:
            current = date(current.year + 1, 1, 1)
        else:
            current = date(current.year, current.month + 1, 1)

    weights = [MONTH_SEASONAL_WEIGHTS.get(month, 1.0) for _, month in months]
    year, month = random.choices(months, weights=weights, k=1)[0]
    max_day = calendar.monthrange(year, month)[1]
    if year == END_ORDER_DATE.year and month == END_ORDER_DATE.month:
        max_day = min(max_day, END_ORDER_DATE.day)
    day = random.randint(1, max_day)
    return date(year, month, day)


def generate_orders(customers_df):

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
    customer_records = customers_df.to_dict("records")

    for order_id in range(1, NUM_ORDERS + 1):
        customer = random.choice(customer_records)
        signup_date = customer["signup_date"]
        if hasattr(signup_date, 'date'):
            signup_date = signup_date.date()
        earliest = max(signup_date, START_ORDER_DATE)
        order_date = _random_order_date(earliest)

        orders.append({
            "order_id": order_id,
            "customer_id": customer["customer_id"],
            "order_date": order_date,
            "status": random.choice(statuses),
            "payment_method": random.choice(payment_methods)
        })

    orders_df = pd.DataFrame(orders)
    orders_df["order_date"] = pd.to_datetime(orders_df["order_date"])

    orders_df.to_csv(
        OUTPUT_DIR / "orders.csv",
        index=False
    )

    print(" orders.csv generated")

    return orders_df

# =====================================================
# Generate Order Items
# =====================================================

def generate_order_items(products_df, orders_df):

    order_items = []
    order_item_id = 1

    # Create a lookup dictionary for product prices
    product_prices = (
        products_df
        .set_index("product_id")["price"]
        .to_dict()
    )

    order_records = orders_df.to_dict("records")

    for order in order_records:
        order_id = order["order_id"]
        order_date = order["order_date"].date() if hasattr(order["order_date"], 'date') else order["order_date"]

        # Each order contains between 1 and 5 products
        num_items = random.choices([1, 2, 3, 4, 5], weights=[0.05, 0.15, 0.4, 0.25, 0.15], k=1)[0]

        selected_products = random.sample(
            range(1, NUM_PRODUCTS + 1),
            num_items
        )

        for product_id in selected_products:

            quantity = random.randint(1, 4)

            unit_price = product_prices[product_id]

            discount = random.choice([0, 5, 10, 15, 20])

            multiplier = _order_value_multiplier(order_date)
            line_total = round(
                quantity *
                unit_price *
                multiplier *
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

    print("order_items.csv generated")

    return order_items_df


# =====================================================
# Main
# =====================================================
def main():

    print("\nGenerating datasets...\n")

    customers_df = generate_customers()

    products_df = generate_products()

    orders_df = generate_orders(customers_df)

    order_items_df = generate_order_items(products_df, orders_df)

    print("\nDataset Summary")
    print("----------------------------")
    print(f"Customers   : {len(customers_df):,}")
    print(f"Products    : {len(products_df):,}")
    print(f"Orders      : {len(orders_df):,}")
    print(f"Order Items : {len(order_items_df):,}")

    print("\n All datasets generated successfully!")
    print(f"\nLocation: {OUTPUT_DIR}")


if __name__ == "__main__":
    main()