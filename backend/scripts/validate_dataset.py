# backend/scripts/validate_dataset.py
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.services.validation_service import ValidationService

def main():
    print(f"============================================================")
    print(f" ColdChain IQ Data Integrity & Compliance Validator")
    print(f"============================================================")

    res = ValidationService.run_all_validations()
    print(f"\n Validation Completed at: {res['validation_timestamp']}")
    print(f" Overall Status: {res['overall_status']}")
    print(f" Summary: Total Rules: {res['summary']['total_rules']} | Passed: {res['summary']['passed']} | Warnings: {res['summary']['warnings']} | Failed: {res['summary']['failed']}")
    
    print("\n Rule Evaluation Details:")
    for r in res["results"]:
        status_symbol = "[PASS]" if r["status"] == "PASSED" else ("[WARN]" if r["status"] == "WARNING" else "[FAIL]")
        print(f" {status_symbol} {r['rule_name']}: Evaluated {r['total_evaluated']} records (Passed: {r['passed_count']}, Failed: {r['failed_count']}, Expected Anomalies: {r['expected_anomalies']})")

if __name__ == "__main__":
    main()
