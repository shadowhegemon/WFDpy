#!/usr/bin/env python3

"""
Comprehensive test script for all new WFD Logger features added today
Tests: Dark mode, Band activity charts, and all backend functions
"""

import sys
import os
import requests
import json
from datetime import datetime

# Add the app directory to the Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Import functions from app
from app import (
    get_band_from_frequency, 
    get_band_activity_data,
    get_temporal_activity_data,
    get_mode_statistics
)

def test_band_conversion():
    """Test frequency to band conversion"""
    print("Testing Band Frequency Conversion...")
    print("=" * 50)
    
    test_cases = [
        (1.85, '160m'),
        (3.75, '80m'),
        (7.05, '40m'),
        (14.205, '20m'),
        (21.05, '15m'),
        (28.4, '10m'),
        (50.125, '6m'),
        (144.2, '2m'),
        (446.0, '70cm'),
        (999.9, '999.9MHz')  # Unknown frequency
    ]
    
    passed = 0
    failed = 0
    
    for freq, expected in test_cases:
        try:
            result = get_band_from_frequency(freq)
            if result == expected:
                print(f"PASS: {freq} MHz -> {result}")
                passed += 1
            else:
                print(f"FAIL: {freq} MHz -> {result} (expected {expected})")
                failed += 1
        except Exception as e:
            print(f"ERROR: {freq} MHz -> Exception: {e}")
            failed += 1
    
    print(f"\nBand Conversion Tests: {passed} passed, {failed} failed")
    return failed == 0

def test_analytics_functions():
    """Test the analytics data functions"""
    print("\nTesting Analytics Functions...")
    print("=" * 50)
    
    try:
        # Test band activity data
        band_data = get_band_activity_data()
        print(f"PASS: get_band_activity_data() returned: {type(band_data)}")
        print(f"  - Keys: {list(band_data.keys())}")
        
        # Test temporal activity data  
        temporal_data = get_temporal_activity_data()
        print(f"PASS: get_temporal_activity_data() returned: {type(temporal_data)}")
        print(f"  - Keys: {list(temporal_data.keys())}")
        
        # Test mode statistics
        mode_data = get_mode_statistics()
        print(f"PASS: get_mode_statistics() returned: {type(mode_data)}")
        print(f"  - Keys: {list(mode_data.keys())}")
        
        print("\nAnalytics Functions: All passed")
        return True
        
    except Exception as e:
        print(f"FAIL: Analytics functions error: {e}")
        return False


def test_web_routes():
    """Test web routes are accessible"""
    print("\nTesting Web Routes...")
    print("=" * 50)
    
    base_url = 'http://127.0.0.1:5000'
    routes_to_test = [
        ('/', 'Home page'),
        ('/log', 'Log contact page'),
        ('/contacts', 'Contacts page'),
        ('/stats', 'Statistics page'),
        ('/setup', 'Station setup page')
    ]
    
    passed = 0
    failed = 0
    
    for route, name in routes_to_test:
        try:
            response = requests.get(f"{base_url}{route}", timeout=5)
            if response.status_code == 200:
                print(f"PASS: {name} ({route}) - Status: {response.status_code}")
                passed += 1
            else:
                print(f"FAIL: {name} ({route}) - Status: {response.status_code}")
                failed += 1
        except requests.exceptions.RequestException as e:
            print(f"ERROR: {name} ({route}) - {e}")
            failed += 1
    
    print(f"\nRoute Tests: {passed} passed, {failed} failed")
    return failed == 0

def test_dark_mode_assets():
    """Test dark mode CSS file exists and is accessible"""
    print("\nTesting Dark Mode Assets...")
    print("=" * 50)
    
    css_file = 'static/css/dark-mode.css'
    
    try:
        if os.path.exists(css_file):
            with open(css_file, 'r') as f:
                content = f.read()
                if ':root' in content and '[data-bs-theme="dark"]' in content:
                    print("PASS: Dark mode CSS file exists and has required selectors")
                    return True
                else:
                    print("FAIL: Dark mode CSS missing required selectors")
                    return False
        else:
            print("FAIL: Dark mode CSS file not found")
            return False
    except Exception as e:
        print(f"ERROR: Cannot read dark mode CSS: {e}")
        return False

def test_template_inheritance():
    """Test that templates extend base.html"""
    print("\nTesting Template Inheritance...")
    print("=" * 50)
    
    templates_to_check = [
        'templates/index.html',
        'templates/log.html', 
        'templates/contacts.html',
        'templates/stats.html',
        'templates/about.html'
    ]
    
    passed = 0
    failed = 0
    
    for template in templates_to_check:
        try:
            if os.path.exists(template):
                with open(template, 'r') as f:
                    content = f.read()
                    if '{% extends "base.html" %}' in content:
                        print(f"PASS: {template} extends base.html")
                        passed += 1
                    else:
                        print(f"FAIL: {template} does not extend base.html")
                        failed += 1
            else:
                print(f"SKIP: {template} not found")
        except Exception as e:
            print(f"ERROR: Cannot read {template}: {e}")
            failed += 1
    
    print(f"\nTemplate Tests: {passed} passed, {failed} failed")
    return failed == 0

def main():
    """Run all tests"""
    print("WFD Logger New Features Test Suite")
    print("==================================")
    print(f"Test started at: {datetime.now()}")
    print()
    
    test_results = []
    
    # Run all tests
    test_results.append(("Band Conversion", test_band_conversion()))
    test_results.append(("Analytics Functions", test_analytics_functions()))
    test_results.append(("Web Routes", test_web_routes()))
    test_results.append(("Dark Mode Assets", test_dark_mode_assets()))
    test_results.append(("Template Inheritance", test_template_inheritance()))
    
    # Print summary
    print("\n" + "=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)
    
    total_passed = 0
    total_failed = 0
    
    for test_name, result in test_results:
        status = "PASS" if result else "FAIL"
        print(f"{test_name:<25} {status}")
        if result:
            total_passed += 1
        else:
            total_failed += 1
    
    print("=" * 60)
    print(f"Total: {total_passed} passed, {total_failed} failed")
    
    if total_failed == 0:
        print("🎉 ALL TESTS PASSED!")
    else:
        print("❌ SOME TESTS FAILED!")
    
    print(f"Test completed at: {datetime.now()}")
    
    return total_failed == 0

if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)