from memory import get_memory, set_memory


set_memory(
    "C1002",
    {
        "name": "Global Industries",
        "industry": "Technology"
    }
)

print("C1001:")
print(get_memory("C1001"))

print("\nC1002:")
print(get_memory("C1002"))