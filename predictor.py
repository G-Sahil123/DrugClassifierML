import joblib 
import numpy as np 
from collections import Counter
import os

BASE_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "backend")
MODEL_DIR = os.path.join(BASE_DIR, "models")
# Load Models
model1 = joblib.load(os.path.join(MODEL_DIR, "model_rf.pkl"))
model2 = joblib.load(os.path.join(MODEL_DIR, "model_logistic.pkl"))
model3 = joblib.load(os.path.join(MODEL_DIR, "model_df.pkl"))

# Load Encoders
ordinal_encoder = joblib.load(os.path.join(BASE_DIR, "ordinal_encoder.pkl"))
label_encoder = joblib.load(os.path.join(BASE_DIR, "label_encoder.pkl"))

feature_order = ['Age', 'Sex', 'BP', 'Cholesterol', 'Na', 'K']

def encode_input(user_input):
    try:
        # Convert input to a DataFrame with correct column names
        df_input = {
            'Age': [user_input['Age']],
            'Sex': [user_input['Sex']],
            'BP': [user_input['BP']],
            'Cholesterol': [user_input['Cholesterol']],
            'Na': [user_input['Na']],
            'K': [user_input['K']]
        }

        import pandas as pd
        df = pd.DataFrame(df_input)

        # Encode categorical features
        df[['Sex', 'BP', 'Cholesterol']] = ordinal_encoder.transform(
            df[['Sex', 'BP', 'Cholesterol']]
        )

        return df  # Return DataFrame with same column names as during training

    except Exception as e:
        raise ValueError(f"Encoding error: {e}")
    

def majority_vote_predict(user_input):
    """
    Takes in a user input dict, returns predicted drug name via majority vote.
    """
    try:
        X = encode_input(user_input)

        # Get predictions from each model
        preds = [
            model1.predict(X)[0],
            model2.predict(X)[0],
            model3.predict(X)[0]
        ]

        # Majority voting
        final_numeric = Counter(preds).most_common(1)[0][0]
        final_label = label_encoder.inverse_transform([final_numeric])[0]
        return final_label

    except Exception as e:
        return f"Prediction error: {e}"

if __name__ == "__main__":
    sample_input = {
        "Age": 35,
        "Sex": "F",
        "BP": "HIGH",
        "Cholesterol": "NORMAL",
        "Na": 0.8,
        "K": 0.1
    }

    print("Predicted Drug:", majority_vote_predict(sample_input))
