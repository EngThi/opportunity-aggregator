import pytest
from src import database, scorer
from src.sources import tabnews

def test_parser_returns_list():
    results = tabnews.fetch_tabnews()
    assert isinstance(results, list)
    if len(results) > 0:
        assert "title" in results[0]
        assert "url" in results[0]

def test_database_saves_opportunity():
    database.init_db() # Garante que a tabela existe
    test_data = [{
        "title": "Test Opp",
        "url": "https://test.com/1",
        "description": "Desc",
        "source": "Test",
        "type": "Test"
    }]
    saved = database.save_opportunity(test_data)
    assert saved >= 0

def test_database_no_duplicates():
    database.init_db() # Garante que a tabela existe
    test_data = {
        "title": "Dup Test",
        "url": "https://test.com/dup",
        "description": "Desc",
        "source": "Test",
        "type": "Test"
    }
    database.save_opportunity([test_data])
    saved = database.save_opportunity([test_data])
    assert saved == 0 

def test_scorer_returns_int():
    score, rationale = scorer.AIScorer().score_opportunity({"title": "Python Dev", "description": "AWS", "source": "Test"})
    assert isinstance(score, int)

def test_scorer_range_0_to_100():
    score, rationale = scorer.AIScorer().score_opportunity({"title": "React Frontend", "description": "Java", "source": "Test"})
    assert 0 <= score <= 100
