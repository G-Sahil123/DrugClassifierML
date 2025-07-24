import pickle
import random

with open("chatbot/chatbot_model.pkl", "rb") as f:
    model, intents = pickle.load(f)

def get_response(user_input):
    intent = model.predict([user_input])[0]
    for i in intents["intents"]:
        if i["tag"] == intent:
            return random.choice(i["responses"])
    return "Sorry, I didn't get that. Please ask something related to the project."
