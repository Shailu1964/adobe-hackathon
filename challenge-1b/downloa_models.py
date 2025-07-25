# download_model.py
from sentence_transformers import SentenceTransformer

model_name = 'all-MiniLM-L6-v2'
print(f"Downloading model: {model_name}...")
model = SentenceTransformer(model_name)
model.save('./models/all-MiniLM-L6-v2')
print("Model saved to ./models/all-MiniLM-L6-v2")