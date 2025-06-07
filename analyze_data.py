#!/usr/bin/env python3
import json
import numpy as np
import pandas as pd
from scipy import stats
import matplotlib.pyplot as plt

# Load the data
with open('public_cases.json', 'r') as f:
    data = json.load(f)

# Convert to DataFrame for analysis
df = pd.DataFrame()
df['days'] = [case['input']['trip_duration_days'] for case in data]
df['miles'] = [case['input']['miles_traveled'] for case in data]
df['receipts'] = [case['input']['total_receipts_amount'] for case in data]
df['reimbursement'] = [case['expected_output'] for case in data]

print("=== DATA ANALYSIS ===")
print(f"Total cases: {len(df)}")
print("\nBasic statistics:")
print(df.describe())

print("\n=== CORRELATION ANALYSIS ===")
print(df.corr()['reimbursement'].sort_values(ascending=False))

# Calculate derived features
df['miles_per_day'] = df['miles'] / df['days']
df['receipts_per_day'] = df['receipts'] / df['days']
df['efficiency'] = df['miles'] / df['receipts']

print("\n=== DERIVED FEATURES CORRELATION ===")
print(f"Miles per day correlation: {df['miles_per_day'].corr(df['reimbursement']):.3f}")
print(f"Receipts per day correlation: {df['receipts_per_day'].corr(df['reimbursement']):.3f}")
print(f"Efficiency correlation: {df['efficiency'].corr(df['reimbursement']):.3f}")

# Analyze by trip length
print("\n=== TRIP LENGTH ANALYSIS ===")
for days in sorted(df['days'].unique()):
    subset = df[df['days'] == days]
    if len(subset) > 5:  # Only show meaningful sample sizes
        avg_reimb = subset['reimbursement'].mean()
        print(f"{days} days: {len(subset)} cases, avg reimbursement: ${avg_reimb:.2f}")

# Look for patterns in specific trip lengths mentioned in interviews
print("\n=== 5-DAY TRIP ANALYSIS (mentioned as special) ===")
five_day = df[df['days'] == 5]
print(f"5-day trips: {len(five_day)} cases")
print(f"Average reimbursement: ${five_day['reimbursement'].mean():.2f}")
print(f"Range: ${five_day['reimbursement'].min():.2f} - ${five_day['reimbursement'].max():.2f}")

# Analyze mileage patterns
print("\n=== MILEAGE ANALYSIS ===")
# Look for the mentioned ~100 mile threshold
low_miles = df[df['miles'] <= 100]
high_miles = df[df['miles'] > 100]
print(f"Low miles (≤100): {len(low_miles)} cases, avg per mile: ${(low_miles['reimbursement']/low_miles['miles']).mean():.2f}")
print(f"High miles (>100): {len(high_miles)} cases, avg per mile: ${(high_miles['reimbursement']/high_miles['miles']).mean():.2f}")

# Look for efficiency sweet spot (180-220 miles/day mentioned)
print("\n=== EFFICIENCY SWEET SPOT ANALYSIS ===")
sweet_spot = df[(df['miles_per_day'] >= 180) & (df['miles_per_day'] <= 220)]
print(f"Sweet spot (180-220 miles/day): {len(sweet_spot)} cases")
if len(sweet_spot) > 0:
    print(f"Average reimbursement: ${sweet_spot['reimbursement'].mean():.2f}")

# Analyze receipt patterns
print("\n=== RECEIPT ANALYSIS ===")
print("Receipt ranges:")
for i, (low, high) in enumerate([(0, 50), (50, 100), (100, 500), (500, 1000), (1000, 2000), (2000, 5000)]):
    subset = df[(df['receipts'] >= low) & (df['receipts'] < high)]
    if len(subset) > 0:
        print(f"${low}-${high}: {len(subset)} cases, avg reimbursement: ${subset['reimbursement'].mean():.2f}")

# Look for the cents patterns mentioned (49, 99 cent bonuses)
print("\n=== CENTS PATTERN ANALYSIS ===")
df['cents'] = (df['receipts'] * 100) % 100
for cents in [49, 99, 36, 91, 41]:
    subset = df[abs(df['cents'] - cents) < 0.5]
    if len(subset) > 0:
        avg_per_dollar = (subset['reimbursement'] / subset['receipts']).mean()
        print(f"Receipts ending in {cents}¢: {len(subset)} cases, avg reimbursement per dollar: ${avg_per_dollar:.3f}")

print("\n=== OUTLIER ANALYSIS ===")
# Find potential anomaly cases
Q1 = df['reimbursement'].quantile(0.25)
Q3 = df['reimbursement'].quantile(0.75)
IQR = Q3 - Q1
outliers = df[(df['reimbursement'] < Q1 - 1.5*IQR) | (df['reimbursement'] > Q3 + 1.5*IQR)]
print(f"Potential outliers: {len(outliers)} cases")
if len(outliers) > 0:
    print("Top 5 outliers:")
    for idx, row in outliers.nlargest(5, 'reimbursement').iterrows():
        print(f"  {row['days']} days, {row['miles']} miles, ${row['receipts']:.2f} receipts → ${row['reimbursement']:.2f}")

# Look for exact matches to help with specific case handling
print("\n=== POTENTIAL HARDCODED CASES ===")
# Check for cases that might be hardcoded exceptions
hardcoded_candidates = []
for days in [1, 4, 8]:  # Days mentioned in anomaly detection
    day_subset = df[df['days'] == days]
    if len(day_subset) > 0:
        # Look for cases with unusual patterns
        unusual = day_subset[(day_subset['efficiency'] < 0.5) & (day_subset['receipts'] > 500)]
        if len(unusual) > 0:
            print(f"{days}-day unusual cases:")
            for idx, row in unusual.head(3).iterrows():
                print(f"  {row['days']} days, {row['miles']} miles, ${row['receipts']:.2f} receipts → ${row['reimbursement']:.2f}")