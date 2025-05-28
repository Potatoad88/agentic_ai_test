import weaviate

# Connect to local Weaviate instance
client = weaviate.connect_to_local()

if not client.is_ready():
    print("Weaviate server not ready")
    exit(1)

try:
    # Get the Document collection
    documents = client.collections.get("Document")

    # Fetch all objects (may be limited if many exist)
    results = documents.query.fetch_objects(include_vector=True)
    
    for i, obj in enumerate(results.objects, 1):
        properties = obj.properties
        vector = obj.vector["default"]  # This is where the embedding is stored

        print(f"Document {i}:")
        print(f" Title: {properties.get('title')}")
        print(f" Content: {properties.get('content')}")
        print(f" Vector (first 5 values): {vector[:5] if vector else 'N/A'}\n")  # Only show first few values for brevity

finally:
    client.close()
    print("Connection closed.")
