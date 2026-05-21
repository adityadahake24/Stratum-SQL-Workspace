from typing import List, Optional
from dataclasses import dataclass, field

import sqlglot
import sqlglot.expressions as exp
import structlog

logger = structlog.get_logger(__name__)

DML_TYPES = {"INSERT", "UPDATE", "DELETE"}
DDL_TYPES = {"CREATE", "ALTER", "DROP", "TRUNCATE", "RENAME"}
TCL_TYPES = {"BEGIN", "COMMIT", "ROLLBACK", "SAVEPOINT"}
READ_TYPES = {"SELECT", "WITH"}


@dataclass
class SQLAnalysisResult:
    statement_types: List[str] = field(default_factory=list)
    needs_transaction_wrap: bool = False
    has_existing_transaction: bool = False
    undo_eligible: bool = False
    target_tables: List[str] = field(default_factory=list)
    is_read_only: bool = True
    has_dangerous_patterns: bool = False
    risk_level: str = "low"
    warnings: List[str] = field(default_factory=list)

    def dict(self):
        return {
            "statement_types": self.statement_types,
            "needs_transaction_wrap": self.needs_transaction_wrap,
            "has_existing_transaction": self.has_existing_transaction,
            "undo_eligible": self.undo_eligible,
            "target_tables": self.target_tables,
            "is_read_only": self.is_read_only,
            "has_dangerous_patterns": self.has_dangerous_patterns,
            "risk_level": self.risk_level,
            "warnings": self.warnings,
        }


class SQLAnalyzer:
    def analyze(self, sql: str) -> SQLAnalysisResult:
        result = SQLAnalysisResult()
        try:
            statements = sqlglot.parse(sql, dialect="postgres")
        except Exception as e:
            logger.warning("sql_parse_error", error=str(e))
            result.warnings.append(f"SQL parse warning: {e}")
            return result

        stmt_types: List[str] = []
        target_tables: List[str] = []
        has_dml = False
        has_tcl = False

        for stmt in statements:
            if stmt is None:
                continue

            stmt_type = type(stmt).__name__.upper()

            if isinstance(stmt, exp.Select):
                stmt_types.append("SELECT")
            elif isinstance(stmt, exp.Insert):
                stmt_types.append("INSERT")
                has_dml = True
                tbl = self._extract_table(stmt)
                if tbl:
                    target_tables.append(tbl)
            elif isinstance(stmt, exp.Update):
                stmt_types.append("UPDATE")
                has_dml = True
                tbl = self._extract_table(stmt)
                if tbl:
                    target_tables.append(tbl)
                if not self._has_where(stmt):
                    result.has_dangerous_patterns = True
                    result.warnings.append("UPDATE without WHERE clause — this will affect all rows")
            elif isinstance(stmt, exp.Delete):
                stmt_types.append("DELETE")
                has_dml = True
                tbl = self._extract_table(stmt)
                if tbl:
                    target_tables.append(tbl)
                if not self._has_where(stmt):
                    result.has_dangerous_patterns = True
                    result.warnings.append("DELETE without WHERE clause — this will delete all rows")
            elif isinstance(stmt, (exp.Create, exp.Drop, exp.AlterTable, exp.Command)):
                stmt_types.append("DDL")
            elif isinstance(stmt, exp.Transaction):
                stmt_types.append("TCL")
                has_tcl = True
            elif isinstance(stmt, (exp.Commit, exp.Rollback)):
                stmt_types.append("TCL")
                has_tcl = True
            elif isinstance(stmt, exp.With):
                # CTE — check inner query
                inner = stmt.find(exp.Select, exp.Insert, exp.Update, exp.Delete)
                if inner:
                    if isinstance(inner, (exp.Insert, exp.Update, exp.Delete)):
                        has_dml = True
                        stmt_types.append(type(inner).__name__.upper())
                    else:
                        stmt_types.append("SELECT")
                else:
                    stmt_types.append("SELECT")
            else:
                stmt_types.append("OTHER")

        result.statement_types = list(dict.fromkeys(stmt_types))  # deduplicate, preserve order
        result.target_tables = list(dict.fromkeys(target_tables))
        result.has_existing_transaction = has_tcl

        dml_set = {t for t in stmt_types if t in DML_TYPES}
        ddl_set = {t for t in stmt_types if t in {"DDL"}}
        result.is_read_only = not has_dml and not ddl_set

        result.needs_transaction_wrap = (
            has_dml
            and not has_tcl
            and not ddl_set  # DDL auto-commits in PG
        )

        result.undo_eligible = (
            has_dml
            and len(dml_set) == 1  # single operation type only
            and not has_tcl
            and not ddl_set
        )

        if result.has_dangerous_patterns:
            result.risk_level = "high"
        elif ddl_set or "UPDATE" in dml_set or "DELETE" in dml_set:
            result.risk_level = "medium"
        else:
            result.risk_level = "low"

        logger.debug(
            "sql_analyzed",
            statement_types=result.statement_types,
            risk_level=result.risk_level,
            undo_eligible=result.undo_eligible,
        )
        return result

    def wrap_in_transaction(self, sql: str) -> str:
        sql = sql.strip().rstrip(";")
        return f"BEGIN;\n{sql};\nCOMMIT;"

    def detect_missing_where(self, sql: str) -> bool:
        analysis = self.analyze(sql)
        return analysis.has_dangerous_patterns

    def extract_affected_tables(self, sql: str) -> List[str]:
        analysis = self.analyze(sql)
        return analysis.target_tables

    def _extract_table(self, stmt) -> Optional[str]:
        try:
            tbl = stmt.find(exp.Table)
            if tbl:
                db = tbl.args.get("db")
                schema = tbl.args.get("db") or tbl.args.get("catalog")
                name = tbl.name
                if hasattr(tbl, "args"):
                    schema_node = tbl.args.get("db")
                    if schema_node:
                        return f"{schema_node}.{name}"
                return name
        except Exception:
            pass
        return None

    def _has_where(self, stmt) -> bool:
        return stmt.find(exp.Where) is not None


sql_analyzer = SQLAnalyzer()
