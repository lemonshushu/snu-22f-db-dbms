from datetime import datetime
from typing import TypedDict, Literal, Any

"""Type Aliases"""

ColumnName = str
TableName = str
DataType = tuple[Literal['int', 'char', 'date'], int | None]
ColumnNameList = list[ColumnName]
ReferentialConstraint = tuple[Literal['ref'],
                              ColumnNameList, TableName, ColumnNameList]
PrimaryKeyConstraint = tuple[Literal['pkey'], ColumnNameList]
TableConstraintDefinition = tuple[Literal['cons'],
                                  ReferentialConstraint | PrimaryKeyConstraint]
ColumnDefinition = tuple[Literal['col'], ColumnName, DataType, bool]
TableElement = ColumnDefinition | TableConstraintDefinition
TableElementList = list[TableElement]

Value = int | str | datetime | None
ValueList = list[Value]

WhereClause = Any
T_A = tuple[TableName, TableName | None]  # T_A means TableName+Alias
C_A = tuple[TableName | None, ColumnName, ColumnName | None]  # (table_name, column_name, alias)

CreateTableQuery = tuple[Literal['create_table'], TableName, TableElementList]
SelectQuery = tuple[Literal['select'], list[C_A], list[T_A], WhereClause | None]
InsertQuery = tuple[Literal['insert'],
                    TableName, ColumnNameList | None, ValueList]
DeleteQuery = tuple[Literal['delete'], TableName, WhereClause | None]
UpdateQuery = tuple[Literal['update'], TableName, ColumnName, Value, WhereClause]
DropTableQuery = tuple[Literal['drop_table'], TableName]
DescTableQuery = tuple[Literal['desc_table'], TableName]
ShowTablesQuery = tuple[Literal['show_tables']]

Query = CreateTableQuery | DropTableQuery | DescTableQuery | ShowTablesQuery \
        | SelectQuery | InsertQuery | DeleteQuery | UpdateQuery | Literal[
            'exit']
QueryList = list[Query]

"""Types to be saved and loaded to Berkeley DB"""


class ColumnMeta(TypedDict):
    data_type: Literal['int', 'char', 'date']
    char_len: int | None
    not_null: bool


class TableSchema(TypedDict):
    columns: dict[ColumnName, ColumnMeta]
    primary_key: list[ColumnName]  # If no primary key, empty list (not None!!)
    foreign_keys: dict[ColumnName, tuple[TableName, ColumnName]]


TableRow = dict[ColumnName, Value]
TableData = list[TableRow]
