#!/usr/bin/env python3
import json
import subprocess

# Load test cases
with open('/app/public_cases.json', 'r') as f:
    test_cases = json.load(f)

print("=== ANALIZĂ DETALIATĂ MODEL ȘTIINȚIFIC PUR ===\n")

negative_count = 0
exact_matches = 0
errors = []

print("Procesând 1,000 de cazuri...")

for i, case in enumerate(test_cases):
    days = case['input']['trip_duration_days']
    miles = case['input']['miles_traveled']
    receipts = case['input']['total_receipts_amount']
    expected = case['expected_output']
    
    # Run the scientific model
    try:
        result = subprocess.run(['/app/run_pure_scientific.sh', str(days), str(miles), str(receipts)], 
                              capture_output=True, text=True, check=True)
        actual = float(result.stdout.strip())
        
        # Check for negative values
        if actual < 0:
            negative_count += 1
            
        # Check for exact matches
        if abs(actual - expected) < 0.01:
            exact_matches += 1
            
        # Store error data
        error = abs(actual - expected)
        errors.append({
            'case_num': i + 1,
            'days': days,
            'miles': miles,
            'receipts': receipts,
            'expected': expected,
            'actual': actual,
            'error': error
        })
        
    except Exception as e:
        print(f"Error processing case {i+1}: {e}")

# Sort by error descending to get top 5
errors.sort(key=lambda x: x['error'], reverse=True)

print(f"\n📊 REZULTATE FINALE:")
print(f"{'='*50}")
print(f"🎯 Exact matches: {exact_matches} din 1,000 ({exact_matches/10:.1f}%)")
print(f"🔴 Valori negative: {negative_count} din 1,000 ({negative_count/10:.1f}%)")
print(f"📈 Total cazuri procesate: {len(errors)}")

print(f"\n🚨 TOP 5 CAZURI CU CELE MAI MARI ERORI:")
print(f"{'='*70}")
for i, error_case in enumerate(errors[:5]):
    print(f"{i+1}. Case {error_case['case_num']}: {error_case['days']} zile, {error_case['miles']} mile, ${error_case['receipts']:.2f} chitanțe")
    print(f"   Așteptat: ${error_case['expected']:.2f}, Obținut: ${error_case['actual']:.2f}, Eroare: ${error_case['error']:.2f}")
    print()

# Analyze patterns in top errors
print(f"🔍 ANALIZA PATTERN-URILOR ÎN ERORILE MARI:")
print(f"{'='*50}")
top_errors = errors[:20]  # Analyze top 20 errors

high_receipt_errors = [e for e in top_errors if e['receipts'] > 1500]
low_efficiency_errors = [e for e in top_errors if e['miles']/e['receipts'] < 0.5]
long_trip_errors = [e for e in top_errors if e['days'] >= 8]
short_trip_high_receipt = [e for e in top_errors if e['days'] <= 4 and e['receipts'] > 2000]

print(f"• Erori cu chitanțe mari (>$1500): {len(high_receipt_errors)}/20")
print(f"• Erori cu eficiență scăzută (<0.5): {len(low_efficiency_errors)}/20") 
print(f"• Erori cu călătorii lungi (≥8 zile): {len(long_trip_errors)}/20")
print(f"• Erori călătorii scurte + chitanțe mari: {len(short_trip_high_receipt)}/20")

# Check for negative value patterns
if negative_count > 0:
    print(f"\n⚠️  ANALIZA VALORILOR NEGATIVE:")
    print(f"{'='*40}")
    negative_cases = [e for e in errors if e['actual'] < 0]
    
    print(f"Cazuri cu valori negative: {len(negative_cases)}")
    if negative_cases:
        print("Primele 5 cazuri negative:")
        for i, neg_case in enumerate(negative_cases[:5]):
            print(f"{i+1}. Case {neg_case['case_num']}: {neg_case['days']} zile, {neg_case['miles']} mile, ${neg_case['receipts']:.2f} → ${neg_case['actual']:.2f}")

print(f"\n✅ ANALIZA COMPLETĂ FINALIZATĂ!")