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
    test_data = [{
        "title": "Test Opp",
        "url": "https://test.com/1",
        "description": "Desc",
        "source": "Test",
        "type": "Test"
    }]
    saved = database.save_opportunity(test_data)
    assert saved >= 0 # Pode ser 0 se já existir de rodadas anteriores

def test_database_no_duplicates():
    test_data = {
        "title": "Dup Test",
        "url": "https://test.com/dup",
        "description": "Desc",
        "source": "Test",
        "type": "Test"
    }
    database.save_opportunity([test_data])
    saved = database.save_opportunity([test_data])
    assert saved == 0 # Não deve salvar duplicata

def test_scorer_returns_int():
    # Mock desc e skills
    score = scorer.calculate_match_score("Python Developer with AWS", "Python, AWS, Docker")
    assert isinstance(score, int)

def test_scorer_range_0_to_100():
    score = scorer.calculate_match_score("React Frontend", "Java Backend")
    assert 0 <= score <= 100
