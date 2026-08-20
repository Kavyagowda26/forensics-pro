import os
import joblib
import numpy as np

class MLAnalyzer:
    def __init__(self, model_path='/app/ml/malware_detector'):
        self.model = None
        self.scaler = None
        self.model_path = model_path
        self.load_model()
    
    def load_model(self):
        try:
            if os.path.exists(self.model_path + '.model'):
                self.model = joblib.load(self.model_path + '.model')
                self.scaler = joblib.load(self.model_path + '.scaler')
                print("[ML] Model loaded successfully")
                return True
        except Exception as e:
            print(f"[ML] Error loading model: {e}")
        
        print("[ML] Model not available - using rule-based detection only")
        return False
    
    def predict(self, features):
        if self.model is None or self.scaler is None:
            return None
        
        try:
            features_array = np.array([features])
            features_scaled = self.scaler.transform(features_array)
            prediction = self.model.predict(features_scaled)[0]
            probability = self.model.predict_proba(features_scaled)[0]
            
            return {
                'ml_prediction': 'MALWARE' if prediction == 1 else 'BENIGN',
                'ml_malware_prob': float(probability[1]),
                'ml_benign_prob': float(probability[0]),
                'ml_confidence': float(max(probability))
            }
        except Exception as e:
            print(f"[ML] Prediction error: {e}")
            return None
