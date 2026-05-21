import pytest
import asyncio
from app.services.undo_engine import UndoEngine


@pytest.fixture
def engine():
    return UndoEngine()


@pytest.mark.asyncio
async def test_generate_inverse_update(engine):
    rows = [{"id": 1, "name": "Alice", "email": "a@b.com"}]
    sql = await engine.generate_inverse_sql("UPDATE", "users", "public", rows, pk_column="id")
    assert "UPDATE public.users SET" in sql
    assert "WHERE id = '1'" in sql


@pytest.mark.asyncio
async def test_generate_inverse_delete(engine):
    rows = [{"id": 1, "name": "Alice"}, {"id": 2, "name": "Bob"}]
    sql = await engine.generate_inverse_sql("DELETE", "users", "public", rows)
    assert "INSERT INTO public.users" in sql
    assert "VALUES" in sql


@pytest.mark.asyncio
async def test_generate_inverse_insert(engine):
    sql = await engine.generate_inverse_sql("INSERT", "users", "public", [], inserted_pks=[1, 2, 3])
    assert "DELETE FROM public.users" in sql
    assert "WHERE id IN" in sql


@pytest.mark.asyncio
async def test_empty_rows_returns_empty(engine):
    sql = await engine.generate_inverse_sql("UPDATE", "users", "public", [])
    assert sql == ""
