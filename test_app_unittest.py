#!/usr/bin/env python3

"""
Comprehensive Unit Tests for WFD Logger Application
Tests all major functionality using Python unittest framework
"""

import unittest
import tempfile
import os
import json
from datetime import datetime, timedelta
from unittest.mock import patch, MagicMock

# Import the Flask app and components
import sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import (
    app, db, Contact, StationSetup, WFDObjective,
    validate_wfd_exchange, extract_arrl_section, 
    get_band_from_frequency, get_band_activity_data,
    get_temporal_activity_data, get_mode_statistics,
    calculate_wfd_score, check_duplicate_contact,
    get_active_station
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


class TestValidationFunctions(WFDLoggerTestCase):
    """Test WFD exchange validation functions"""
    
    def test_validate_wfd_exchange_valid(self):
        """Test valid WFD exchange formats"""
        valid_exchanges = [
            "2I WI",
            "1H CA", 
            "3O NY",
            "1M TX",
            "5I FL",
            "2M MX",
            "1H DX"
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
            "2B WI",     # Invalid class letter
            "0I WI",     # Zero not allowed
            "2I XX",     # Invalid section
            "2I WI NY",  # Too many parts
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
            ("1M TX", "TX"),
            ("5I NFL", "NFL"),
            ("2M MX", "MX"),
            ("1H DX", "DX"),
            ("2I XX", None),  # Invalid section
            ("2I", None),     # Missing section
            ("", None),       # Empty
            (None, None)      # None input
        ]
        
        for exchange, expected in test_cases:
            with self.subTest(exchange=exchange):
                result = extract_arrl_section(exchange)
                self.assertEqual(result, expected)


class TestBandConversion(WFDLoggerTestCase):
    """Test frequency to band conversion"""
    
    def test_get_band_from_frequency(self):
        """Test amateur radio band conversion"""
        test_cases = [
            (1.85, '160m'),
            (3.75, '80m'),
            (7.05, '40m'),
            (10.125, '30m'),
            (14.205, '20m'),
            (18.1, '17m'),
            (21.05, '15m'),
            (24.9, '12m'),
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


class TestAnalyticsFunctions(WFDLoggerTestCase):
    """Test analytics and statistics functions"""
    
    def setUp(self):
        """Set up test data"""
        super().setUp()
        
        # Create test station setup
        station = StationSetup(
            station_callsign='W1TEST',
            operator_name='Test Operator',
            operator_callsign='W1OP',
            wfd_category='2I',
            arrl_section='WI',
            is_active=True
        )
        db.session.add(station)
        
        # Create test contacts
        test_contacts = [
            Contact(callsign='W1AW', frequency='14.205', mode='SSB', 
                   exchange_sent='2I WI', exchange_received='1H CT',
                   arrl_section='CT', datetime=datetime.now() - timedelta(hours=2)),
            Contact(callsign='K2ABC', frequency='7.05', mode='CW',
                   exchange_sent='2I WI', exchange_received='3O NY', 
                   arrl_section='NY', datetime=datetime.now() - timedelta(hours=1)),
            Contact(callsign='VE3XYZ', frequency='21.05', mode='FT8',
                   exchange_sent='2I WI', exchange_received='1H ON',
                   arrl_section='ON', datetime=datetime.now())
        ]
        
        for contact in test_contacts:
            db.session.add(contact)
        
        db.session.commit()
    
    def test_get_band_activity_data(self):
        """Test band activity data generation"""
        data = get_band_activity_data()
        
        self.assertIn('band_counts', data)
        self.assertIn('modes_per_band', data)
        self.assertIn('hourly_activity', data)
        
        # Should have data for 20m, 40m, and 15m bands
        expected_bands = {'20m', '40m', '15m'}
        actual_bands = set(data['band_counts'].keys())
        self.assertEqual(actual_bands, expected_bands)
    
    def test_get_temporal_activity_data(self):
        """Test temporal activity data generation"""
        data = get_temporal_activity_data()
        
        self.assertIn('hourly_counts', data)
        self.assertIn('daily_counts', data) 
        self.assertIn('cumulative_data', data)
        
        # Should have 24 hours
        self.assertEqual(len(data['hourly_counts']), 24)
        
        # Should have cumulative data for 3 contacts
        self.assertEqual(len(data['cumulative_data']), 3)
    
    def test_get_mode_statistics(self):
        """Test mode statistics generation"""
        data = get_mode_statistics()
        
        self.assertIn('mode_counts', data)
        self.assertIn('mode_points', data)
        self.assertIn('mode_hourly', data)
        
        # Should have data for SSB, CW, and FT8
        expected_modes = {'SSB', 'CW', 'FT8'}
        actual_modes = set(data['mode_counts'].keys())
        self.assertEqual(actual_modes, expected_modes)
        
        # Check point calculations
        self.assertEqual(data['mode_points']['CW'], 2)  # CW = 2 points
        self.assertEqual(data['mode_points']['FT8'], 2)  # FT8 = 2 points  
        self.assertEqual(data['mode_points']['SSB'], 1)  # SSB = 1 point


class TestScoringSystem(WFDLoggerTestCase):
    """Test WFD scoring calculations"""
    
    def setUp(self):
        """Set up test data for scoring"""
        super().setUp()
        
        # Create test contacts with different modes and sections
        test_contacts = [
            Contact(callsign='W1AW', frequency='14.205', mode='SSB',
                   exchange_received='1H CT', arrl_section='CT'),
            Contact(callsign='K2ABC', frequency='7.05', mode='CW', 
                   exchange_received='3O NY', arrl_section='NY'),
            Contact(callsign='VE3XYZ', frequency='21.05', mode='FT8',
                   exchange_received='1H ON', arrl_section='ON'),
            Contact(callsign='W5DEF', frequency='14.205', mode='SSB',
                   exchange_received='2M TX', arrl_section='TX')
        ]
        
        for contact in test_contacts:
            db.session.add(contact)
        
        # Create test objectives
        objectives = [
            WFDObjective(name='Emergency Power', description='Test', points=100, completed=True),
            WFDObjective(name='Outdoor Setup', description='Test', points=100, completed=False)
        ]
        
        for obj in objectives:
            db.session.add(obj)
        
        db.session.commit()
    
    def test_calculate_wfd_score(self):
        """Test WFD score calculation"""
        score_data = calculate_wfd_score()
        
        # Check basic structure
        self.assertIn('contact_points', score_data)
        self.assertIn('multipliers', score_data)
        self.assertIn('base_score', score_data)
        self.assertIn('final_score', score_data)
        
        # Expected: SSB(1) + CW(2) + FT8(2) + SSB(1) = 6 points
        self.assertEqual(score_data['contact_points'], 6)
        
        # Expected: CT, NY, ON, TX = 4 unique sections
        self.assertEqual(score_data['multipliers'], 4)
        
        # Base score: 6 * 4 = 24
        self.assertEqual(score_data['base_score'], 24)
        
        # One completed objective (100 points bonus)
        self.assertEqual(score_data['completed_objectives_count'], 1)


class TestDuplicateDetection(WFDLoggerTestCase):
    """Test duplicate contact detection"""
    
    def setUp(self):
        """Set up test contacts"""
        super().setUp()
        
        # Create a contact 5 minutes ago
        old_contact = Contact(
            callsign='W1TEST',
            frequency='14.205',
            mode='SSB',
            datetime=datetime.now() - timedelta(minutes=5)
        )
        db.session.add(old_contact)
        db.session.commit()
    
    def test_check_duplicate_contacts(self):
        """Test duplicate contact checking"""
        # Test exact duplicate (same callsign within 10 minutes)
        result = check_duplicate_contact('W1TEST', '14.205', 'SSB')
        self.assertTrue(result['is_duplicate'])
        self.assertIsNotNone(result['exact_dupe'])
        
        # Test different callsign (no duplicate)
        result = check_duplicate_contact('K2DIFF', '14.205', 'SSB')
        self.assertFalse(result['is_duplicate'])
        self.assertIsNone(result['exact_dupe'])
        
        # Test same callsign but different band (band dupe)
        result = check_duplicate_contact('W1TEST', '7.05', 'SSB')
        self.assertFalse(result['is_duplicate'])  # Not exact dupe
        self.assertTrue(result['is_band_duplicate'])


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




class TestStationManagement(WFDLoggerTestCase):
    """Test station setup and management"""
    
    def test_get_active_station_none(self):
        """Test getting active station when none exists"""
        result = get_active_station()
        self.assertIsNone(result)
    
    def test_get_active_station_exists(self):
        """Test getting active station when one exists"""
        station = StationSetup(
            station_callsign='W1TEST',
            operator_name='Test Op',
            operator_callsign='W1OP',
            wfd_category='2I',
            arrl_section='WI',
            is_active=True
        )
        db.session.add(station)
        db.session.commit()
        
        result = get_active_station()
        self.assertIsNotNone(result)
        self.assertEqual(result.station_callsign, 'W1TEST')
        self.assertTrue(result.is_active)




if __name__ == '__main__':
    # Create a test suite with all test cases
    test_suite = unittest.TestSuite()
    
    # Add all test classes
    test_classes = [
        TestValidationFunctions,
        TestBandConversion, 
        TestAnalyticsFunctions,
        TestScoringSystem,
        TestDuplicateDetection,
        TestWebRoutes,
        TestStationManagement
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
    print(f"Success rate: {((result.testsRun - len(result.failures) - len(result.errors))/result.testsRun)*100:.1f}%")
    
    if result.failures:
        print(f"\nFAILURES ({len(result.failures)}):")
        for test, traceback in result.failures:
            print(f"- {test}: {traceback.split('AssertionError:')[-1].strip()}")
    
    if result.errors:
        print(f"\nERRORS ({len(result.errors)}):")
        for test, traceback in result.errors:
            print(f"- {test}: {traceback.split(':', 1)[-1].strip()}")
    
    print(f"{'='*60}")
    
    # Exit with appropriate code
    exit(0 if result.wasSuccessful() else 1)