"""
test_final_refinements.py - Unit and Integration Tests for Final Refinements:
- Trip stop update route (/trips/<id>/stops/<id>/update) and MySQL persistence
- Edit stop modal and live-save status indicator in trip detail
- Empty itinerary 'Add First Stop' navigation control
- Budget duration clarity and grammatical pluralization (no '1 Nights')
- Budget round-trip transit and methodology explanation
- Standalone vector logo.svg validation
"""

import unittest
from unittest.mock import patch, MagicMock
from app import app


class TestFinalRefinements(unittest.TestCase):

    def setUp(self):
        app.config['TESTING'] = True
        app.config['WTF_CSRF_ENABLED'] = False
        self.client = app.test_client()

    def test_trip_detail_renders_live_saved_and_edit_controls(self):
        """Verifies trip detail renders instant-save indicator, edit stop triggers, and edit modal."""
        mock_trip = {
            'trip_id': 101,
            'trip_name': 'Golden Triangle Tour',
            'starting_city': 'New Delhi',
            'planned_duration_days': 5,
            'notes': 'Heritage tour',
            'created_at': None
        }
        mock_stops = [
            {
                'stop_id': 1,
                'trip_id': 101,
                'destination_id': 1,
                'visit_order': 1,
                'planned_days': 2,
                'stop_notes': 'Visit at sunrise',
                'place_name': 'Taj Mahal',
                'locality_city': 'Agra',
                'state_ut': 'Uttar Pradesh',
                'category': 'Heritage'
            }
        ]
        with patch('app.fetch_one', return_value=mock_trip):
            with patch('app.fetch_all', side_effect=[mock_stops, [{'destination_id': 1, 'place_name': 'Taj Mahal', 'state_ut': 'UP'}]]):
                res = self.client.get('/trips/101')
                self.assertEqual(res.status_code, 200)
                html = res.data.decode('utf-8')
                res.close()

                # Live Saved status indicator
                self.assertIn('Live Saved to MySQL', html)

                # Edit Stop button & modal
                self.assertIn('btn-edit-stop', html)
                self.assertIn('id="editStopModal"', html)
                self.assertIn('Save Changes', html)
                self.assertIn('/trips/101/stops/1/update', html)

    def test_empty_itinerary_renders_add_first_stop_button(self):
        """Verifies empty itinerary panel renders the designated Add First Stop control."""
        mock_trip = {
            'trip_id': 102,
            'trip_name': 'Empty Expedition',
            'starting_city': 'Bengaluru',
            'planned_duration_days': 3,
            'notes': '',
            'created_at': None
        }
        with patch('app.fetch_one', return_value=mock_trip):
            with patch('app.fetch_all', side_effect=[[], [{'destination_id': 1, 'place_name': 'Taj Mahal', 'state_ut': 'UP'}]]):
                res = self.client.get('/trips/102')
                self.assertEqual(res.status_code, 200)
                html = res.data.decode('utf-8')
                res.close()

                self.assertIn('id="addFirstStopBtn"', html)
                self.assertIn('href="#addStopSection"', html)
                self.assertIn('Add First Stop', html)

    def test_trip_update_stop_route_validates_and_executes(self):
        """Verifies /trips/<trip_id>/stops/<stop_id>/update validates input and executes SQL update."""
        mock_trip = {'trip_id': 101}
        mock_stop = {'stop_id': 1, 'visit_order': 1}

        with patch('app.fetch_one', side_effect=[mock_trip, mock_stop]):
            with patch('app.execute_query') as mock_exec:
                res = self.client.post('/trips/101/stops/1/update', data={
                    'planned_days': '3',
                    'stop_notes': 'Updated sunset schedule'
                }, follow_redirects=False)

                self.assertEqual(res.status_code, 302)
                res.close()
                mock_exec.assert_called_once()
                sql = mock_exec.call_args[0][0]
                params = mock_exec.call_args[0][1]
                self.assertIn('UPDATE trip_plan_destinations', sql)
                self.assertEqual(params[0], 3)
                self.assertEqual(params[1], 'Updated sunset schedule')
                self.assertEqual(params[2], 1)
                self.assertEqual(params[3], 101)

    def test_trip_update_stop_rejects_invalid_days(self):
        """Verifies /trips/<trip_id>/stops/<stop_id>/update rejects zero or negative days."""
        mock_trip = {'trip_id': 101}
        mock_stop = {'stop_id': 1, 'visit_order': 1}

        with patch('app.fetch_one', side_effect=[mock_trip, mock_stop]):
            with patch('app.execute_query') as mock_exec:
                res = self.client.post('/trips/101/stops/1/update', data={
                    'planned_days': '0',
                    'stop_notes': 'Invalid'
                }, follow_redirects=False)

                self.assertEqual(res.status_code, 302)
                res.close()
                mock_exec.assert_not_called()

    def test_budget_duration_clarity_rendering(self):
        """Verifies budget comparison presents grammatically correct duration and methodology notes."""
        mock_dest = {
            'destination_id': 1,
            'place_name': 'Taj Mahal',
            'locality_city': 'Agra',
            'district': 'Agra',
            'state_ut': 'Uttar Pradesh',
            'category': 'Heritage',
            'description': 'Mausoleum'
        }
        mock_estimates = [
            {
                'budget_id': 1,
                'destination_id': 1,
                'starting_city': 'New Delhi',
                'trip_duration_days': 1,
                'accommodation_nights': 0,
                'transport_mode': 'Express Rail',
                'transport_class': 'Chair Car',
                'target_travel_period': 'Winter',
                'long_distance_round_trip_cost_inr': 700.0,
                'onward_transport_cost_inr': 0.0,
                'local_transport_cost_inr': 200.0,
                'accommodation_cost_inr': 0.0,
                'food_and_water_cost_inr': 400.0,
                'entry_and_mandatory_fees_inr': 50.0,
                'other_essential_cost_inr': 50.0,
                'contingency_cost_inr': 100.0,
                'estimated_total_budget_inr': 1500.0,
                'confidence_level': 'High',
                'date_checked': '2026-10-15',
                'limitations': 'Peak season ticket demand',
                'calculation_methodology': 'Calculated as day excursion.'
            },
            {
                'budget_id': 2,
                'destination_id': 1,
                'starting_city': 'Kolkata',
                'trip_duration_days': 3,
                'accommodation_nights': 1,
                'transport_mode': 'Superfast Rail',
                'transport_class': 'Sleeper',
                'target_travel_period': 'Winter',
                'long_distance_round_trip_cost_inr': 1800.0,
                'onward_transport_cost_inr': 0.0,
                'local_transport_cost_inr': 350.0,
                'accommodation_cost_inr': 1200.0,
                'food_and_water_cost_inr': 900.0,
                'entry_and_mandatory_fees_inr': 50.0,
                'other_essential_cost_inr': 100.0,
                'contingency_cost_inr': 300.0,
                'estimated_total_budget_inr': 4700.0,
                'confidence_level': 'High',
                'date_checked': '2026-10-15',
                'limitations': '',
                'calculation_methodology': 'Includes 2 transit days and 1 night stay.'
            }
        ]

        def mock_fetch_all(query, params=None):
            if "budget_estimates" in query:
                return mock_estimates
            return [{'destination_id': 1, 'place_name': 'Taj Mahal', 'locality_city': 'Agra', 'state_ut': 'UP', 'category': 'Heritage'}]

        with patch('app.fetch_one', return_value=mock_dest):
            with patch('app.fetch_all', side_effect=mock_fetch_all):
                res = self.client.get('/budgets?destination_id=1')
                self.assertEqual(res.status_code, 200)
                html = res.data.decode('utf-8')
                res.close()

                # Grammatically correct: 1 Day, 0 Nights (Day Excursion)
                self.assertIn('1 Day Total Trip', html)
                self.assertIn('Day Excursion (0 Nights)', html)
                self.assertNotIn('1 Days', html)
                self.assertNotIn('1 Nights', html)

                # Grammatically correct: 1 Night Stay, 3 Days
                self.assertIn('3 Days Total Trip', html)
                self.assertIn('1 Night Stay', html)

                # Methodology explanation
                self.assertIn('Understanding Trip Duration & Transport Assumptions', html)
                self.assertIn('Long-Distance Transit (Round-Trip)', html)

    def test_standalone_vector_svg_logo(self):
        """Verifies logo.svg is a valid standalone SVG with heritage pin geometry."""
        import os
        svg_path = os.path.join(app.root_path, 'static', 'images', 'logo.svg')
        self.assertTrue(os.path.exists(svg_path))
        with open(svg_path, 'r', encoding='utf-8') as f:
            content = f.read()

        self.assertIn('<svg', content)
        self.assertIn('YatraSetu Heritage Pin Logo', content)
        self.assertIn('pinTerracotta', content)
        self.assertIn('shoreTemple', content)
        self.assertIn('sanchiStupa', content)
        self.assertIn('nagaraTemple', content)
        self.assertIn('tajMahal', content)


if __name__ == '__main__':
    unittest.main()
