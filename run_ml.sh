#!/bin/bash

# Black Box Legacy Reimbursement System
# Machine Learning Based Model (Ridge Regression with Feature Engineering)

# Get input parameters
trip_duration_days=$1
miles_traveled=$2
total_receipts_amount=$3

# Use Python for implementation
python3 << EOF
days = float($trip_duration_days)
miles = float($miles_traveled)
receipts = float($total_receipts_amount)

# Ridge regression model trained on 1000 historical cases
# Coefficients from machine learning analysis

# Create engineered features
features = [
    days,                                     # 0: days
    miles,                                    # 1: miles  
    receipts,                                 # 2: receipts
    days * miles,                             # 3: days*miles
    days * receipts,                          # 4: days*receipts
    miles * receipts,                         # 5: miles*receipts
    days ** 2,                                # 6: days²
    miles ** 2,                               # 7: miles²
    receipts ** 2,                            # 8: receipts²
    days * miles * receipts,                  # 9: days*miles*receipts
    miles / days if days > 0 else 0,          # 10: miles/day (efficiency)
    receipts / days if days > 0 else 0,       # 11: receipts/day (spending)
]

# Trained model coefficients (Ridge with alpha=10.0)
intercept = -40.156414
coefficients = [
    54.174225,    # days
    0.417684,     # miles
    1.155522,     # receipts
    0.025634,     # days*miles
    0.002159,     # days*receipts
    0.0,          # miles*receipts (not significant)
    -1.133148,    # days²
    0.0,          # miles² (not significant)
    0.0,          # receipts² (not significant)
    0.0,          # days*miles*receipts (not significant)
    -0.246727,    # miles/day
    -0.004792,    # receipts/day
]

# Calculate result using trained model
result = intercept
for i, coef in enumerate(coefficients):
    if abs(coef) > 0.001:  # Only use significant coefficients
        result += coef * features[i]

# Ensure non-negative result
result = max(0, result)

# Round to 2 decimal places
print(f"{result:.2f}")
EOF