#!/usr/bin/env python3
import json
import sys
import re
import argparse

def extract_metrics_from_md(md_content):
    # Match <metric id="key">value</metric>
    pattern = re.compile(r'<metric\s+id="([^"]+)">([^<]+)</metric>')
    matches = pattern.findall(md_content)
    metrics = {}
    for key, val in matches:
        metrics[key] = val.strip()
    return metrics

def compare_values(report_val, ledger_val):
    # Convert both to strings and strip whitespace/commas for robust comparison
    r_val = str(report_val).replace(',', '').strip()
    l_val = str(ledger_val).replace(',', '').strip()
    
    # Try float comparison first
    try:
        if abs(float(r_val) - float(l_val)) < 1e-4:
            return True
    except ValueError:
        pass
        
    # Fallback to string comparison
    return r_val == l_val

def main():
    parser = argparse.ArgumentParser(description="Validate markdown report metrics against ledger.json")
    parser.add_argument("report_file", help="Path to the markdown report file")
    parser.add_argument("ledger_file", help="Path to the ledger.json file")
    args = parser.parse_args()

    try:
        with open(args.report_file, 'r', encoding='utf-8') as f:
            md_content = f.read()
    except Exception as e:
        print(f"[Firewall Error] Failed to read report file: {e}")
        sys.exit(1)
        
    try:
        with open(args.ledger_file, 'r', encoding='utf-8') as f:
            ledger_data = json.load(f)
    except Exception as e:
        print(f"[Firewall Error] Failed to read ledger.json: {e}")
        sys.exit(1)

    extracted_metrics = extract_metrics_from_md(md_content)
    
    if not extracted_metrics:
        print("[Firewall Warning] No <metric id=\"...\">...</metric> tags found in the report.")
        print("Static Validation requires at least one tagged metric to verify state consistency.")
        sys.exit(1)

    errors = []
    for key, report_val in extracted_metrics.items():
        if key not in ledger_data:
            errors.append(f"Metric '{key}' found in report but missing from ledger.json.")
            continue
            
        ledger_val = ledger_data[key]
        if not compare_values(report_val, ledger_val):
            errors.append(f"Mismatch for '{key}': Report says '{report_val}', but ledger says '{ledger_val}'.")

    if errors:
        print("\n[Firewall Reject] Static Validation Failed! Found discrepancies:")
        for err in errors:
            print(f" - {err}")
        print("\nAction Required: Please rewrite the erroneous numbers in the report to match the ledger exactly, then re-run this validation script.")
        sys.exit(1)
        
    print("\n[Firewall Pass] Static Validation Successful! All tagged metrics match the ledger perfectly.")
    sys.exit(0)

if __name__ == "__main__":
    main()
