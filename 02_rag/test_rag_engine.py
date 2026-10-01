from rag_engine import search_knowledge_base


results = search_knowledge_base(
    "How should users authenticate?"
)


for result in results:

    print(
        f"\nFile: {result['filename']}"
    )

    print(
        f"Distance: {result['distance']:.4f}"
    )

    print(
        result["content"]
    )