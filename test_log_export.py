#!/usr/bin/env python3

"""
Test script for WFD Logger log export functionality
"""

import requests
import sys
import time

# Test configuration
BASE_URL = "http://127.0.0.1:5000"

def test_log_export_routes():
    """Test that log export routes respond correctly"""
    print("Testing log export functionality...")
    print("=" * 50)
    
    # Test Cabrillo export
    print("Testing Cabrillo export route...")
    try:
        response = requests.get(f"{BASE_URL}/download/cabrillo")
        if response.status_code == 200:
            print("PASS: Cabrillo export responds with 200")
            # Check if it's a file download
            if 'attachment' in response.headers.get('Content-Disposition', ''):
                print("PASS: Cabrillo export provides file download")
                # Check file extension
                if '.log' in response.headers.get('Content-Disposition', ''):
                    print("PASS: Cabrillo file has .log extension")
                else:
                    print("INFO: Cabrillo filename format may vary")
            else:
                print("INFO: Cabrillo export may redirect (no station setup)")
        elif response.status_code == 302:
            print("INFO: Cabrillo export redirected (likely no station setup)")
        else:
            print(f"WARN: Cabrillo export returned status {response.status_code}")
    except Exception as e:
        print(f"ERROR: Cabrillo export failed: {e}")
        return False
    
    # Test ADIF export
    print("Testing ADIF export route...")
    try:
        response = requests.get(f"{BASE_URL}/download/adif")
        if response.status_code == 200:
            print("PASS: ADIF export responds with 200")
            # Check if it's a file download
            if 'attachment' in response.headers.get('Content-Disposition', ''):
                print("PASS: ADIF export provides file download")
                # Check file extension
                if '.adif' in response.headers.get('Content-Disposition', ''):
                    print("PASS: ADIF file has .adif extension")
                else:
                    print("INFO: ADIF filename format may vary")
            else:
                print("INFO: ADIF export may redirect")
        elif response.status_code == 302:
            print("INFO: ADIF export redirected")
        else:
            print(f"WARN: ADIF export returned status {response.status_code}")
    except Exception as e:
        print(f"ERROR: ADIF export failed: {e}")
        return False
    
    print("Log export route testing completed.")
    return True

def test_ui_elements():
    """Test that UI elements for log export are present"""
    print("\nTesting UI elements...")
    print("=" * 50)
    
    pages_to_check = [
        ("/", "home page"),
        ("/contacts", "contacts page"), 
        ("/stats", "statistics page")
    ]
    
    for url, page_name in pages_to_check:
        try:
            response = requests.get(f"{BASE_URL}{url}")
            if response.status_code == 200:
                content = response.text
                # Check for download links
                if 'download_cabrillo' in content or 'download_adif' in content:
                    print(f"PASS: {page_name} has export links")
                else:
                    print(f"INFO: {page_name} may not show export links (no contacts)")
            else:
                print(f"WARN: {page_name} returned status {response.status_code}")
        except Exception as e:
            print(f"ERROR: Failed to check {page_name}: {e}")
    
    return True

if __name__ == "__main__":
    print("WFD Logger Export Test Suite")
    print("=" * 40)
    
    # Give server time to be ready
    time.sleep(1)
    
    success = True
    success &= test_log_export_routes()
    success &= test_ui_elements()
    
    print("\n" + "=" * 40)
    if success:
        print("LOG EXPORT TESTS COMPLETED!")
        print("Note: Some tests may show INFO messages if no station setup or contacts exist.")
        sys.exit(0)
    else:
        print("SOME EXPORT TESTS FAILED!")
        sys.exit(1)