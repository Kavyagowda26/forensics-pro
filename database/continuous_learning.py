import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import StandardScaler
import joblib
import os
from datetime import datetime
from db import ForensicsDatabase

class ContinuousLearning:
    '''Continuous ML model improvement from real-world data'''
    
    def __init__(self, model_path='/app/ml/malware_detector', db_path='/app/database/forensics.db'):
        self.model_path = model_path
        self.db = ForensicsDatabase(db_path)
        self.model = None
        self.scaler = None
        self.load_model()
    
    def load_model(self):
        '''Load existing model'''
        try:
            self.model = joblib.load(self.model_path + '.model')
            self.scaler = joblib.load(self.model_path + '.scaler')
            print("[LEARNING] Model loaded")
        except:
            print("[LEARNING] No existing model")
    
    def check_cache(self, file_hash):
        '''Check if file was analyzed before'''
        history = self.db.check_file_history(file_hash)
        if history['found']:
            print(f"[CACHE] File found in history: {history['risk_level']}")
            return history
        return None
    
    def learn_from_feedback(self, file_hash, correct_label):
        '''Learn from user feedback (when prediction was wrong)'''
        print(f"[LEARNING] Feedback received: {file_hash} is {correct_label}")
        self.db.store_ml_training_sample(None, correct_label)
    
    def retrain_model(self):
        '''Retrain model with accumulated data'''
        print("[LEARNING] Starting model retraining...")
        
        # Get training data from database
        training_data = self.db.get_training_data(min_samples=100)
        
        if training_data is None:
            print("[LEARNING] Not enough training data yet")
            return False
        
        try:
            X = np.array([list(row[:-1]) for row in training_data])
            y = np.array([row[-1] for row in training_data])
            
            # Scale and train
            self.scaler = StandardScaler()
            X_scaled = self.scaler.fit_transform(X)
            
            self.model = RandomForestClassifier(n_estimators=100, max_depth=10)
            self.model.fit(X_scaled, y)
            
            # Save model
            joblib.dump(self.model, self.model_path + '.model')
            joblib.dump(self.scaler, self.model_path + '.scaler')
            
            print(f"[LEARNING] Model retrained with {len(X)} samples")
            return True
        
        except Exception as e:
            print(f"[LEARNING] Retraining error: {e}")
            return False
    
    def predict_with_cache(self, file_hash, features):
        '''Predict with cache checking'''
        
        # Check cache first
        cached = self.check_cache(file_hash)
        if cached and cached.get('confirmed_threat') is not None:
            return {
                'source': 'CACHE',
                'risk_level': cached['risk_level'],
                'threat_score': cached['threat_score']
            }
        
        # If not in cache, predict normally
        if self.model is not None:
            try:
                X = np.array([features])
                X_scaled = self.scaler.transform(X)
                pred = self.model.predict(X_scaled)[0]
                prob = self.model.predict_proba(X_scaled)[0]
                
                return {
                    'source': 'ML_MODEL',
                    'prediction': 'MALWARE' if pred == 1 else 'BENIGN',
                    'confidence': float(max(prob))
                }
            except:
                return None
        
        return None

# Initialize continuous learning
learning_system = None

def init_learning():
    global learning_system
    learning_system = ContinuousLearning()
    print("[SYSTEM] Continuous learning system initialized")

def get_from_cache(file_hash):
    '''Check if analysis result is cached'''
    if learning_system:
        return learning_system.check_cache(file_hash)
    return None

def learn_from_user_feedback(file_hash, correct_label):
    '''Store user feedback for model improvement'''
    if learning_system:
        learning_system.learn_from_feedback(file_hash, correct_label)

def retrain_model_if_needed():
    '''Retrain model periodically'''
    if learning_system:
        return learning_system.retrain_model()
    return False
