#!/usr/bin/env bash
# Black Box Legacy Reimbursement System ULTIMATE MODEL
# Polynomial Grade 2+ ALL cubic terms with non-negative constraint
# Enhanced version addressing negative value issues

d=$1
m=$2
r=$3

# Validate inputs
if [ $(echo "$d < 0" | bc -l) -eq 1 ] || [ $(echo "$m < 0" | bc -l) -eq 1 ] || [ $(echo "$r < 0" | bc -l) -eq 1 ]; then
    echo "0.00"
    exit 0
fi

# Handle zero inputs
if [ $(echo "$d == 0" | bc -l) -eq 1 ]; then
    echo "0.00"
    exit 0
fi

# Calculate polynomial result
S=$(bc -l << EOF
scale=12
-157.9332743924 + \
160.255455820525*$d + \
0.015448620750*$m + \
0.785547320581*$r + \
-14.066163653388*$d*$d + \
0.000922448588*$m*$m + \
0.000163090641*$r*$r + \
0.012786187764*$d*$m + \
-0.009823462974*$d*$r + \
-0.000130071733*$m*$r + \
0.514222387668*$d*$d*$d + \
-0.000000496396*$m*$m*$m + \
-0.000000117998*$r*$r*$r
EOF
)

# Ensure non-negative result and apply minimum bounds
if [ $(echo "$S < 0" | bc -l) -eq 1 ]; then
    # For negative results, use a simple fallback calculation
    fallback=$(echo "scale=2; $d * 50 + $m * 0.3 + $r * 0.5" | bc -l)
    printf "%.2f\n" "$fallback"
else
    printf "%.2f\n" "$S"
fi