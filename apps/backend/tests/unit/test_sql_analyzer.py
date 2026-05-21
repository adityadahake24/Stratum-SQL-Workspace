import pytest
from app.services.sql_analyzer import SQLAnalyzer


@pytest.fixture
def analyzer():
    return SQLAnalyzer()


def test_select_is_readonly(analyzer):
    result = analyzer.analyze("SELECT * FROM users")
    assert result.is_read_only is True
    assert "SELECT" in result.statement_types
    assert result.risk_level == "low"
    assert result.undo_eligible is False


def test_insert_dml(analyzer):
    result = analyzer.analyze("INSERT INTO users (name) VALUES ('Alice')")
    assert result.is_read_only is False
    assert "INSERT" in result.statement_types
    assert result.undo_eligible is True
    assert result.needs_transaction_wrap is True


def test_update_with_where(analyzer):
    result = analyzer.analyze("UPDATE users SET name='Bob' WHERE id=1")
    assert "UPDATE" in result.statement_types
    assert result.has_dangerous_patterns is False
    assert result.risk_level == "medium"
    assert result.undo_eligible is True


def test_update_without_where(analyzer):
    result = analyzer.analyze("UPDATE users SET name='Bob'")
    assert result.has_dangerous_patterns is True
    assert result.risk_level == "high"
    assert len(result.warnings) > 0


def test_delete_without_where(analyzer):
    result = analyzer.analyze("DELETE FROM users")
    assert result.has_dangerous_patterns is True
    assert result.risk_level == "high"


def test_transaction_wrapping(analyzer):
    sql = "UPDATE users SET active=true WHERE id=1"
    wrapped = analyzer.wrap_in_transaction(sql)
    assert wrapped.startswith("BEGIN;")
    assert "COMMIT;" in wrapped


def test_existing_transaction_not_rewrapped(analyzer):
    sql = "BEGIN; UPDATE users SET x=1 WHERE id=1; COMMIT;"
    result = analyzer.analyze(sql)
    assert result.has_existing_transaction is True
    assert result.needs_transaction_wrap is False


def test_ddl_not_wrapped(analyzer):
    result = analyzer.analyze("CREATE TABLE foo (id serial PRIMARY KEY)")
    assert "DDL" in result.statement_types
    assert result.needs_transaction_wrap is False
