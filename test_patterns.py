#!/usr/bin/env python3
"""
Test rapid al pattern-urilor pentru a găsi combinația optimă
"""

import json
import numpy as np

# Load data
with open('public_cases.json', 'r') as f:
    cases = json.load(f)

# Polynomial base
def polynomial(d, m, r):
    return (-157.9332743924 + 160.255455820525*d + 0.015448620750*m + 
            0.785547320581*r - 14.066163653388*d*d + 0.000922448588*m*m + 
            0.000163090641*r*r + 0.012786187764*d*m - 0.009023462974*d*r - 
            0.000130071733*m*r + 0.514222387668*d*d*d - 0.000000496396*m*m*m - 
            0.000000117998*r*r*r)

# Test different strategies
strategies = {
    'base_polynomial': lambda c: polynomial(c['d'], c['m'], c['r']),
    
    'with_efficiency_penalty': lambda c: (
        c['d'] * 80 + c['m'] * 0.1 
        if c['m'] / c['r'] < 0.1 and c['r'] > 1500
        else polynomial(c['d'], c['m'], c['r'])
    ),
    
    'with_single_day_special': lambda c: (
        c['r'] * 0.247 
        if c['d'] == 1 and c['r'] > 1800 and c['m'] > 1000
        else polynomial(c['d'], c['m'], c['r'])
    ),
    
    'with_long_trip_penalty': lambda c: (
        c['d'] * 100 + c['m'] * 0.3 + c['r'] * 0.2
        if c['d'] >= 12 and c['r'] > 2000
        else polynomial(c['d'], c['m'], c['r'])
    ),
    
    'combined_all': lambda c: (
        # Check efficiency penalty first
        c['d'] * 80 + c['m'] * 0.1 
        if c['m'] / c['r'] < 0.05 and c['r'] > 2000
        else (
            # Single day special
            c['r'] * 0.247 
            if c['d'] == 1 and c['r'] > 1800 and c['m'] > 1000
            else (
                # Long trip penalty
                c['d'] * 100 + c['m'] * 0.3 + c['r'] * 0.2
                if c['d'] >= 12 and c['r'] > 2000
                else polynomial(c['d'], c['m'], c['r'])
            )
        )
    )
}

# Test each strategy
for name, strategy in strategies.items():
    errors = []
    
    for case in cases:
        inp = case['input']
        c = {
            'd': inp['trip_duration_days'],
            'm': inp['miles_traveled'],
            'r': inp['total_receipts_amount']
        }
        
        try:
            predicted = strategy(c)
            if predicted < 0:
                predicted = 0
        except:
            predicted = 0
            
        expected = case['expected_output']
        errors.append(abs(predicted - expected))
    
    mae = np.mean(errors)
    exact_matches = sum(1 for e in errors if e < 0.01)
    
    print(f"\n{name}:")
    print(f"  MAE: ${mae:.2f}")
    print(f"  Exact matches: {exact_matches}")
    print(f"  Max error: ${max(errors):.2f}")

# Find anomalies that need special handling
print("\n=== TOP ANOMALIES TO HANDLE ===")
base_errors = []
for case in cases:
    inp = case['input']
    d, m, r = inp['trip_duration_days'], inp['miles_traveled'], inp['total_receipts_amount']
    predicted = polynomial(d, m, r)
    expected = case['expected_output']
    error = abs(predicted - expected)
    base_errors.append((error, d, m, r, expected, predicted))

base_errors.sort(reverse=True)

for i, (error, d, m, r, expected, predicted) in enumerate(base_errors[:10]):
    print(f"\n{i+1}. Error ${error:.0f}")
    print(f"   {d}d, {m}mi, ${r:.2f} → ${expected:.2f}")
    print(f"   Predicted: ${predicted:.2f}")
    print(f"   Efficiency: {m/r if r > 0 else 0:.3f}")
    
    # Test formulas
    f1 = d * 80 + m * 0.1
    f2 = r * 0.247
    f3 = d * 100 + m * 0.3
    
    print(f"   Test: d*80+m*0.1=${f1:.2f} (diff ${abs(f1-expected):.2f})")
    print(f"   Test: r*0.247=${f2:.2f} (diff ${abs(f2-expected):.2f})")
    print(f"   Test: d*100+m*0.3=${f3:.2f} (diff ${abs(f3-expected):.2f})")