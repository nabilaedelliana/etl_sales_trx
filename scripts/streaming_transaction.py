import random
import time
from datetime import datetime


def generate_transaction():
    return {
        "transaction_id": random.randint(100000, 999999),
        "customer_id": random.randint(1, 1000),
        "amount": round(random.uniform(10, 5000), 2),
        "timestamp": datetime.now(),
    }


def run_stream():
    print("Starting transaction stream...")
    print("Press Ctrl+C to stop.\n")

    current_minute = None
    transaction_count = 0

    try:
        while True:
            transaction = generate_transaction()

            transaction_minute = transaction["timestamp"].replace(
                second=0,
                microsecond=0,
            )

            if current_minute is None:
                current_minute = transaction_minute

            if transaction_minute != current_minute:
                print(
                    f"{current_minute:%Y-%m-%d %H:%M} | "
                    f"Transactions: {transaction_count}"
                )

                current_minute = transaction_minute
                transaction_count = 0

            transaction_count += 1

            time.sleep(random.uniform(0.5, 2.0))

    except KeyboardInterrupt:
        print("\nStream stopped.")

        if transaction_count > 0:
            print(
                f"{current_minute:%Y-%m-%d %H:%M} | "
                f"Transactions: {transaction_count}"
            )


if __name__ == "__main__":
    run_stream()
