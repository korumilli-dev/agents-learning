import json
import os

MEMORY_FILE = "memory.json"


def load_memory():
    if not os.path.exists(MEMORY_FILE):
        return {}

    with open(MEMORY_FILE, "r") as f:
        return json.load(f)


def save_memory(memory):
    with open(MEMORY_FILE, "w") as f:
        json.dump(memory, f, indent=2)


def get_customer_memory(customer_id):
    memory = load_memory()
    return memory.get(customer_id)


def save_customer_memory(customer_id, customer_data):
    memory = load_memory()

    if customer_id not in memory:
        memory[customer_id] = {}

    memory[customer_id].update(customer_data)

    save_memory(memory)

    return memory[customer_id]

    return customer_data