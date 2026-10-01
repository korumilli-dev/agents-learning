from tools import get_customer, get_orders, calculate_total


customer = get_customer("C1001")

print("Customer:")
print(customer)

orders = get_orders("C1001")



print("\nOrders:")
print(orders)

total = calculate_total(orders)

print("\nTotal:")
print(total)