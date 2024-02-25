from myTypes import *

PROMPT = 'DB_2019-18873> '


def print_after_prompt(msg):
    print(PROMPT + str(msg))


def type_check(data_type: Literal['int', 'char', 'date'], char_len: int | None, value: Value,
               char_len_strict=False) -> bool:
    if data_type == 'int':
        return isinstance(value, int) or value is None
    elif data_type == 'char':
        assert (char_len is not None)
        if not char_len_strict:
            return (isinstance(value, str) and len(value) >= char_len) or value is None
        else:
            return (isinstance(value, str) and len(value) == char_len) or value is None
    elif data_type == 'date':
        return isinstance(value, datetime) or value is None


def select_pkey_cols(schema: TableSchema, row: dict[str, Value]) -> dict[str, Value]:
    if len(schema['primary_key']) == 0:
        raise Exception('No primary key')
    return {col: row[col] for col in schema['primary_key']}


def value_to_str(value: Value) -> str:
    if isinstance(value, int):
        return str(value)
    elif isinstance(value, str):
        return value
    elif isinstance(value, datetime):
        return f"{value.strftime('%Y-%m-%d')}"
    else:
        assert (value is None)
        return 'NULL'


def pkey_unique_check(schema: TableSchema, rows: list[TableRow]) -> bool:
    pkey_cols = schema['primary_key']
    if len(pkey_cols) == 0:
        return True
    pkey_values = [tuple(row[col] for col in pkey_cols) for row in rows]
    if len(pkey_values) != len(set(pkey_values)):
        return False
    return True
