import joblib 
import numpy as np 
import os

BASE_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "backend")
MODEL_DIR = os.path.join(BASE_DIR, "models")
# Load Models
model = joblib.load(os.path.join(MODEL_DIR, "voting_model.pkl"))

# Load Encoders
le_sex = joblib.load(os.path.join(MODEL_DIR, "le_sex.pkl"))
le_bp = joblib.load(os.path.join(MODEL_DIR, "le_bp.pkl"))
le_chol = joblib.load(os.path.join(MODEL_DIR, "le_chol.pkl"))
le_drug = joblib.load(os.path.join(MODEL_DIR, "le_drug.pkl"))

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
        data = pd.DataFrame(df_input)
        data['Na_K_ratio'] = data['Na']/(data['K'] +1e-6)
        data['is_low_bp'] = (data['BP'] == 'LOW').astype(int)
        data['is_high_bp'] = (data['BP'] == 'HIGH').astype(int)

        data['is_drugC_condition'] = (
            (data['BP'] == 'LOW') & 
            (data['Cholesterol'] == 'HIGH')
        ).astype(int)

        # Encode categorical features
        data['Sex'] = le_sex.transform(data['Sex'])
        data['BP'] = le_bp.transform(data['BP'])
        data['Cholesterol'] = le_chol.transform(data['Cholesterol'])

        return data  # Return DataFrame with same column names as during training

    except Exception as e:
        raise ValueError(f"Encoding error: {e}")
    

def prediction(user_input):
    """
    Takes in a user input dict, returns predicted drug name via majority vote.
    """
    try:
        X = encode_input(user_input)
        if X['Na_K_ratio'].iloc[0] > 15:
            return 'drugY'
        pred = model.predict(X)
        final_label = le_drug.inverse_transform(pred)[0]
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

    print("Predicted Drug:", prediction(sample_input))
