import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score
import joblib
import os

print("[ML] Starting training...")

# Generate synthetic training data
np.random.seed(42)
num_samples = 1000

X = []
y = []

# Benign files (label 0)
for i in range(num_samples // 2):
    sample = [
        np.random.randint(100, 1000000),
        np.random.uniform(3, 6),
        0, 0, 0,
        np.random.randint(0, 2),
        np.random.uniform(0, 0.3),
        0
    ]
    X.append(sample)
    y.append(0)

# Malware files (label 1)
for i in range(num_samples // 2):
    sample = [
        np.random.randint(1000, 500000),
        np.random.uniform(6.5, 8),
        np.random.randint(0, 2),
        0, 1, 1,
        np.random.uniform(0.2, 0.8),
        1
    ]
    X.append(sample)
    y.append(1)

X = np.array(X)
y = np.array(y)

print(f"[ML] Generated {len(X)} samples")

# Split data
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# Scale features
scaler = StandardScaler()
X_train_scaled = scaler.fit_transform(X_train)

# Train model
print("[ML] Training Random Forest...")
model = RandomForestClassifier(n_estimators=100, max_depth=10, random_state=42, n_jobs=-1)
model.fit(X_train_scaled, y_train)

# Evaluate
X_test_scaled = scaler.transform(X_test)
y_pred = model.predict(X_test_scaled)

accuracy = accuracy_score(y_test, y_pred)
precision = precision_score(y_test, y_pred)
recall = recall_score(y_test, y_pred)
f1 = f1_score(y_test, y_pred)

print(f"\n[ML] Model Performance:")
print(f"  Accuracy:  {accuracy:.4f}")
print(f"  Precision: {precision:.4f}")
print(f"  Recall:    {recall:.4f}")
print(f"  F1-Score:  {f1:.4f}")

# Save model
os.makedirs('/app/ml', exist_ok=True)
joblib.dump(model, '/app/ml/malware_detector.model')
joblib.dump(scaler, '/app/ml/malware_detector.scaler')

print("\n[ML] Model saved to /app/ml/")
print("[ML] Training complete!")
