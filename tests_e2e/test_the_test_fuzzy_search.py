from tests_e2e.fuzzy_search import FuzzySearch


def test_the_test_fuzzy_search():
    s = FuzzySearch[str]("aaa bbb ccc ddd\neee fff ggg")
    assert "aaa ccc" in s
    assert "aaa eee" not in s
    assert "eee fff ggg" in s
    assert "eee    fff " in s
