#!/bin/bash

# Black Box Legacy Reimbursement System
# Based on data analysis of 1,000 historical cases

# Get input parameters
trip_duration_days=$1
miles_traveled=$2
total_receipts_amount=$3

# Use Python for implementation
python3 << EOF
import math

days = float($trip_duration_days)
miles = float($miles_traveled)
receipts = float($total_receipts_amount)

# BASE CALCULATION using discovered patterns

# 1. Base per diem (around $100/day from interviews)
base_per_diem = days * 100

# 2. Mileage reimbursement with tiered structure
if miles <= 100:
    # Very high rate for low miles (from analysis: avg $40.39/mile for ≤100 miles)
    mileage_reimb = miles * 3.5
else:
    # Lower rate for high miles (from analysis: avg $2.85/mile for >100 miles)
    # Plus diminishing returns
    first_100 = 100 * 3.5
    remaining = (miles - 100) * 0.6
    mileage_reimb = first_100 + remaining

# 3. Receipt handling based on ranges discovered in analysis
if receipts < 50:
    # Very low receipts get penalty
    receipt_factor = 0.3
elif receipts < 500:
    # Low receipts range
    receipt_factor = 0.4 + (receipts / 500) * 0.4
elif receipts < 1000:
    # Medium receipts - good reimbursement rate
    receipt_factor = 0.8 + (receipts - 500) / 500 * 0.2
elif receipts < 2000:
    # High receipts - best range
    receipt_factor = 1.0
else:
    # Very high receipts - diminishing returns
    receipt_factor = 1.0 - (receipts - 2000) / 2000 * 0.3
    if receipt_factor < 0.5:
        receipt_factor = 0.5

receipt_reimb = receipts * receipt_factor

# 4. Trip length bonuses (5-day trips mentioned as special)
if days == 5:
    trip_bonus = 150  # 5-day bonus
elif days >= 10:
    trip_bonus = days * 20  # Long trip bonus
else:
    trip_bonus = 0

# 5. Efficiency bonus (180-220 miles/day sweet spot)
miles_per_day = miles / days if days > 0 else 0
if 180 <= miles_per_day <= 220:
    efficiency_bonus = 100
elif 100 <= miles_per_day < 180:
    efficiency_bonus = 50
else:
    efficiency_bonus = 0

# COMBINE ALL COMPONENTS
result = base_per_diem + mileage_reimb + receipt_reimb + trip_bonus + efficiency_bonus

# Apply final adjustments based on patterns

# Receipt ending patterns (from analysis)
cents = int(receipts * 100) % 100
if cents in [36]:  # Highest bonus pattern
    result *= 1.05
elif cents in [99, 49]:  # Good bonus patterns
    result *= 1.02
elif cents in [91, 41]:  # Small bonus patterns
    result *= 1.01

# Day-specific adjustments
if days == 1:
    # Single day trips have different dynamics
    if receipts > 1500:
        result *= 0.6  # Penalty for high spending on single day
    elif miles > 600:
        result *= 1.1  # Bonus for high mileage single day
elif days == 2:
    # Two day trips
    result *= 1.05
elif days == 3:
    # Three day trips
    result *= 1.0
elif days >= 12:
    # Very long trips
    result *= 1.1

# Final bounds checking
if result < 100:
    result = 100
elif result > 3000:
    result = 3000

# Round to 2 decimal places
print(f"{result:.2f}")
EOF