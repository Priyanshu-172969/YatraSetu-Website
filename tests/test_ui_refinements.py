"""
test_ui_refinements.py - Unit and Integration Tests for UI/UX Polish and Usability Fixes
Covers:
- Search autocomplete suggestions via datalist
- Multi-URL pipe parsing and URL scheme validation
- Removal of SQL jargon from user-facing deletion warnings
- Budget-empty and image-fallback states
- Zero-stop itinerary actions
- Modal accessibility and CSRF token integrity
- Category badge mapping filter
- Branded 400 error page
"""

import unittest
from unittest.mock import patch, MagicMock
from app import app, is_valid_http_url, category_badge


class TestUIRefinements(unittest.TestCase):

    def setUp(self):
        app.config['TESTING'] = True
        app.config['WTF_CSRF_ENABLED'] = False
        self.client = app.test_client()

    def test_category_badge_mapping(self):
        """Verifies category_badge filter correctly maps combined categories to CSS classes."""
        self.assertEqual(category_badge('Heritage'), 'badge-heritage')
        self.assertEqual(category_badge('Religious/Pilgrimage'), 'badge-religious')
        self.assertEqual(category_badge('Wildlife/Nature'), 'badge-wildlife')
        self.assertEqual(category_badge('Beach/Coastal'), 'badge-beach')
        self.assertEqual(category_badge('Beach/Nature'), 'badge-beach')
        self.assertEqual(category_badge('Nature/Mountain'), 'badge-nature')
        self.assertEqual(category_badge('Nature/Lake'), 'badge-nature')
        self.assertEqual(category_badge('Nature/Waterfall'), 'badge-nature')
        self.assertEqual(category_badge('Cultural'), 'badge-cultural')
        self.assertEqual(category_badge('Unknown/Custom'), 'badge-default')
        self.assertEqual(category_badge(None), 'badge-default')

    def test_url_validation_helper(self):
        """Verifies is_valid_http_url accepts valid http/https and rejects invalid schemes or plain text."""
        self.assertTrue(is_valid_http_url('https://asi.nic.in'))
        self.assertTrue(is_valid_http_url('http://example.com/path?query=1'))
        self.assertFalse(is_valid_http_url('ftp://ftp.example.com'))
        self.assertFalse(is_valid_http_url('javascript:alert(1)'))
        self.assertFalse(is_valid_http_url('not-a-url'))
        self.assertFalse(is_valid_http_url(''))
        self.assertFalse(is_valid_http_url(None))

    def test_search_suggestions_rendered_from_destinations(self):
        """Verifies destination name datalist suggestions are rendered in Destination Explorer."""
        mock_destinations = [
            {'destination_id': 1, 'place_name': 'Taj Mahal', 'locality_city': 'Agra', 'district': 'Agra', 'state_ut': 'Uttar Pradesh', 'category': 'Heritage', 'description': 'Mausoleum'}
        ]
        mock_names = [{'place_name': 'Hampi'}, {'place_name': 'Taj Mahal'}]

        def mock_fetch_all(query, params=None):
            if "DISTINCT place_name" in query:
                return mock_names
            if "DISTINCT state_ut" in query:
                return [{'state_ut': 'Uttar Pradesh'}]
            if "DISTINCT category" in query:
                return [{'category': 'Heritage'}]
            return mock_destinations

        with patch('app.fetch_all', side_effect=mock_fetch_all):
            with patch('app.fetch_one', return_value={'total': 1}):
                res = self.client.get('/destinations')
                self.assertEqual(res.status_code, 200)
                html = res.data.decode('utf-8')
                self.assertIn('list="destinationSuggestions"', html)
                self.assertIn('<datalist id="destinationSuggestions">', html)
                self.assertIn('<option value="Taj Mahal">', html)
                self.assertIn('<option value="Hampi">', html)

    def test_invalid_url_scheme_rejected_on_destination_create(self):
        """Verifies invalid URL scheme is rejected with a friendly message and input preserved."""
        form_data = {
            'place_name': 'Test Shrine',
            'locality_city': 'City',
            'district': 'District',
            'state_ut': 'State',
            'category': 'Heritage',
            'description': 'A historic site.',
            'best_time_to_visit': 'Winter',
            'how_to_reach': 'By road',
            'major_attractions': 'Main hall',
            'entry_fee_text': 'Free',
            'opening_hours_text': '9 AM - 5 PM',
            'primary_official_source_url': 'ftp://bad-scheme.org',
            'supporting_source_urls': '',
            'local_languages': 'Hindi, English'
        }
        res = self.client.post('/destinations/new', data=form_data, follow_redirects=True)
        self.assertEqual(res.status_code, 200)
        html = res.data.decode('utf-8')
        self.assertIn('Primary official portal URL must be a valid web address starting with http:// or https://', html)
        self.assertIn('Test Shrine', html)

    def test_valid_multiple_supporting_urls_accepted(self):
        """Verifies supporting_source_urls allows pipe-separated URLs."""
        form_data = {
            'place_name': 'Valid Temple',
            'locality_city': 'City',
            'district': 'District',
            'state_ut': 'State',
            'category': 'Heritage',
            'description': 'A historic site.',
            'best_time_to_visit': 'Winter',
            'how_to_reach': 'By road',
            'major_attractions': 'Main hall',
            'entry_fee_text': 'Free',
            'opening_hours_text': '9 AM - 5 PM',
            'primary_official_source_url': 'https://official.gov.in',
            'supporting_source_urls': 'https://asi.nic.in | https://whc.unesco.org',
            'local_languages': 'Hindi, English'
        }
        with patch('app.get_db_cursor') as mock_cursor_ctx:
            mock_cursor = MagicMock()
            mock_cursor.lastrowid = 101
            mock_cursor_ctx.return_value.__enter__.return_value = mock_cursor

            res = self.client.post('/destinations/new', data=form_data, follow_redirects=False)
            self.assertEqual(res.status_code, 302)
            self.assertIn('/destinations/101', res.headers['Location'])

    def test_deletion_warnings_free_from_sql_jargon(self):
        """Verifies that trip and destination deletion warnings contain no SQL syntax or constraint names."""
        mock_trips = [
            {
                'trip_id': 1,
                'trip_name': 'South Trail',
                'starting_city': 'Bengaluru',
                'planned_duration_days': 7,
                'notes': '',
                'created_at': None,
                'total_stops': 3
            },
            {
                'trip_id': 2,
                'trip_name': 'Empty Trail',
                'starting_city': 'New Delhi',
                'planned_duration_days': 4,
                'notes': '',
                'created_at': None,
                'total_stops': 0
            }
        ]
        with patch('app.fetch_all', side_effect=lambda q, p=None: mock_trips if 'trip_plans' in q else [{'starting_city': 'Bengaluru'}]):
            res = self.client.get('/trips')
            self.assertEqual(res.status_code, 200)
            html = res.data.decode('utf-8')

            # Ensure technical SQL constraint jargon is NOT in HTML
            self.assertNotIn('ON DELETE CASCADE', html)
            self.assertNotIn('ON DELETE RESTRICT', html)
            self.assertNotIn('trip_plan_destinations', html)
            self.assertNotIn('trip_plans', html)

            # Ensure friendly stop-dependent messages appear
            self.assertIn('This trip contains 3 scheduled destinations. Deleting the plan will also remove these stops.', html)
            self.assertIn('This trip has no scheduled destinations. Deleting the trip plan cannot be undone.', html)

    def test_empty_trip_card_has_actionable_links(self):
        """Verifies trips with zero stops show 'Add first destination' and 'Explore Destinations'."""
        mock_trips = [
            {
                'trip_id': 5,
                'trip_name': 'Fresh Journey',
                'starting_city': 'Kolkata',
                'planned_duration_days': 5,
                'notes': '',
                'created_at': None,
                'total_stops': 0
            }
        ]
        with patch('app.fetch_all', side_effect=lambda q, p=None: mock_trips if 'trip_plans' in q else [{'starting_city': 'Kolkata'}]):
            res = self.client.get('/trips')
            html = res.data.decode('utf-8')
            self.assertIn('Add first destination', html)
            self.assertIn('Explore Destinations', html)
            self.assertIn('/trips/5#addStopSection', html)

    def test_budget_empty_state_rendered(self):
        """Verifies destination without budget estimates renders designated polite academic prototype empty state."""
        mock_dest = {'destination_id': 99, 'place_name': 'New Unestimated Place', 'locality_city': 'Town', 'state_ut': 'State', 'category': 'Heritage'}

        def mock_fetch_all(query, params=None):
            if "destination_core" in query:
                return [mock_dest]
            return []  # No budget estimates exist for this destination

        with patch('app.fetch_all', side_effect=mock_fetch_all):
            with patch('app.fetch_one', return_value=mock_dest):
                # Request budget comparison for dest 99 which returns 0 estimates
                res = self.client.get('/budgets?destination_id=99')
                self.assertEqual(res.status_code, 200)
                html = res.data.decode('utf-8')
                self.assertIn('Budget estimates unavailable', html)
                self.assertIn('academic prototype contains predefined estimates', html)

    def test_modal_csrf_token_and_accessible_markup(self):
        """Verifies delete confirmation modal includes session CSRF token and accessible dialog attributes."""
        res = self.client.get('/')
        html = res.data.decode('utf-8')
        self.assertIn('id="deleteConfirmModal"', html)
        self.assertIn('role="dialog"', html)
        self.assertIn('aria-modal="true"', html)
        self.assertIn('name="csrf_token"', html)

    def test_branded_400_error_page(self):
        """Verifies 400 bad request returns branded error page."""
        app.config['WTF_CSRF_ENABLED'] = True
        res = self.client.post('/trips/create', data={})
        self.assertEqual(res.status_code, 400)
        html = res.data.decode('utf-8')
        self.assertIn('Unable to Process Request', html)
        self.assertIn('CSRF', html)
        self.assertIn('Refresh Page', html)


if __name__ == '__main__':
    unittest.main()
