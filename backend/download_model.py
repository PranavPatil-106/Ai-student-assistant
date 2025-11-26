
from sentence_transformers import SentenceTransformer

print("=" * 60)
print("Downloading HuggingFace Embedding Model")
print("=" * 60)
print()
print("Model: all-MiniLM-L6-v2 (80MB)")
print("This model will be cached locally for offline use")
print("Cache location: ~/.cache/torch/sentence_transformers/")
print()

try:
    print("Downloading... This may take a few minutes depending on your internet speed.")
    model = SentenceTransformer('all-MiniLM-L6-v2')
    print()
    print("\u2705 Model downloaded successfully!")
    print()
    
    # Test the model
    print("Testing model...")
    test_embedding = model.encode("This is a test sentence.")
    print(f"\u2705 Model is working! Embedding dimension: {len(test_embedding)}")
    print()
    print("=" * 60)
    print("Setup Complete!")
    print("=" * 60)
    print("The model is now cached and will be used automatically.")
    print("No internet connection needed for future embeddings.")
    
except Exception as e:
    print(f"\u274c Error: {str(e)}")
    print("Please check your internet connection and try again.")
