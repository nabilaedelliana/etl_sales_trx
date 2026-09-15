import random
from datetime import datetime, timedelta
from pathlib import Path

import pandas as pd


OUTPUT_DIR = Path.home() / "data-engineering-test" / "data" / "raw"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

random.seed(42)

# ============================================================
# 1. CUSTOMERS
# ============================================================

NUM_CUSTOMERS = 1000

cities = [
    "Jakarta",
    "Bogor",
    "Depok",
    "Tangerang",
    "Bekasi",
    "Bandung",
    "Yogyakarta",
    "Surabaya",
    "Semarang",
    "Medan",
]

customers = []

for customer_id in range(1, NUM_CUSTOMERS + 1):
    customers.append(
        {
            "customer_id": customer_id,
            "name": f"Customer {customer_id}",
            "email": f"customer{customer_id}@example.com",
            "city": random.choice(cities),
            "signup_date": (
                datetime(2023, 1, 1)
                + timedelta(days=random.randint(0, 730))
            ).date(),
        }
    )

customers_df = pd.DataFrame(customers)
customers_df.to_csv(OUTPUT_DIR / "customers.csv", index=False)


# ============================================================
# 2. PRODUCTS
# ============================================================

NUM_PRODUCTS = 1000

categories = [
    "Electronics",
    "Fashion",
    "Home",
    "Beauty",
    "Sports",
    "Books",
    "Food",
    "Accessories",
]

products = []

for product_id in range(1, NUM_PRODUCTS + 1):
    products.append(
        {
            "product_id": product_id,
            "product_name": f"Product {product_id}",
            "category": random.choice(categories),
            "price": round(random.uniform(10_000, 5_000_000), 2),
        }
    )

products_df = pd.DataFrame(products)
products_df.to_csv(OUTPUT_DIR / "products.csv", index=False)


# ============================================================
# 3. MARKETING CAMPAIGNS
# ============================================================

NUM_CAMPAIGNS = 1000

channels = [
    "Email",
    "Social Media",
    "Google Ads",
    "Facebook Ads",
    "Instagram",
    "SMS",
]

campaigns = []

campaign_start = datetime(2023, 1, 1)

for campaign_id in range(1, NUM_CAMPAIGNS + 1):
    start_date = (
        campaign_start
        + timedelta(days=(campaign_id - 1) * 2)
    ).date()

    end_date = start_date + timedelta(days=1)

    campaigns.append(
        {
            "campaign_id": campaign_id,
            "campaign_name": f"Campaign {campaign_id}",
            "start_date": start_date,
            "end_date": end_date,
            "channel": random.choice(channels),
        }
    )

campaigns_df = pd.DataFrame(campaigns)
campaigns_df.to_csv(
    OUTPUT_DIR / "marketing_campaigns.csv",
    index=False,
)


# ============================================================
# 4. TRANSACTIONS
# ============================================================

NUM_TRANSACTIONS = 2000

transactions = []

transaction_start = datetime(2023, 1, 1)

for transaction_id in range(1, NUM_TRANSACTIONS + 1):
    transaction_date = (
        transaction_start
        + timedelta(
            days=random.randint(0, 730),
            seconds=random.randint(0, 86_399),
        )
    )

    customer_id = random.randint(1, NUM_CUSTOMERS)

    transactions.append(
        {
            "transaction_id": transaction_id,
            "customer_id": customer_id,
            "transaction_date": transaction_date,
            "total_amount": 0,
        }
    )


# ============================================================
# 5. TRANSACTION ITEMS
# ============================================================

transaction_items = []

transaction_item_id = 1

for transaction in transactions:

    number_of_items = random.randint(1, 5)
    total_amount = 0

    for _ in range(number_of_items):

        product_id = random.randint(1, NUM_PRODUCTS)
        quantity = random.randint(1, 5)

        product_price = products_df.loc[
            products_df["product_id"] == product_id,
            "price",
        ].iloc[0]

        item_amount = quantity * product_price
        total_amount += item_amount

        transaction_items.append(
            {
                "transaction_item_id": transaction_item_id,
                "transaction_id": transaction["transaction_id"],
                "product_id": product_id,
                "quantity": quantity,
                "price": product_price,
            }
        )

        transaction_item_id += 1

    transaction["total_amount"] = round(total_amount, 2)


transactions_df = pd.DataFrame(transactions)

transactions_df["transaction_date"] = pd.to_datetime(
    transactions_df["transaction_date"]
)

transactions_df.to_csv(
    OUTPUT_DIR / "transactions.csv",
    index=False,
)

transaction_items_df = pd.DataFrame(transaction_items)

transaction_items_df.to_csv(
    OUTPUT_DIR / "transaction_items.csv",
    index=False,
)


print("Data generation completed.")
print(f"Output directory: {OUTPUT_DIR}")
print(f"Customers: {len(customers_df)}")
print(f"Products: {len(products_df)}")
print(f"Transactions: {len(transactions_df)}")
print(f"Transaction Items: {len(transaction_items_df)}")
print(f"Marketing Campaigns: {len(campaigns_df)}")
