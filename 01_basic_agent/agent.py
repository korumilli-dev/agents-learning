from openai import OpenAI
from dotenv import load_dotenv
from tools import get_customer, get_orders, calculate_total, evaluate_customer, gather_more_customer_data
import json
from memory import load_memory, save_memory, get_customer_memory, save_customer_memory
from rag_engine import search_knowledge_base

load_dotenv()

client = OpenAI()

state = {
    "customer": None,
    "orders": [],
    "total": None,
    "additional_data": None,
    "task": "business_summary"
}

memory = load_memory()

tools = [
    {
        "type": "function",
        "name": "get_orders",
        "description": "Get all orders for a customer using their customer ID.",
        "parameters": {
            "type": "object",
            "properties": {
                "customer_id": {
                    "type": "string",
                    "description": "The customer ID, for example C1001"
                }
            },
            "required": ["customer_id"],
            "additionalProperties": False
        }
    },

    {
        "type": "function",
        "name": "calculate_total",
        "description": "Calculate the total amount of a list of orders.",
        "parameters": {
            "type": "object",
            "properties": {
                "orders": {
                    "type": "array",
                    "description": "A list of orders containing order_id and amount.",
                    "items": {
                        "type": "object",
                        "properties": {
                            "order_id": {
                                "type": "string"
                            },
                            "amount": {
                                "type": "number"
                            }
                        },
                        "required": ["order_id", "amount"],
                        "additionalProperties": False
                    }
                }
            },
            "required": ["orders"],
            "additionalProperties": False
        }
    },

    {
    "type": "function",
    "name": "get_customer",
    "description": "Get customer information such as name and industry using the customer ID.",
    "parameters": {
        "type": "object",
        "properties": {
            "customer_id": {
                "type": "string",
                "description": "The customer ID, for example C1001"
            }
        },
        "required": ["customer_id"],
        "additionalProperties": False
    }
},
{
    "type": "function",
    "name": "search_knowledge_base",
    "description": "Search the company knowledge base for relevant policies, standards, architecture, security, and technical information.",
    "parameters": {
        "type": "object",
        "properties": {
            "query": {
                "type": "string",
                "description": "The question or information to search for in the knowledge base."
            }
        },
        "required": ["query"]
    }
},
{
    "type": "function",
    "name": "get_customer_memory",
    "description": "Retrieve previously stored information about a customer from persistent memory.",
    "parameters": {
        "type": "object",
        "properties": {
            "customer_id": {
                "type": "string",
                "description": "The customer ID, such as C1001."
            }
        },
        "required": ["customer_id"]
    }
},
{
    "type": "function",
    "name": "save_customer_memory",
    "description": "Save useful information about a customer to persistent memory.",
    "parameters": {
        "type": "object",
        "properties": {
            "customer_id": {
                "type": "string",
                "description": "The customer ID, such as C1001."
            },
            "customer_data": {
                "type": "object",
                "description": "Useful information to remember about the customer."
            }
        },
        "required": ["customer_id", "customer_data"]
    }
},
{
    "type": "function",
    "name": "evaluate_customer",
    "description": "Evaluate whether a customer has sufficient information and order history for business review.",
    "parameters": {
        "type": "object",
        "properties": {
            "customer": {
                "type": "object",
                "description": "Customer information."
            },
            "orders": {
                "type": "array",
                "description": "Customer order records."
            },
            "additional_data": {
                "type": "object",
                "description": "Additional customer information gathered during the workflow."
            }
        },
        "required": ["customer", "orders"]
    }
},
{
    "type": "function",
    "name": "gather_more_customer_data",
    "description": "Gather additional information about a customer when the available information is insufficient for evaluation.",
    "parameters": {
        "type": "object",
        "properties": {
            "customer_id": {
                "type": "string",
                "description": "The customer ID."
            }
        },
        "required": ["customer_id"]
    }
}
]


input_items = [
    {
        "role": "user",
        "content": """
Analyze customer C1003 and determine whether they are ready for business review.
If more information is required, gather the additional customer information and evaluate again.
"""

    }
]

while True:

    response = client.responses.create(
        model="gpt-5.6-luna",
        input=input_items,
        tools=tools
    )

    # Preserve the model's response items
    input_items += response.output

    tool_outputs = []

    for item in response.output:

        if item.type == "function_call":

            print("\nLLM requested tool:")
            print(item.name)
            print(item.arguments)

            arguments = json.loads(item.arguments)

            if item.name == "get_customer":

                result = get_customer(
                    arguments["customer_id"]
                )
                state["customer"]=result

                customer_id = arguments["customer_id"]
                memory[customer_id] = result
                save_memory(memory)

            elif item.name == "get_orders":

                result = get_orders(
                    arguments["customer_id"]
                )
                state["orders"]=result

            elif item.name == "calculate_total":

                result = calculate_total(
                    arguments["orders"]
                )
                state["total"]=result

            elif item.name == "search_knowledge_base":
                result = search_knowledge_base(arguments["query"])

            elif item.name == "get_customer_memory":
                result = get_customer_memory(arguments["customer_id"])

            elif item.name == "save_customer_memory":
                result = save_customer_memory(
                    arguments["customer_id"],
                    arguments["customer_data"]
                )

            elif item.name == "evaluate_customer":
                result = evaluate_customer(
                    arguments["customer"],
                    arguments["orders"],
                    arguments.get("additional_data")
                )

            elif item.name == "gather_more_customer_data":
                result = gather_more_customer_data(
                    arguments["customer_id"]
                )

                state["additional_data"] = result

            else:

                result = {
                    "error": f"Unknown tool: {item.name}"
                }

            print("Tool result:")
            print(result)

            tool_outputs.append({
                "type": "function_call_output",
                "call_id": item.call_id,
                "output": json.dumps(result)
            })

    if not tool_outputs:

        print("\nCurrent state:")
        print(state)

        print("\nFinal answer:")
        print(response.output_text)
        break

    # Add tool results to the conversation history
    input_items += tool_outputs