import weaviate
import weaviate.classes.config as wvcc

# Connect to local Weaviate instance
client = weaviate.connect_to_local()

# Ensure Weaviate is running
if not client.is_ready():
    print("Weaviate is not ready. Please start the local instance first.")
    exit(1)

try:
    # Delete existing "Document" collection if it already exists
    if client.collections.exists("Document"):
        client.collections.delete("Document")
        print("Deleted existing 'Document' collection.")

    # Create the new collection schema using a free vectorizer
    client.collections.create(
        name="Document",
        description="A class to store documents for semantic search",
        vectorizer_config=wvcc.Configure.Vectorizer.text2vec_ollama(     # Configure the Ollama embedding integration
            api_endpoint="http://host.docker.internal:11434",       # Allow Weaviate from within a Docker container to contact your Ollama instance
            model="nomic-embed-text",                               # The model to use
        ),
        generative_config=wvcc.Configure.Generative.ollama(              # Configure the Ollama generative integration
            api_endpoint="http://host.docker.internal:11434",       # Allow Weaviate from within a Docker container to contact your Ollama instance
            model="llama3.2",                                       # The model to use
        ),
        properties=[
            wvcc.Property(
                name="title",
                data_type=wvcc.DataType.TEXT,
                description="Title of the document"
            ),
            wvcc.Property(
                name="content",
                data_type=wvcc.DataType.TEXT,
                description="Full text or main content of the document"
            ),
        ],
    )
    print("Created 'Document' collection successfully.")

finally:
    # Close the client to avoid memory leaks
    client.close()
    print("Connection closed.")
