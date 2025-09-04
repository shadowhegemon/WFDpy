#!/usr/bin/env python3

"""
Integration test for WFD Logger - Test complete workflow
"""

import sys
import os
import requests
from bs4 import BeautifulSoup
import time

# Test configuration
BASE_URL = "http://127.0.0.1:5000"

def test_home_page():
    """Test that home page loads correctly"""
    print("Testing home page...")
    response = requests.get(f"{BASE_URL}/")
    
    if response.status_code == 200:
        if "WFD Logger" in response.text and "Winter Field Day" in response.text:
            print("PASS: Home page loads correctly")
            return True
        else:
            print("FAIL: Home page missing expected content")
            return False
    else:
        print(f"FAIL: Home page returned status {response.status_code}")
        return False

def test_log_page():
    """Test that log contact page loads correctly"""
    print("Testing log contact page...")
    response = requests.get(f"{BASE_URL}/log")
    
    if response.status_code == 200:
        if "Log New Contact" in response.text and "Exchange" in response.text:
            print("PASS: Log contact page loads correctly")
            return True
        else:
            print("FAIL: Log contact page missing expected content")
            return False
    else:
        print(f"FAIL: Log contact page returned status {response.status_code}")
        return False

def test_contacts_page():
    """Test that contacts page loads correctly"""
    print("Testing contacts page...")
    response = requests.get(f"{BASE_URL}/contacts")
    
    if response.status_code == 200:
        if "All Contacts" in response.text:
            print("PASS: Contacts page loads correctly")
            return True
        else:
            print("FAIL: Contacts page missing expected content")
            return False
    else:
        print(f"FAIL: Contacts page returned status {response.status_code}")
        return False

def test_stats_page():
    """Test that statistics page loads correctly"""
    print("Testing statistics page...")
    response = requests.get(f"{BASE_URL}/stats")
    
    if response.status_code == 200:
        if "Statistics" in response.text and "Total Contacts" in response.text:
            print("PASS: Statistics page loads correctly")
            return True
        else:
            print("FAIL: Statistics page missing expected content")
            return False
    else:
        print(f"FAIL: Statistics page returned status {response.status_code}")
        return False

def test_map_page():
    """Test that map page loads correctly"""
    print("Testing map page...")
    response = requests.get(f"{BASE_URL}/map")
    
    if response.status_code == 200:
        if "Contact Map" in response.text and "ARRL Sections" in response.text:
            print("PASS: Map page loads correctly")
            return True
        else:
            print("FAIL: Map page missing expected content")
            return False
    else:
        print(f"FAIL: Map page returned status {response.status_code}")
        return False

def test_svg_map():
    """Test that SVG map loads correctly"""
    print("Testing SVG map file...")
    response = requests.get(f"{BASE_URL}/static/us.svg")
    
    if response.status_code == 200:
        if response.headers.get('content-type') in ['image/svg+xml', 'text/xml', 'application/xml']:
            print("PASS: SVG map file loads with correct content type")
            return True
        elif '<svg' in response.text:
            print("PASS: SVG map file loads (content-type not set correctly but has SVG)")
            return True
        else:
            print("FAIL: SVG map file doesn't contain SVG content")
            return False
    else:
        print(f"FAIL: SVG map file returned status {response.status_code}")
        return False

if __name__ == "__main__":
    print("WFD Logger Integration Test Suite")
    print("=" * 40)
    
    # Give server time to fully start
    time.sleep(2)
    
    tests = [
        test_home_page,
        test_log_page,
        test_contacts_page,
        test_stats_page,
        test_map_page,
        test_svg_map
    ]
    
    passed = 0
    failed = 0
    
    for test_func in tests:
        try:
            if test_func():
                passed += 1
            else:
                failed += 1
        except Exception as e:
            print(f"ERROR in {test_func.__name__}: {e}")
            failed += 1
    
    print("\n" + "=" * 40)
    print(f"Integration Tests: {passed} passed, {failed} failed")
    
    if failed == 0:
        print("ALL INTEGRATION TESTS PASSED!")
        sys.exit(0)
    else:
        print("SOME INTEGRATION TESTS FAILED!")
        sys.exit(1)