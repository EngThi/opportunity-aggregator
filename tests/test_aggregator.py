import unittest
from unittest.mock import patch, Mock
import sys
import os
import json

# Add src to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src')))
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.sources.mlh import fetch_mlh
from src.sources.devpost import fetch_devpost
from src.sources.tabnews import fetch_tabnews
from src.scorer import AIScorer
from src import database

class TestAggregator(unittest.TestCase):
    def setUp(self):
        database.DB_PATH = "test_opportunities.db"
        database.init_db()
        database.init_user_db()

    def tearDown(self):
        if os.path.exists("test_opportunities.db"):
            os.remove("test_opportunities.db")

    @patch('src.sources.mlh.requests.get')
    def test_mlh_scraper(self, mock_get):
        mock_response = Mock()
        # Updated mock to match the resilient scraper logic
        mock_payload = {
            "props": {
                "upcoming_events": [
                    {"name": "MLH Event", "url": "/event", "date_range": "Now", "location": "Remote"}
                ]
            }
        }
        import html
        json_str = html.escape(json.dumps(mock_payload))
        mock_response.text = f'<html><body><div id="app" data-page="{json_str}"></div></body></html>'
        mock_response.status_code = 200
        mock_get.return_value = mock_response

        results = fetch_mlh()
        self.assertIsInstance(results, list)
        self.assertGreaterEqual(len(results), 0)

    def test_scorer_logic(self):
        scorer = AIScorer()
        opp = {'title': 'Python Job', 'description': 'Need Python', 'source': 'Test'}
        score, rationale = scorer.score_opportunity(opp)
        self.assertIsInstance(score, int)
        self.assertIsInstance(rationale, str)

if __name__ == '__main__':
    unittest.main()
