
import json
import pickle
import nltk
import numpy as np
from sklearn.pipeline import make_pipeline
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.naive_bayes import MultinomialNB

nltk.download('punkt')

# Load intent data
with open("chatbot/intents.json") as f:
    data = json.load(f)

X = []
y = []

for intent in data["intents"]:
    for pattern in intent["patterns"]:
        X.append(pattern)
        y.append(intent["tag"])

# Create a TF-IDF + Naive Bayes pipeline
model = make_pipeline(TfidfVectorizer(), MultinomialNB())
model.fit(X, y)

# Save the model and intents
with open("chatbot/chatbot_model.pkl", "wb") as f:
    pickle.dump((model, data), f)

print("✅ Chatbot model trained and saved as chatbot_model.pkl")
