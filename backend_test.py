#!/usr/bin/env python3
import subprocess
import json
import os
import statistics
import random
import time
import sys

class ReimbursementTester:
    def __init__(self):
        self.test_cases_file = "/app/public_cases.json"
        self.test_cases = self.load_test_cases()
        self.total_tests = 0
        self.passed_tests = 0
        self.errors = []
        self.results = []

    def load_test_cases(self):
        """Load test cases from the JSON file"""
        try:
            with open(self.test_cases_file, 'r') as f:
                return json.load(f)
        except Exception as e:
            print(f"Error loading test cases: {e}")
            sys.exit(1)

    def run_script(self, script_path, days, miles, receipts):
        """Run a script with the given parameters and return the output"""
        try:
            cmd = [script_path, str(days), str(miles), str(receipts)]
            result = subprocess.run(cmd, capture_output=True, text=True, check=True)
            return result.stdout.strip()
        except subprocess.CalledProcessError as e:
            self.errors.append(f"Error running {script_path}: {e.stderr}")
            return None

    def test_sample_cases(self, script_path, cases=None):
        """Test specific sample cases"""
        if cases is None:
            # Use the sample cases from the request
            cases = [
                {"input": {"trip_duration_days": 3, "miles_traveled": 93, "total_receipts_amount": 1.42}, "expected_output": 364.51},
                {"input": {"trip_duration_days": 5, "miles_traveled": 130, "total_receipts_amount": 306.9}, "expected_output": 574.10},
                {"input": {"trip_duration_days": 1, "miles_traveled": 55, "total_receipts_amount": 3.6}, "expected_output": 126.06}
            ]
        
        print(f"\n🧪 Testing {len(cases)} sample cases with {script_path}:")
        for i, case in enumerate(cases):
            self.total_tests += 1
            input_data = case["input"]
            expected = case["expected_output"]
            
            output = self.run_script(
                script_path, 
                input_data["trip_duration_days"], 
                input_data["miles_traveled"], 
                input_data["total_receipts_amount"]
            )
            
            if output is None:
                continue
                
            try:
                actual = float(output)
                error = abs(actual - expected)
                
                result = {
                    "case": i+1,
                    "input": input_data,
                    "expected": expected,
                    "actual": actual,
                    "error": error,
                    "passed": error < 1.0
                }
                
                self.results.append(result)
                
                if result["passed"]:
                    self.passed_tests += 1
                    status = "✅"
                else:
                    status = "❌"
                
                print(f"{status} Case {i+1}: {input_data['trip_duration_days']} days, {input_data['miles_traveled']} miles, ${input_data['total_receipts_amount']} receipts")
                print(f"   Expected: ${expected:.2f}, Got: ${actual:.2f}, Error: ${error:.2f}")
                
            except ValueError:
                self.errors.append(f"Invalid output format from {script_path}: {output}")
                print(f"❌ Case {i+1}: Invalid output format: {output}")

    def test_edge_cases(self, script_path):
        """Test edge cases with extreme values"""
        edge_cases = [
            # Zero values
            {"input": {"trip_duration_days": 0, "miles_traveled": 0, "total_receipts_amount": 0}, "description": "All zeros"},
            # Very large values
            {"input": {"trip_duration_days": 100, "miles_traveled": 10000, "total_receipts_amount": 10000}, "description": "Very large values"},
            # Negative values (should handle gracefully)
            {"input": {"trip_duration_days": -1, "miles_traveled": 100, "total_receipts_amount": 100}, "description": "Negative days"},
            {"input": {"trip_duration_days": 5, "miles_traveled": -100, "total_receipts_amount": 100}, "description": "Negative miles"},
            {"input": {"trip_duration_days": 5, "miles_traveled": 100, "total_receipts_amount": -100}, "description": "Negative receipts"},
            # Decimal values
            {"input": {"trip_duration_days": 3.5, "miles_traveled": 100.5, "total_receipts_amount": 100.5}, "description": "Decimal values"},
            # Extreme ratios
            {"input": {"trip_duration_days": 1, "miles_traveled": 1000, "total_receipts_amount": 1}, "description": "High miles, low receipts"},
            {"input": {"trip_duration_days": 1, "miles_traveled": 1, "total_receipts_amount": 1000}, "description": "Low miles, high receipts"}
        ]
        
        print(f"\n🧪 Testing {len(edge_cases)} edge cases with {script_path}:")
        for i, case in enumerate(edge_cases):
            self.total_tests += 1
            input_data = case["input"]
            description = case["description"]
            
            output = self.run_script(
                script_path, 
                input_data["trip_duration_days"], 
                input_data["miles_traveled"], 
                input_data["total_receipts_amount"]
            )
            
            if output is None:
                print(f"❌ Edge Case {i+1} ({description}): Script execution failed")
                continue
                
            try:
                actual = float(output)
                print(f"✓ Edge Case {i+1} ({description}): ${actual:.2f}")
                
            except ValueError:
                self.errors.append(f"Invalid output format from {script_path}: {output}")
                print(f"❌ Edge Case {i+1} ({description}): Invalid output format: {output}")

    def compare_models(self):
        """Compare different model implementations on the same test cases"""
        models = [
            {"name": "Main Model", "path": "/app/run.sh"},
            {"name": "Polynomial Model", "path": "/app/run_polynomial.sh"},
            {"name": "ML Model", "path": "/app/run_ml.sh"}
        ]
        
        # Select 10 random test cases from the public dataset
        random_cases = random.sample(self.test_cases, 10)
        
        print("\n🔄 Comparing different model implementations:")
        for i, case in enumerate(random_cases):
            input_data = case["input"]
            expected = case["expected_output"]
            
            print(f"\nCase {i+1}: {input_data['trip_duration_days']} days, {input_data['miles_traveled']} miles, ${input_data['total_receipts_amount']} receipts")
            print(f"Expected: ${expected:.2f}")
            
            for model in models:
                output = self.run_script(
                    model["path"], 
                    input_data["trip_duration_days"], 
                    input_data["miles_traveled"], 
                    input_data["total_receipts_amount"]
                )
                
                if output is None:
                    print(f"❌ {model['name']}: Script execution failed")
                    continue
                    
                try:
                    actual = float(output)
                    error = abs(actual - expected)
                    print(f"{model['name']}: ${actual:.2f} (Error: ${error:.2f})")
                    
                except ValueError:
                    print(f"❌ {model['name']}: Invalid output format: {output}")

    def run_full_evaluation(self):
        """Run the full evaluation script and capture the output"""
        print("\n📊 Running full evaluation with eval.sh:")
        try:
            start_time = time.time()
            result = subprocess.run(["/app/eval.sh"], capture_output=True, text=True)
            elapsed_time = time.time() - start_time
            
            print(f"Evaluation completed in {elapsed_time:.2f} seconds")
            print(result.stdout)
            
            if result.stderr:
                print("Errors encountered:")
                print(result.stderr)
                
        except Exception as e:
            print(f"Error running evaluation script: {e}")

    def run_all_tests(self):
        """Run all tests"""
        print("🧾 Black Box Challenge - Reimbursement System Testing")
        print("===================================================")
        
        # Test sample cases with main implementation
        self.test_sample_cases("/app/run.sh")
        
        # Test edge cases
        self.test_edge_cases("/app/run.sh")
        
        # Compare different models
        self.compare_models()
        
        # Run full evaluation
        self.run_full_evaluation()
        
        # Print summary
        print("\n📋 Test Summary:")
        print(f"Total tests run: {self.total_tests}")
        print(f"Tests passed: {self.passed_tests}")
        print(f"Success rate: {(self.passed_tests / self.total_tests * 100):.1f}%")
        
        if self.errors:
            print("\n⚠️ Errors encountered:")
            for error in self.errors[:5]:  # Show only first 5 errors
                print(f"- {error}")
            if len(self.errors) > 5:
                print(f"... and {len(self.errors) - 5} more errors")

if __name__ == "__main__":
    tester = ReimbursementTester()
    tester.run_all_tests()
