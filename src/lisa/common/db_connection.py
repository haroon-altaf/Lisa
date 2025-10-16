from __future__ import annotations

from collections.abc import Iterable
from pathlib import Path
from typing import Any

import pandas as pd
import sqlalchemy as db
from sqlalchemy.dialects.sqlite import insert

from lisa.utils import find_project_root

from .template_logger import TemplateLogger

root = find_project_root(Path(__file__).resolve())
SQLITE_PATH = root.joinpath("data").joinpath("Leading Indicators and Stocks.db")
ENGINE = db.create_engine(f"sqlite:///{SQLITE_PATH}")
METADATA = db.MetaData()
EXE_LIMIT = 32766

logger = TemplateLogger(__name__).logger


class DBConnection:
    """
    Class for handling database operations. Commit and rollback occur when context manager exits.
    """

    def __init__(self) -> None:
        self._connection = ENGINE.connect()

    def upsert_rows(
        self,
        table_name: str,
        data_rows: list[dict[str, Any]],
        delete_first: bool = False,
    ) -> None:
        table = db.Table(table_name, METADATA, autoload_with=ENGINE)
        pk_columns, name_types_dict = self._table_schema(table)
        incoming_name_types_dict = {name: type(value) for name, value in data_rows[0].items()}
        self._pre_load_checks(table, incoming_name_types_dict, name_types_dict)

        if delete_first:
            self._connection.execute(table.delete())

        n_col = len(data_rows[0])
        n_rows = len(data_rows)
        chunk_size = EXE_LIMIT // n_col
        n_chunks = int(n_rows / chunk_size) + (n_rows % chunk_size > 0)

        for i in range(n_chunks):
            data_rows_i = data_rows[i * chunk_size : (i + 1) * chunk_size]
            stmt = insert(table).values(data_rows_i)
            stmt = stmt.on_conflict_do_update(
                index_elements=pk_columns,
                set_={c.name: stmt.excluded[c.name] for c in table.columns if c.name not in pk_columns},
            )
            self._connection.execute(stmt)

        print(f"Successful upsert in {table_name}.")

    def _pre_load_checks(
        self,
        table: db.Table,
        incoming_name_types_dict: dict[str, Any],
        name_types_dict: dict[str, Any],
    ) -> None:
        new_columns = self._new_columns(incoming_name_types_dict.keys(), name_types_dict.keys())
        if new_columns:
            raise ValueError(
                f"Received column names must match column names in table: {table.name}.\nNew columns not in database:\n{sorted(list(new_columns))}."
            )

        missing_columns = self._missing_columns(incoming_name_types_dict.keys(), name_types_dict.keys())
        if missing_columns:
            logger.warning(
                f"The following columns exist in database but are missing from received data:\n{sorted(list(missing_columns))}"
            )

        type_mismatches = self._mismatching_types(incoming_name_types_dict, name_types_dict)
        if type_mismatches:
            raise ValueError(
                f"Received column types must match column types in table: {table.name}.\nMismatches:\n{type_mismatches}"
            )

    def df_from_sql(self, table_name: str) -> pd.DataFrame:
        return pd.read_sql_table(table_name, ENGINE)

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_type is None:
            self._connection.commit()
        else:
            self._connection.rollback()
        self._connection.close()

    @staticmethod
    def _table_schema(table: db.Table) -> tuple[list[str], dict[str, Any]]:
        primary_keys = [c.name for c in table.primary_key]
        types_dict = {c.name: c.type.python_type for c in table.columns}
        return primary_keys, types_dict

    @staticmethod
    def _new_columns(incoming_columns: Iterable, expected_columns: Iterable) -> set[str]:
        return set(incoming_columns) - set(expected_columns)

    @staticmethod
    def _missing_columns(incoming_columns: Iterable, expected_columns: Iterable) -> set[str]:
        return set(expected_columns) - set(incoming_columns)

    @staticmethod
    def _mismatching_types(
        incoming_types_dict: dict[str, Any], expected_types_dict: dict[str, Any]
    ) -> list[dict[str, Any]]:
        mismatches = [
            {
                "Column": name,
                "Received type": typ,
                "Required type": expected_types_dict[name],
            }
            for name, typ in incoming_types_dict.items()
            if typ
            not in {
                type(None),
                expected_types_dict[name],
                int
                if expected_types_dict[name] is float
                else type(None),  # relaxation: accept integers when floats expected; not vice versa
            }
        ]
        return mismatches
