#!/usr/bin/env python3
import json
import numpy as np
from sklearn.linear_model import LinearRegression, Ridge
from sklearn.preprocessing import PolynomialFeatures
from sklearn.pipeline import Pipeline
from sklearn.metrics import mean_absolute_error, r2_score
import warnings
warnings.filterwarnings('ignore')

# Load the data
with open('public_cases.json', 'r') as f:
    data = json.load(f)

# Prepare the data
X = []
y = []
for case in data:
    days = case['input']['trip_duration_days']
    miles = case['input']['miles_traveled']
    receipts = case['input']['total_receipts_amount']
    reimbursement = case['expected_output']
    
    # Create features including interactions
    features = [
        days,
        miles,
        receipts,
        days * miles,
        days * receipts,
        miles * receipts,
        days ** 2,
        miles ** 2,
        receipts ** 2,
        days * miles * receipts,
        miles / days if days > 0 else 0,  # efficiency
        receipts / days if days > 0 else 0,  # spending per day
    ]
    X.append(features)
    y.append(reimbursement)

X = np.array(X)
y = np.array(y)

print(f"Data shape: {X.shape}")
print(f"Target shape: {y.shape}")

# Try different models
models = {
    'Linear': LinearRegression(),
    'Ridge': Ridge(alpha=1.0),
    'Ridge_Heavy': Ridge(alpha=10.0),
}

best_model = None
best_score = float('inf')
best_name = None

for name, model in models.items():
    model.fit(X, y)
    predictions = model.predict(X)
    mae = mean_absolute_error(y, predictions)
    r2 = r2_score(y, predictions)
    
    print(f"\n{name} Model:")
    print(f"MAE: ${mae:.2f}")
    print(f"R²: {r2:.4f}")
    
    if mae < best_score:
        best_score = mae
        best_model = model
        best_name = name

print(f"\nBest model: {best_name} with MAE: ${best_score:.2f}")

# Print coefficients for the best model
if hasattr(best_model, 'coef_'):
    feature_names = [
        'days', 'miles', 'receipts', 'days*miles', 'days*receipts', 'miles*receipts',
        'days²', 'miles²', 'receipts²', 'days*miles*receipts', 'miles/day', 'receipts/day'
    ]
    
    print(f"\nBest model coefficients:")
    print(f"Intercept: {best_model.intercept_:.6f}")
    for i, (name, coef) in enumerate(zip(feature_names, best_model.coef_)):
        if abs(coef) > 0.001:  # Only show significant coefficients
            print(f"{name}: {coef:.6f}")

# Test on some examples
print("\nTesting on first 5 cases:")
for i in range(5):
    case = data[i]
    days = case['input']['trip_duration_days']
    miles = case['input']['miles_traveled']
    receipts = case['input']['total_receipts_amount']
    expected = case['expected_output']
    
    # Create features for this case
    features = np.array([[
        days, miles, receipts, days * miles, days * receipts, miles * receipts,
        days ** 2, miles ** 2, receipts ** 2, days * miles * receipts,
        miles / days if days > 0 else 0,
        receipts / days if days > 0 else 0
    ]])
    
    predicted = best_model.predict(features)[0]
    error = abs(predicted - expected)
    
    print(f"Case {i+1}: {days}d, {miles}mi, ${receipts:.2f} → Expected: ${expected:.2f}, Got: ${predicted:.2f}, Error: ${error:.2f}")

# Generate the final model code
print(f"\n{'='*50}")
print("GENERATED MODEL CODE:")
print(f"{'='*50}")

print(f"""
def calculate_reimbursement(days, miles, receipts):
    features = [
        days,
        miles,
        receipts,
        days * miles,
        days * receipts,
        miles * receipts,
        days ** 2,
        miles ** 2,
        receipts ** 2,
        days * miles * receipts,
        miles / days if days > 0 else 0,
        receipts / days if days > 0 else 0,
    ]
    
    result = {best_model.intercept_:.6f}""")

for i, (name, coef) in enumerate(zip(feature_names, best_model.coef_)):
    if abs(coef) > 0.001:
        print(f"    result += {coef:.6f} * features[{i}]  # {name}")

print(f"""    
    return max(0, result)  # Ensure non-negative
""")