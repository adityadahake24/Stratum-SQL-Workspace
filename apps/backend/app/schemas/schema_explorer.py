from typing import List, Optional
from pydantic import BaseModel


class SchemaInfo(BaseModel):
    name: str
    owner: Optional[str] = None


class TableInfo(BaseModel):
    name: str
    schema: str
    table_type: str  # BASE TABLE / VIEW
    row_estimate: Optional[int] = None
    comment: Optional[str] = None


class ColumnInfo(BaseModel):
    name: str
    data_type: str
    is_nullable: bool
    column_default: Optional[str] = None
    is_primary_key: bool = False
    ordinal_position: int


class IndexInfo(BaseModel):
    name: str
    columns: List[str]
    is_unique: bool
    is_primary: bool


class FKInfo(BaseModel):
    constraint_name: str
    column_name: str
    foreign_table: str
    foreign_column: str
