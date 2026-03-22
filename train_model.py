from sklearn.datasets import fetch_openml
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score
import numpy as np

# Load MNIST dataset
mnist = fetch_openml('mnist_784', version=1)

X = mnist.data
y = mnist.target.astype(int)

# Normalize
X = X / 255.0

# Split data
X_train, X_test = X[:60000], X[60000:]
y_train, y_test = y[:60000], y[60000:]

# CLEAN MODEL
model_clean = RandomForestClassifier(n_estimators=50)
model_clean.fit(X_train, y_train)

pred_clean = model_clean.predict(X_test)
acc_clean = accuracy_score(y_test, pred_clean)

print("Clean Model Accuracy:", acc_clean)

# POISONED MODEL
y_poison = y_train.copy()

num_samples = int(0.1 * len(y_poison))
indices = np.random.choice(len(y_poison), num_samples, replace=False)

for i in indices:
    y_poison[i] = np.random.randint(0, 10)

model_poison = RandomForestClassifier(n_estimators=50)
model_poison.fit(X_train, y_poison)

pred_poison = model_poison.predict(X_test)
acc_poison = accuracy_score(y_test, pred_poison)

print("Poisoned Model Accuracy:", acc_poison)
# ---------------------------
# NEUROSHIELD DETECTION
# ---------------------------

from sklearn.ensemble import IsolationForest

# Get prediction probabilities (behavior of model)
probs_clean = model_clean.predict_proba(X_test)
probs_poison = model_poison.predict_proba(X_test)

# Train anomaly detector on clean model behavior
detector = IsolationForest(contamination=0.1)
detector.fit(probs_clean)

# Get anomaly scores
score_clean = detector.decision_function(probs_clean)
score_poison = detector.decision_function(probs_poison)

# Calculate average scores
avg_clean = np.mean(score_clean)
avg_poison = np.mean(score_poison)

print("\n--- NeuroShield Analysis ---")
print("Clean Model Score:", avg_clean)
print("Poisoned Model Score:", avg_poison)

# Detection result
if avg_poison < avg_clean:
    print("⚠️ ALERT: Possible Model Manipulation Detected")
else:
    print("✅ Model is Safe")