#!/usr/bin/env python3

"""
Test script for WFD Logger validation functionality
"""

import sys
import os

# Add the app directory to the Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Import our validation functions
from app import validate_wfd_exchange, extract_arrl_section

def test_exchange_validation():
    """Test the WFD exchange validation function"""
    print("Testing WFD Exchange Validation...")
    print("=" * 50)
    
    # Test cases: (exchange, expected_valid, description)
    test_cases = [
        # Valid exchanges
        ("2I WI", True, "Valid: 2I WI"),
        ("1H CA", True, "Valid: 1H CA"),
        ("3O NY", True, "Valid: 3O NY"),
        ("1M TX", True, "Valid: 1M TX"),
        ("5I FL", True, "Valid: 5I FL"),
        ("2M MX", True, "Valid: 2M MX (Mexico)"),
        ("1H DX", True, "Valid: 1H DX (Other countries)"),
        
        # Invalid exchanges
        ("2I", False, "Invalid: Missing section"),
        ("WI", False, "Invalid: Missing category"),
        ("2B WI", False, "Invalid: Bad class letter (B not valid in 2026)"),
        ("0I WI", False, "Invalid: Zero not allowed"),
        ("2I XX", False, "Invalid: Invalid ARRL section"),
        ("2I WI CA", False, "Invalid: Too many parts"),
        ("", False, "Invalid: Empty exchange"),
        ("  ", False, "Invalid: Whitespace only"),
    ]
    
    passed = 0
    failed = 0
    
    for exchange, expected_valid, description in test_cases:
        is_valid, message = validate_wfd_exchange(exchange)
        
        if is_valid == expected_valid:
            print(f"PASS: {description}")
            passed += 1
        else:
            print(f"FAIL: {description}")
            print(f"   Expected: {expected_valid}, Got: {is_valid}")
            print(f"   Message: {message}")
            failed += 1
    
    print(f"\nValidation Tests: {passed} passed, {failed} failed")
    return failed == 0

def test_arrl_section_extraction():
    """Test the ARRL section extraction function"""
    print("\nTesting ARRL Section Extraction...")
    print("=" * 50)
    
    # Test cases: (exchange, expected_section, description)
    test_cases = [
        ("2I WI", "WI", "Extract WI from 2I WI"),
        ("1H CA", "CA", "Extract CA from 1H CA"),
        ("3O NY", "NY", "Extract NY from 3O NY"),
        ("1M TX", "TX", "Extract TX from 1M TX"),
        ("5I NFL", "NFL", "Extract NFL from 5I NFL"),
        ("2M MX", "MX", "Extract MX from 2M MX"),
        ("1H DX", "DX", "Extract DX from 1H DX"),
        ("2I XX", None, "Invalid section XX"),
        ("2I", None, "Missing section"),
        ("WI", None, "Only section, no category"),
        ("", None, "Empty exchange"),
        (None, None, "None input"),
    ]
    
    passed = 0
    failed = 0
    
    for exchange, expected_section, description in test_cases:
        extracted_section = extract_arrl_section(exchange)
        
        if extracted_section == expected_section:
            print(f"PASS: {description}")
            passed += 1
        else:
            print(f"FAIL: {description}")
            print(f"   Expected: {expected_section}, Got: {extracted_section}")
            failed += 1
    
    print(f"\nExtraction Tests: {passed} passed, {failed} failed")
    return failed == 0

if __name__ == "__main__":
    print("WFD Logger Test Suite")
    print("=====================\n")
    
    validation_passed = test_exchange_validation()
    extraction_passed = test_arrl_section_extraction()
    
    print("\n" + "=" * 50)
    if validation_passed and extraction_passed:
        print("ALL TESTS PASSED!")
        sys.exit(0)
    else:
        print("SOME TESTS FAILED!")
        sys.exit(1)