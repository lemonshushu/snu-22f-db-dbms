"""Simple Database Management System using Berkeley DB."""

from berkeleydb import db
from lark.exceptions import UnexpectedInput
from lark.lark import Lark

from execute import *
from myUtils import *
from transformers import SQLTransformer

with open('grammar.lark') as file:
    sql_parser = Lark(file.read(), start="command", lexer="basic",
                      transformer=SQLTransformer(), parser="lalr")

# Load from Berkeley DB
myDB = db.DB()
myDB.open('myDB', dbtype=db.DB_HASH, flags=db.DB_CREATE)

table_schemas: dict[TableName, TableSchema] = {}
table_data: dict[TableName, TableData] = {}

for key, value in myDB.items():
    # if key ends with '.schema', it is a table schema. If it ends with '.data', it is a table data.
    if key.decode().endswith('.schema'):
        table_schemas[key.decode()[:-7]] = json.loads(value.decode(),
                                                      cls=MyDecoder)
    elif key.decode().endswith('.data'):
        table_data[key.decode()[:-5]] = json.loads(value.decode(),
                                                   cls=MyDecoder)

exit_flag = False

while not exit_flag:
    # Get input until query ends with semicolon
    buf = input(PROMPT)
    buf = buf.rstrip()  # Strip trailing whitespaces for semicolon check
    while not buf.endswith(';'):
        buf += ' '  # Add whitespace between lines
        buf += input()
        buf = buf.rstrip()

    query_strings = buf.split(';')
    query_strings = query_strings[:-1]  # Remove last empty string
    # Re-append semicolon to each entry of buf
    query_strings = [entry + ';' for entry in query_strings]

    for query_string in query_strings:
        try:
            parsed_tree = sql_parser.parse(query_string)
            assert (isinstance(parsed_tree, list))  # To bypass type hint error
            query: Query = parsed_tree[0]

            # Execute query
            if query == 'exit':
                exit_flag = True
                break
            elif query[0] == 'create_table':
                create_table(myDB, table_schemas, table_data, query)
            elif query[0] == 'drop_table':
                table_name: TableName = query[1]
                drop_table(myDB, table_schemas, table_data, table_name)
            elif query[0] == 'desc_table':
                table_name: TableName = query[1]
                desc_table(table_schemas, table_name)
            elif query[0] == 'show_tables':
                show_tables(table_schemas)
            elif query[0] == 'insert':
                insert_data(myDB, table_schemas, table_data, query)
            elif query[0] == 'delete':
                delete_data(myDB, table_schemas, table_data, query)
            elif query[0] == 'update':
                update_data(myDB, table_schemas, table_data, query)
            elif query[0] == 'select':
                select_data(table_schemas, table_data, query)
        except UnexpectedInput:
            print_after_prompt("Syntax error")
            continue

# Close Berkeley DB
myDB.close()
