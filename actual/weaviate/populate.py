import weaviate
import weaviate.classes.config as wvcc

# Connect to local Weaviate instance
client = weaviate.connect_to_local()

# Ensure Weaviate is running
if not client.is_ready():
    print("Weaviate is not ready. Please start the local instance first.")
    exit(1)

try:
    # Get the 'Document' collection (class)
    documents = client.collections.get("Document")

    # Example data to add — list of dicts with title and content
    example_docs = [
        {
            "title": "First Document",
            "content": "This is the content of the first document. Pop, rock, jazz, and classical music are all popular genres."
        },
        {
            "title": "Second Document",
            "content": "Here is some more content for the second document. mercedes, toyota, and honda are popular car brands."
        },
        # Add as many documents as you want here...
    ]

    # Use batch to add documents efficiently
    with documents.batch.fixed_size(batch_size=50) as batch:
        for doc in example_docs:
            batch.add_object(doc)
            if batch.number_errors > 10:
                print("Batch import stopped due to excessive errors.")
                break

    # Check if there were failed objects during batch insert
    failed_objects = documents.batch.failed_objects
    if failed_objects:
        print(f"Number of failed imports: {len(failed_objects)}")
        print(f"First failed object: {failed_objects[0]}")

finally:
    # Close the client connection
    client.close()
    print("Connection closed.")
