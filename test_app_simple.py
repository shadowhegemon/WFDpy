#!/usr/bin/env python3

"""
Simplified Unit Tests for WFD Logger Application
Tests core functionality with proper Flask context handling
"""

import unittest
import tempfile
import os
from datetime import datetime, timedelta
from unittest.mock import patch, MagicMock

# Import the Flask app and components
import sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import (
    app, db, Contact, StationSetup,
    validate_wfd_exchange, extract_arrl_section, 
    get_band_from_frequency
)


class WFDLoggerTestCase(unittest.TestCase):
    """Base test case with database setup"""
    
    def setUp(self):
        """Set up test client and temporary database"""
        self.db_fd, app.config['DATABASE'] = tempfile.mkstemp()
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + app.config['DATABASE']
        app.config['TESTING'] = True
        app.config['WTF_CSRF_ENABLED'] = False
        
        self.app = app.test_client()
        self.app_context = app.app_context()
        self.app_context.push()
        
        db.create_all()
        
    def tearDown(self):
        """Clean up test database"""
        db.session.remove()
        db.drop_all()
        self.app_context.pop()
        os.close(self.db_fd)
        os.unlink(app.config['DATABASE'])


class TestValidationFunctions(unittest.TestCase):
    """Test WFD exchange validation functions (no database required)"""
    
    def test_validate_wfd_exchange_valid(self):
        """Test valid WFD exchange formats"""
        valid_exchanges = [
            "2I WI",
            "1H CA", 
            "3O NY",
            "1M TX"
        ]
        
        for exchange in valid_exchanges:
            with self.subTest(exchange=exchange):
                result = validate_wfd_exchange(exchange)
                self.assertTrue(result['valid'], f"Exchange '{exchange}' should be valid")
    
    def test_validate_wfd_exchange_invalid(self):
        """Test invalid WFD exchange formats"""
        invalid_exchanges = [
            "2I",        # Missing section
            "WI",        # Missing category  
            "",          # Empty
            "   "        # Whitespace only
        ]
        
        for exchange in invalid_exchanges:
            with self.subTest(exchange=exchange):
                result = validate_wfd_exchange(exchange)
                self.assertFalse(result['valid'], f"Exchange '{exchange}' should be invalid")
    
    def test_extract_arrl_section(self):
        """Test ARRL section extraction"""
        test_cases = [
            ("2I WI", "WI"),
            ("1H CA", "CA"), 
            ("3O NY", "NY"),
            ("", None),       # Empty
            (None, None)      # None input
        ]
        
        for exchange, expected in test_cases:
            with self.subTest(exchange=exchange):
                result = extract_arrl_section(exchange)
                self.assertEqual(result, expected)


class TestBandConversion(unittest.TestCase):
    """Test frequency to band conversion (no database required)"""
    
    def test_get_band_from_frequency(self):
        """Test amateur radio band conversion"""
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
        
        for freq, expected_band in test_cases:
            with self.subTest(freq=freq):
                result = get_band_from_frequency(freq)
                self.assertEqual(result, expected_band)


class TestDatabaseModels(WFDLoggerTestCase):
    """Test database models and basic operations"""
    
    def test_contact_creation(self):
        """Test creating a contact record"""
        contact = Contact(
            callsign='W1TEST',
            frequency='14.205',
            mode='SSB',
            exchange_sent='2I WI',
            exchange_received='1H CT',
            arrl_section='CT'
        )
        
        db.session.add(contact)
        db.session.commit()
        
        # Verify the contact was saved
        saved_contact = Contact.query.filter_by(callsign='W1TEST').first()
        self.assertIsNotNone(saved_contact)
        self.assertEqual(saved_contact.frequency, '14.205')
        self.assertEqual(saved_contact.mode, 'SSB')
    
    def test_station_setup_creation(self):
        """Test creating a station setup record"""
        station = StationSetup(
            setup_name='Test Station',
            station_callsign='W1TEST',
            operator_name='Test Operator',
            operator_callsign='W1OP',
            wfd_category='2I',
            arrl_section='WI',
            power_level='QRP',  # Add required field
            is_active=True
        )
        
        db.session.add(station)
        db.session.commit()
        
        # Verify the station was saved
        saved_station = StationSetup.query.filter_by(station_callsign='W1TEST').first()
        self.assertIsNotNone(saved_station)
        self.assertEqual(saved_station.wfd_category, '2I')
        self.assertTrue(saved_station.is_active)


class TestWebRoutes(WFDLoggerTestCase):
    """Test web routes and endpoints"""
    
    def test_home_route(self):
        """Test home page"""
        response = self.app.get('/')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Winter Field Day', response.data)
    
    def test_log_contact_route(self):
        """Test log contact page"""
        response = self.app.get('/log')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Log Contact', response.data)
    
    def test_contacts_route(self):
        """Test contacts list page"""
        response = self.app.get('/contacts')
        self.assertEqual(response.status_code, 200)
    
    def test_stats_route(self):
        """Test statistics page"""
        response = self.app.get('/stats')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Statistics', response.data)
    
    def test_setup_route(self):
        """Test station setup page"""
        response = self.app.get('/setup')
        self.assertEqual(response.status_code, 200)
    
    def test_about_route(self):
        """Test about page"""
        response = self.app.get('/about')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Winter Field Day', response.data)


class TestAnalyticsFunctionsWithContext(WFDLoggerTestCase):
    """Test analytics functions with proper Flask context"""
    
    def setUp(self):
        """Set up test data"""
        super().setUp()
        
        # Create test contacts
        test_contacts = [
            Contact(callsign='W1AW', frequency='14.205', mode='SSB', 
                   exchange_received='1H CT', arrl_section='CT'),
            Contact(callsign='K2ABC', frequency='7.05', mode='CW',
                   exchange_received='3O NY', arrl_section='NY'),
            Contact(callsign='VE3XYZ', frequency='21.05', mode='FT8',
                   exchange_received='1H ON', arrl_section='ON')
        ]
        
        for contact in test_contacts:
            db.session.add(contact)
        
        db.session.commit()
    
    def test_analytics_functions_import(self):
        """Test that analytics functions can be imported and called"""
        from app import get_band_activity_data, get_temporal_activity_data, get_mode_statistics
        
        # Test that functions exist and are callable
        self.assertTrue(callable(get_band_activity_data))
        self.assertTrue(callable(get_temporal_activity_data))
        self.assertTrue(callable(get_mode_statistics))
        
        # Test basic function calls (may return empty data with no contacts)
        try:
            band_data = get_band_activity_data()
            temporal_data = get_temporal_activity_data()
            mode_data = get_mode_statistics()
            
            # Basic structure checks
            self.assertIsInstance(band_data, dict)
            self.assertIsInstance(temporal_data, dict)
            self.assertIsInstance(mode_data, dict)
            
        except Exception as e:
            self.fail(f"Analytics functions failed: {e}")


class TestCallsignLookup(unittest.TestCase):
    """Test callsign lookup functions (mocked network calls)"""
    
    @patch('app.requests.get')
    def test_lookup_callsign_hamqth_success(self, mock_get):
        """Test successful HamQTH callsign lookup"""
        from app import lookup_callsign_hamqth
        
        # Mock successful response
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.content = b'''<?xml version="1.0" encoding="UTF-8"?>
        <HamQTH>
            <callsign>W1AW</callsign>
            <nick>Test Station</nick>
            <country>United States</country>
        </HamQTH>'''
        mock_get.return_value = mock_response
        
        result = lookup_callsign_hamqth('W1AW')
        
        self.assertIsNotNone(result)
        self.assertEqual(result.get('callsign'), 'W1AW')


class TestAPIEndpoints(WFDLoggerTestCase):
    """Test API endpoints"""
    
    def test_callsign_lookup_api_missing_param(self):
        """Test callsign lookup API without callsign parameter"""
        response = self.app.get('/lookup_callsign')
        self.assertEqual(response.status_code, 400)
        
        # Check if response contains error message
        self.assertIn(b'error', response.data.lower())


if __name__ == '__main__':
    # Create a test suite with all test cases
    test_suite = unittest.TestSuite()
    
    # Add all test classes
    test_classes = [
        TestValidationFunctions,
        TestBandConversion, 
        TestDatabaseModels,
        TestWebRoutes,
        TestAnalyticsFunctionsWithContext,
        TestCallsignLookup,
        TestAPIEndpoints
    ]
    
    for test_class in test_classes:
        tests = unittest.TestLoader().loadTestsFromTestCase(test_class)
        test_suite.addTests(tests)
    
    # Run the tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(test_suite)
    
    # Print summary
    print(f"\n{'='*60}")
    print("UNIT TEST SUMMARY")
    print(f"{'='*60}")
    print(f"Tests run: {result.testsRun}")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")
    
    if result.testsRun > 0:
        success_rate = ((result.testsRun - len(result.failures) - len(result.errors))/result.testsRun)*100
        print(f"Success rate: {success_rate:.1f}%")
    
    if result.failures:
        print(f"\nFAILURES ({len(result.failures)}):")
        for test, traceback in result.failures:
            print(f"- {test}")
    
    if result.errors:
        print(f"\nERRORS ({len(result.errors)}):")
        for test, traceback in result.errors:
            print(f"- {test}")
    
    print(f"{'='*60}")
    
    # Exit with appropriate code
    exit(0 if result.wasSuccessful() else 1)