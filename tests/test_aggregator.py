import unittest
from unittest.mock import patch, Mock
import sys
import os
import json
import sqlite3

# Add src to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src')))

from sources.mlh import fetch_mlh
from sources.devpost import fetch_devpost
from sources.tabnews import fetch_tabnews
from scorer import AIScorer
from database import init_db, save_opportunity, get_today_opportunities, search_opportunities, DB_PATH

class TestAggregator(unittest.TestCase):
    def setUp(self):
        # Override DB_PATH for testing
        import database
        self.original_db_path = database.DB_PATH
        database.DB_PATH = "test_opportunities.db"
        if os.path.exists("test_opportunities.db"):
            os.remove("test_opportunities.db")

        # Make sure env keys are removed to test fallback scorer
        if "GEMINI_API_KEY" in os.environ:
            del os.environ["GEMINI_API_KEY"]

        # Create a dummy user profile if missing
        with open("user_profile.md", "w", encoding="utf-8") as f:
            f.write("# User Profile\n- Skills: Python, Node.js\n- Interests: AI, hackathon\n")

    def tearDown(self):
        import database
        database.DB_PATH = self.original_db_path
        if os.path.exists("test_opportunities.db"):
            os.remove("test_opportunities.db")
        if os.path.exists("user_profile.md"):
            os.remove("user_profile.md")

    @patch('sources.mlh.requests.get')
    def test_mlh_scraper(self, mock_get):
        # Mock HTML payload with JSON embedded data matching MLH format
        mock_response = Mock()
        mock_response.content = b'<html><body><div id="app" data-page="{&quot;props&quot;: {&quot;upcomingEvents&quot;: [{&quot;name&quot;: &quot;Mock Hackathon&quot;, &quot;url&quot;: &quot;/mock&quot;, &quot;dateRange&quot;: &quot;Jan 1&quot;, &quot;location&quot;: &quot;Remote&quot;}]}}"></div></body></html>'
        mock_get.return_value = mock_response

        results = fetch_mlh()
        self.assertIsInstance(results, list)
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]['title'], 'Mock Hackathon')
        self.assertEqual(results[0]['source'], 'MLH')

    @patch('sources.devpost.requests.get')
    def test_devpost_scraper(self, mock_get):
        # Mock JSON response from Devpost API
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"hackathons": [{"title": "Mock Devpost Hackathon", "url": "http://devpost.mock", "prize_amount": "$10"}]}
        mock_get.return_value = mock_response

        results = fetch_devpost()
        self.assertIsInstance(results, list)
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]['title'], 'Mock Devpost Hackathon')
        self.assertEqual(results[0]['source'], 'Devpost')

    @patch('sources.tabnews.feedparser.parse')
    def test_tabnews_scraper(self, mock_parse):
        # Mock feedparser return object
        mock_feed = Mock()
        mock_entry = Mock()
        mock_entry.title = "Mock News"
        mock_entry.link = "http://tabnews.mock"
        mock_feed.entries = [mock_entry]
        mock_parse.return_value = mock_feed

        results = fetch_tabnews()
        self.assertIsInstance(results, list)
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]['title'], 'Mock News')
        self.assertEqual(results[0]['source'], 'TabNews')

    def test_scorer_fallback(self):
        scorer = AIScorer()
        opp = {
            'title': 'Test Python Hackathon',
            'description': 'A hackathon about AI and python',
            'source': 'test'
        }
        score, rationale = scorer.score_opportunity(opp)
        self.assertIsInstance(score, int)
        self.assertIsInstance(rationale, str)
        # Should be > 0 because of 'python' and 'hackathon' and 'ai'
        self.assertGreater(score, 0)
        self.assertIn("Fallback", rationale)

    def test_database_operations(self):
        import database
        database.init_db()
        self.assertTrue(os.path.exists("test_opportunities.db"))

        mock_data = {
            'title': 'Hackathon DB Test',
            'url': 'https://example.com/dbtest',
            'description': 'Test desc python',
            'source': 'Test',
            'type': 'Hackathon',
            'score': 85,
            'rationale': 'Matches Python'
        }

        # Test Save
        saved_count = database.save_opportunity([mock_data])
        self.assertEqual(saved_count, 1)

        # Test Save Duplicates
        saved_count2 = database.save_opportunity([mock_data])
        self.assertEqual(saved_count2, 0) # Integrity error handled silently, 0 saved

        # Test Get Today
        today_opps = database.get_today_opportunities()
        self.assertGreaterEqual(len(today_opps), 1)
        self.assertEqual(today_opps[0]['title'], 'Hackathon DB Test')

        # Test Search
        search_results = database.search_opportunities('python')
        self.assertGreaterEqual(len(search_results), 1)

if __name__ == '__main__':
    unittest.main()
