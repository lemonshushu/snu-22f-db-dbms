import copy
import json

from lark.exceptions import VisitError

from bdbUtils import *
from myMsgs import *
from myUtils import *
from transformers import WhereClauseTransformer


def create_table(my_db, table_schemas: dict[TableName, TableSchema], table_data: dict[TableName, TableData],
                 query: CreateTableQuery):
    try:
        table_name, table_element_list = query[1:]
        if table_name in table_schemas:
            raise TableExistenceError(table_name)

        column_definitions: list[ColumnDefinition] = []
        primary_key_constraints: list[PrimaryKeyConstraint] = []
        referential_constraints: list[ReferentialConstraint] = []
        for table_element in table_element_list:
            if table_element[0] == 'col':
                column_definitions.append(table_element)
            elif table_element[0] == 'cons':
                constraint = table_element[1]
                if constraint[0] == 'pkey':
                    primary_key_constraints.append(constraint)
                elif constraint[0] == 'ref':
                    referential_constraints.append(constraint)

        # Check for duplicate column names
        column_names = set()
        for column_definition in column_definitions:
            column_name = column_definition[1]
            if column_name in column_names:
                raise DuplicateColumnDefError(column_name)
            column_names.add(column_name)

        # Save column definitions
        schema: TableSchema = {
            'columns': {},
            'primary_key': [],
            'foreign_keys': {}
        }
        for column_definition in column_definitions:
            column_name, data_type, not_null = column_definition[1:]
            (data_type_string, char_len) = data_type
            if data_type_string == 'char':
                assert (char_len is not None)
                if char_len <= 0:
                    raise CharLengthError(char_len)
            schema['columns'][column_name] = {
                'data_type': data_type_string,
                'char_len': char_len,
                'not_null': not_null
            }

        # Save primary key constraint
        if len(primary_key_constraints) == 1:
            primary_key_constraint = primary_key_constraints[0]
            column_name_list = list(set(primary_key_constraint[1]))
            for column_name in column_name_list:
                if column_name not in column_names:
                    raise NonExistingColumnDefError(column_name)
            schema['primary_key'] = column_name_list
            for column in column_name_list:
                schema['columns'][column]['not_null'] = True
        elif len(primary_key_constraints) > 1:
            raise DuplicatePrimaryKeyDefError()

        # Save referential constraints
        for referential_constraint in referential_constraints:
            foreign_key_cols, referenced_table, referenced_cols = referential_constraint[1:]
            for column_name in foreign_key_cols:
                if column_name not in column_names:
                    raise NonExistingColumnDefError(column_name)
            if referenced_table not in table_schemas:
                raise ReferenceTableExistenceError(referenced_table)
            for column_name in referenced_cols:
                if column_name not in table_schemas[referenced_table]['columns']:
                    raise ReferenceColumnExistenceError(column_name)
            # Check if referenced_cols are primary key of referenced_table
            if set(referenced_cols) != set(table_schemas[referenced_table]['primary_key']):
                raise ReferenceNonPrimaryKeyError()
            # Check if types of foreign_key_cols and referenced_cols are the same
            if len(foreign_key_cols) != len(referenced_cols):
                raise ReferenceTypeError()
            for i in range(len(foreign_key_cols)):
                foreign_key_col = foreign_key_cols[i]
                referenced_col = referenced_cols[i]
                if schema['columns'][foreign_key_col]['data_type'] != \
                        table_schemas[referenced_table]['columns'][referenced_col]['data_type'] or \
                        schema['columns'][foreign_key_col]['char_len'] != \
                        table_schemas[referenced_table]['columns'][referenced_col]['char_len']:
                    raise ReferenceTypeError()

            # All checks passed, save referential constraint
            for referencing_col in foreign_key_cols:
                schema['foreign_keys'][referencing_col] = (
                    referenced_table, referenced_cols[foreign_key_cols.index(referencing_col)])

        # Create table
        table_schemas[table_name] = schema
        table_data[table_name] = []

        # Use berkleyDB to store data
        my_db.put(tname_to_schema_key(table_name).encode(), json.dumps(
            schema, cls=MyEncoder).encode())
        my_db.put(tname_to_data_key(table_name).encode(), json.dumps(
            [], cls=MyEncoder).encode())

        print_after_prompt(CreateTableSuccess(table_name))
    except Exception as e:
        print_after_prompt(e)


def drop_table(my_db, table_schemas: dict[TableName, TableSchema], table_data: dict[TableName, TableData],
               table_name: TableName):
    try:
        if table_name not in table_schemas:
            raise NoSuchTable(table_name)

        # Check if there are any foreign keys referencing this table
        for table in table_schemas.values():
            for foreign_key in table['foreign_keys'].values():
                if foreign_key[0] == table_name:
                    raise DropReferencedTableError(table_name)

        del table_schemas[table_name]
        del table_data[table_name]
        schema_file_name = table_name + '.schema'
        data_file_name = table_name + '.data'
        my_db.delete(schema_file_name.encode())
        my_db.delete(data_file_name.encode())
        print_after_prompt(DropSuccess(table_name))
    except Exception as e:
        print_after_prompt(e)


def desc_table(table_schemas: dict[TableName, TableSchema], table_name: TableName):
    """Print the schema of the table"""
    try:
        if table_name not in table_schemas:
            raise NoSuchTable(table_name)
        table = table_schemas[table_name]
        print('-------------------------------------------------')
        print(f'table_name [{table_name}]')
        print(f"{'column_name':<20}  {'type':<10}  {'null':<10}  {'key':<10}")
        for column_name, column in table['columns'].items():
            null_string = 'N' if column['not_null'] else 'Y'
            is_pkey = column_name in table['primary_key']
            is_fkey = column_name in table['foreign_keys']
            if is_pkey and is_fkey:
                key_string = 'PRI/FOR'
            elif is_pkey:
                key_string = 'PRI'
            elif is_fkey:
                key_string = 'FOR'
            else:
                key_string = ''
            type_string = column['data_type']
            if column['data_type'] == 'char':
                type_string += f'({column["char_len"]})'
            print(
                f"{column_name:<20}  {type_string:<10}  {null_string:<10}  {key_string:<10}")
        print('-------------------------------------------------')
    except Exception as e:
        print_after_prompt(e)


def show_tables(table_schemas: dict[TableName, TableSchema]):
    """Print the names of all tables"""
    print('----------------')
    for table_name in table_schemas:
        print(table_name)
    print('----------------')


def insert_data(my_db, table_schemas: dict[TableName, TableSchema], table_data: dict[TableName, TableData],
                query: InsertQuery):
    """Insert data(tuple) into the table"""
    try:
        table_name: TableName = query[1]
        column_name_list: ColumnNameList | None = query[2]
        value_list: ValueList = query[3]

        if table_name not in table_schemas:
            raise NoSuchTable(table_name)

        if column_name_list is None:
            column_name_list = list(
                table_schemas[table_name]['columns'].keys())

        num_cols = len(table_schemas[table_name]['columns'])
        if len(column_name_list) != num_cols or len(value_list) != num_cols:
            raise InsertTypeMismatchError()

        row: dict[ColumnName, Value] = {}

        for i in range(len(column_name_list)):
            column_name = column_name_list[i]
            value = value_list[i]

            # Check column existence
            if column_name not in table_schemas[table_name]['columns']:
                raise InsertColumnExistenceError(column_name)

            # Check if not_null constraint is met
            if table_schemas[table_name]['columns'][column_name]['not_null'] and value is None:
                raise InsertionColumnNonNullableError(column_name)

            # Check if types match
            column_type = table_schemas[table_name]['columns'][column_name]['data_type']
            char_len = table_schemas[table_name]['columns'][column_name]['char_len']
            if not type_check(column_type, char_len, value):
                raise InsertTypeMismatchError()

            # If string is longer than char_len, truncate it
            if column_type == 'char' and value is not None:
                if len(value) > char_len:
                    value = value[:char_len]

            # Check for foreign key constraint
            if value is not None and column_name in table_schemas[table_name]['foreign_keys']:
                (ref_table,
                 ref_col) = table_schemas[table_name]['foreign_keys'][column_name]
                available_values = set([row[ref_col]
                                        for row in table_data[ref_table]])
                if value not in available_values:
                    raise InsertReferentialIntegrityError()

            row[column_name] = value

        # Check if primary key is unique
        if len(table_schemas[table_name]['primary_key']) > 0:
            pkey = select_pkey_cols(table_schemas[table_name], row)
            existing_pkeys = [select_pkey_cols(table_schemas[table_name], row)
                              for row in table_data[table_name]]
            if pkey in existing_pkeys:
                raise InsertDuplicatePrimaryKeyError()

        # All checks passed, insert row and save
        table_data[table_name].append(row)
        my_db.put(tname_to_data_key(table_name).encode(),
                  json.dumps(table_data[table_name], cls=MyEncoder).encode())

        print_after_prompt(InsertResult())

    except Exception as e:
        print_after_prompt(e)


def delete_data(my_db, table_schemas: dict[TableName, TableSchema], table_data: dict[TableName, TableData],
                query: DeleteQuery):
    """Delete data from the table"""
    try:
        table_name: TableName = query[1]
        where_clause: WhereClause = query[2]

        if table_name not in table_schemas:
            raise NoSuchTable(table_name)

        delete_count = 0
        cant_delete: int = 0  # number of rows that can't be deleted due to referential constraints
        modified_tables: set[TableName] = set()  # tables that have been modified

        referenced_by: dict[ColumnName, list[tuple[TableName, ColumnName]]] = {}
        for table in table_schemas:
            for column in table_schemas[table]['foreign_keys']:
                (ref_table, ref_col) = table_schemas[table]['foreign_keys'][column]
                if ref_table == table_name:
                    if ref_col not in referenced_by:
                        referenced_by[ref_col] = []
                    referenced_by[ref_col].append((table, column))

        new_data: list[TableRow] = []  # new data after deletion

        # Deletion rule : ON DELETE SET NULL
        for row in table_data[table_name]:
            if where_clause is not None:
                if not WhereClauseTransformer({table_name: row}).transform(
                        where_clause):  # Where clause is not met, so add to new_data
                    new_data.append(row)
                    continue

            is_referenced: bool = False  # whether the current row is referenced by any row in other tables
            for column in referenced_by:
                for (ref_table, ref_col) in referenced_by[column]:
                    for ref_row in table_data[ref_table]:
                        if ref_row[ref_col] == row[column]:
                            is_referenced = True
                            if table_schemas[ref_table]['columns'][ref_col]['not_null']:
                                cant_delete += 1
                                new_data.append(row)
                                continue

            if is_referenced:
                # The row is referenced by other rows, but they are all nullable.
                # Therefore, set them to NULL, then we can delete the row.
                for column in referenced_by:
                    for (ref_table, ref_col) in referenced_by[column]:
                        for ref_row in table_data[ref_table]:
                            if ref_row[ref_col] == row[column]:
                                ref_row[ref_col] = None
                                modified_tables.add(ref_table)

            delete_count += 1

        table_data[table_name] = new_data
        modified_tables.add(table_name)

        # Save modified tables
        for table in modified_tables:
            my_db.put(tname_to_data_key(table).encode(),
                      json.dumps(table_data[table], cls=MyEncoder).encode())

        print_after_prompt(DeleteResult(delete_count))
        if cant_delete > 0:
            print_after_prompt(DeleteReferentialIntegrityPassed(cant_delete))
    except VisitError as e:
        print_after_prompt(e.orig_exc)
    except Exception as e:
        print_after_prompt(e)


def select_data(table_schemas: dict[TableName, TableSchema], table_data: dict[TableName, TableData],
                query: SelectQuery):
    """Select data from the table"""
    try:
        c_a_list: list[C_A] = query[1]
        t_a_list: list[T_A] = query[2]
        where_clause: WhereClause | None = query[3]

        table_dict: dict[TableName, TableData] = {}
        table_columns: dict[TableName, list[ColumnName]] = {}
        for (t, a) in t_a_list:
            if t not in table_schemas:
                raise SelectTableExistenceError(t)
            name_to_use = a if a is not None else t
            if name_to_use in table_dict:
                raise NotUniqueTableAlias(name_to_use)
            table_dict[name_to_use] = table_data[t]
            table_columns[name_to_use] = list(table_schemas[t]['columns'].keys())

        # Empty c_a_list means "select *". In this case, first supply c_a_list with all columns
        if len(c_a_list) == 0:
            for t in table_dict:
                for c in table_columns[t]:
                    c_a_list.append((t, c, None))

        for i, (t, c, a) in enumerate(c_a_list):
            # If table name is not specified, check column name and infer table name
            if t is None:
                table_name = None
                for t in table_dict:
                    if c in table_columns[t]:
                        if table_name is not None:
                            # Column name is ambiguous
                            raise SelectColumnResolveError(c)
                        table_name = t
                if table_name is None:
                    raise SelectColumnResolveError(c)
                c_a_list[i] = (table_name, c, a)
            else:
                if t not in table_dict:
                    raise SelectColumnResolveError(f'{t}.{c}')
                elif c not in table_columns[t]:
                    raise SelectColumnResolveError(f'{t}.{c}')

        # replace (t, c, None) with (t, c, c) in c_a_list
        c_a_list = [(t, c, c if a is None else a) for (t, c, a) in c_a_list]

        # selected rows to be printed
        select_result: list[dict[tuple[TableName, ColumnName], Value]] = []
        curr: dict[TableName, int] = {
            t: 0 for t in table_dict.keys()}  # current row index

        # Iterate through rows in table_dict (Cartesian product)
        while True:
            try:
                curr_rows = {t: table_dict[t][curr[t]]
                             for t in table_dict.keys()}
                # Check if where_clause is satisfied
                where_clause_satisfied = False
                if where_clause is None:
                    where_clause_satisfied = True
                elif WhereClauseTransformer(curr_rows).transform(where_clause):
                    where_clause_satisfied = True

                if where_clause_satisfied:
                    zipped: dict[tuple[TableName, ColumnName], Value] = {}
                    for (t, c, a) in c_a_list:
                        assert (t is not None)
                        zipped[(t, c)] = curr_rows[t][c]
                    select_result.append(zipped)

                for t in table_dict.keys():
                    curr[t] += 1
                    if curr[t] < len(table_dict[t]):
                        break
                    else:
                        curr[t] = 0

                # If all rows have been iterated through, break
                if all([curr[t] == 0 for t in table_dict.keys()]):
                    break
            except IndexError:  # At least one table is empty
                break

        # Print columns (Cell width of each column is determined by the longest value in the column)

        # Before printing, cast every value in select_result to string
        printable_result = [{(t, c): value_to_str(v) for (
            (t, c), v) in row.items()} for row in select_result]

        col_widths: dict[C_A, int] = {}
        for (t, c, a) in c_a_list:
            assert (t is not None and a is not None)
            col_widths[(t, c, a)] = max([len(str(result[(t, c)]))
                                         for result in printable_result] + [len(a)])

        # Print column names
        hr_line: str = '+'  # horizontal line (to be reused)
        for (t, c, a) in c_a_list:
            assert (a is not None)
            hr_line += '-' * (col_widths[(t, c, a)] + 2) + '+'

        print(hr_line)

        print('|', end='')
        for (t, c, a) in c_a_list:
            assert (t is not None and a is not None)
            print(f' {a:<{col_widths[(t, c, a)]}} |', end='')
        print()

        print(hr_line)

        for row in printable_result:
            print('|', end='')
            for (t, c, a) in c_a_list:
                assert (t is not None and a is not None)
                print(f' {row[(t, c)]:<{col_widths[(t, c, a)]}} |', end='')
            print()

        print(hr_line)

    except VisitError as e:
        print_after_prompt(e.orig_exc)
    except Exception as e:
        print_after_prompt(e)


def update_data(my_db, table_schemas: dict[TableName, TableSchema], table_data: dict[TableName, TableData],
                query: UpdateQuery):
    try:
        (_, table_name, column_name, value, where_clause) = query
        if table_name not in table_schemas:
            raise NoSuchTable(table_name)
        if column_name not in table_schemas[table_name]['columns']:
            raise UpdateColumnExistenceError(column_name)
        if not type_check(table_schemas[table_name]['columns'][column_name]['data_type'],
                          table_schemas[table_name]['columns'][column_name]['char_len'], value):
            raise UpdateTypeMismatchError()
        if value is None and table_schemas[table_name]['columns'][column_name]['not_null']:
            raise UpdateColumnNonNullableError(column_name)

        if type(value) == str:
            value = value[:table_schemas[table_name]['columns'][column_name]['char_len']]

        is_pkey: bool = column_name in table_schemas[table_name]['primary_key']
        referenced_by: list[tuple[TableName, ColumnName]] = []
        if is_pkey:
            for t in table_schemas:
                for c, (ref_table, ref_column) in table_schemas[t]['foreign_keys'].items():
                    if ref_table == table_name and ref_column == column_name:
                        referenced_by.append((t, c))

        is_fkey: bool = column_name in table_schemas[table_name]['foreign_keys']
        fkey_violated: bool = False
        if is_fkey:
            # Check if the new value doesn't violate foreign key constraint
            (ref_table, ref_col) = table_schemas[table_name]['foreign_keys'][column_name]
            if not any([ref_row[ref_col] == value for ref_row in table_data[ref_table]]):
                fkey_violated = True

        update_count = 0
        orig_data = copy.deepcopy(table_data[table_name])

        for row in table_data[table_name]:
            to_update: bool = False
            if row[column_name] == value:  # No need to update
                to_update = False
            elif where_clause is None:
                to_update = True
            elif WhereClauseTransformer({table_name: row}).transform(where_clause):
                to_update = True
            if to_update:
                if is_fkey and fkey_violated:
                    raise UpdateReferentialIntegrityError()
                if is_pkey:
                    # Check if there is a foreign key that references the row
                    for (ref_table, ref_col) in referenced_by:
                        for ref_row in table_data[ref_table]:
                            if ref_row[ref_col] == ref_row[column_name]:
                                # TODO: Currently - cancel update and raise error
                                table_data[table_name] = orig_data  # roll back all changes
                                raise UpdateReferentialIntegrityError()
                    row[column_name] = value
                    # Primary key uniqueness check
                    if not pkey_unique_check(table_schemas[table_name], table_data[table_name]):
                        table_data[table_name] = orig_data  # roll back all changes
                        raise UpdateDuplicatePrimaryKeyError()
                row[column_name] = value
                update_count += 1
        my_db.put(tname_to_data_key(table_name).encode(),
                  json.dumps(table_data[table_name], cls=MyEncoder).encode())
        print_after_prompt(UpdateResult(update_count))
    except VisitError as e:
        print_after_prompt(e.orig_exc)
    except Exception as e:
        print_after_prompt(e)
