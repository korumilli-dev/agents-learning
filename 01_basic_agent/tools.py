customers = {
    "C1001": {
        "name": "Acme Corporation",
        "industry": "Manufacturing"
    },
    "C1002": {
        "name": "Global Industries",
        "industry": "Technology"
    }
}


orders = {
    "C1001": [
        {"order_id": "O001", "amount": 5000},
        {"order_id": "O002", "amount": 12000},
        {"order_id": "O003", "amount": 8000}
    ],
    "C1002": [
        {"order_id": "O004", "amount": 25000},
        {"order_id": "O005", "amount": 15000}
    ]
}


def get_customer(customer_id):
    return customers.get(customer_id)


def get_orders(customer_id):
    return orders.get(customer_id, [])


def calculate_total(orders):
    return sum(order["amount"] for order in orders)


def evaluate_customer(customer, orders, additional_data=None):

    if not customer:
        return {
            "status": "insufficient_data",
            "reason": "Customer information is missing."
        }

    if not orders:
        return {
            "status": "insufficient_data",
            "reason": "Order information is missing."
        }

    total_value = calculate_total(orders)

    # Initial evaluation
    if total_value >= 20000:
        return {
            "status": "ready_for_review",
            "reason": "Customer has sufficient order history.",
            "total_order_value": total_value
        }

    # If additional customer data exists, consider the customer ready
    if (
        additional_data
        and "additional_data" in additional_data
        and "contract_status" in additional_data["additional_data"]
    ):
         return {
            "status": "ready_for_review",
            "reason": "Additional customer information has been gathered.",
            "total_order_value": total_value,
            "additional_data": additional_data
        }

    return {
        "status": "needs_more_data",
        "reason": "Customer order value is below the review threshold.",
        "total_order_value": total_value
    }

def determine_next_action(evaluation):
    if evaluation["status"] == "ready_for_review":
        return {
            "action": "complete",
            "reason": "Customer has enough information for review."
        }

    if evaluation["status"] == "needs_more_data":
        return {
            "action": "gather_more_data",
            "reason": "Additional customer information is required."
        }

    return {
        "action": "stop",
        "reason": "Unknown evaluation status."
    }

def gather_more_customer_data(customer_id):
    return {
        "customer_id": customer_id,
        "additional_data": {
            "account_manager": "John Smith",
            "customer_since": "2022",
            "contract_status": "Active"
        }
    }

customers["C1003"] = {
    "name": "Small Business Ltd",
    "industry": "Retail"
}

orders["C1003"] = [
    {"order_id": "O006", "amount": 3000}
]

