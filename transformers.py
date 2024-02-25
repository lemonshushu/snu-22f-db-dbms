from lark.lexer import Token
from lark.visitors import Transformer

from myMsgs import *
from myTypes import *


class SQLTransformer(Transformer):

    def command(self, args) -> list[Query]:
        return args[0]

    def query_list(self, args) -> list[Query]:
        return args

    def query(self, args) -> Query:
        return args[0]

    def table_element_list(self, args) -> TableElementList:
        return args[1:-1]

    def table_element(self, args) -> TableElement:
        return args[0]

    def data_type(self, args) -> DataType:
        dt = args[0].value
        char_len = None
        if dt == 'char':
            char_len = int(args[2].value)
        return dt, char_len

    def column_definition(self, args) -> ColumnDefinition:
        column_name: ColumnName = args[0]
        data_type: DataType = args[1]
        not_null: bool = args[2] is not None
        return 'col', column_name, data_type, not_null

    def table_constraint_definition(self, args) -> TableConstraintDefinition:
        return 'cons', args[0]

    def primary_key_constraint(self, args) -> PrimaryKeyConstraint:
        column_name_list = args[2]
        return 'pkey', column_name_list

    def referential_constraint(self, args) -> ReferentialConstraint:
        foreign_key_cols: ColumnNameList = args[2]
        referenced_table: TableName = args[4]
        referenced_cols: ColumnNameList = args[5]
        return 'ref', foreign_key_cols, referenced_table, referenced_cols

    def column_name_list(self, args) -> ColumnNameList:
        return args[1:-1]

    def table_name(self, args) -> TableName:
        return args[0].value.lower()

    def column_name(self, args) -> ColumnName:
        return args[0].value.lower()

    def create_table_query(self, args: list) -> CreateTableQuery:
        table_name: TableName = args[2]
        table_element_list: TableElementList = args[3]
        return 'create_table', table_name, table_element_list

    def drop_table_query(self, args) -> DropTableQuery:
        table_name: TableName = args[2]
        return 'drop_table', table_name

    def desc_table_query(self, args) -> DescTableQuery:
        table_name: TableName = args[1]
        return 'desc_table', table_name

    def show_tables_query(self, args) -> ShowTablesQuery:
        return 'show_tables',

    def value(self, args) -> Value:
        val_token: Token = args[0]
        val = val_token.value
        if val_token.type == 'INT':
            val = int(val)
        elif val_token.type == 'STR':
            val = val[1:-1]  # remove quotes
        elif val_token.type == 'DATE':
            val = datetime.strptime(val, '%Y-%m-%d')
        elif val_token.type == 'NULL':
            val = None
        return val

    def value_list(self, args) -> ValueList:
        return args[1:-1]

    def insert_query(self, args) -> InsertQuery:
        table_name: TableName = args[2]
        column_name_list: ColumnNameList | None = args[3]
        value_list: ValueList = args[5]
        return 'insert', table_name, column_name_list, value_list

    def delete_query(self, args) -> DeleteQuery:
        table_name: TableName = args[2]
        where_clause: WhereClause | None = args[3]
        return 'delete', table_name, where_clause

    def select_query(self, args) -> SelectQuery:
        select_list: list[C_A] = args[1]
        (t_a_list, where_clause) = args[2]
        return 'select', select_list, t_a_list, where_clause

    def select_list(self, args: list[C_A]) -> list[C_A]:
        return args

    def selected_column(self, args) -> C_A:
        table_name: TableName | None = args[0]
        column_name: ColumnName = args[1]
        column_alias: ColumnName | None = args[3]
        return table_name, column_name, column_alias

    def table_expression(self, args) -> tuple[list[T_A], WhereClause | None]:
        t_a_list: list[T_A] = args[0]
        where_clause: WhereClause | None = args[1]
        return t_a_list, where_clause

    def from_clause(self, args) -> list[T_A]:
        return args[1]

    def table_reference_list(self, args: list[T_A]) -> list[T_A]:
        return args

    def referred_table(self, args) -> T_A:
        table_name: TableName = args[0]
        table_alias: TableName | None = args[2]
        return table_name, table_alias

    def update_query(self, args) -> UpdateQuery:
        table_name: TableName = args[1]
        column_name: ColumnName = args[3]
        value: Value = args[4]
        where_clause: WhereClause | None = args[5]
        return 'update', table_name, column_name, value, where_clause


class WhereClauseTransformer(Transformer):
    """If return type is bool | None, None means Unknown (i.e., Possible values : true, false, unknown)"""

    def __init__(self, table_rows: dict[TableName, TableRow]):
        self.table_rows = table_rows
        super().__init__()

    def where_clause(self, args) -> bool | None:
        return args[1]

    def boolean_expr(self, args) -> bool | None:
        boolean_terms: list[bool] = args[::2]
        intermediate_result: bool | None = False
        for term in boolean_terms:
            if term is True or intermediate_result is True:
                intermediate_result = True
            elif term is None or intermediate_result is None:
                intermediate_result = None
            else:
                intermediate_result = intermediate_result or term
        return intermediate_result

    def boolean_term(self, args) -> bool | None:
        boolean_factors: list[bool | None] = args[::2]
        intermediate_result: bool | None = True
        for factor in boolean_factors:
            if factor is False or intermediate_result is False:
                intermediate_result = False
            elif factor is None or intermediate_result is None:
                intermediate_result = None
            else:
                intermediate_result = intermediate_result and factor
        return intermediate_result

    def boolean_factor(self, args) -> bool | None:
        not_keyword_exists = args[0] is not None
        boolean_test: bool | None = args[1]

        if boolean_test is None:
            return None
        else:
            if not_keyword_exists:
                return not boolean_test
            else:
                return boolean_test

    def boolean_test(self, args) -> bool | None:
        return args[0]

    def parenthesized_boolean_expr(self, args) -> bool:
        return args[1]

    def predicate(self, args) -> bool | None:
        return args[0]

    def comparison_predicate(self, args) -> bool | None:
        left = args[0]
        right = args[2]
        comp_operator: Literal['lt', 'gt', 'eq',
                               'gte', 'lte', 'neq'] = args[1].data
        # If either operand is None(NULL), the comparison is unknown -> return None
        if left is None or right is None:
            return None

        # Case-insensitive comparison for string
        if isinstance(left, str):
            left = left.lower()
        if isinstance(right, str):
            right = right.lower()

        try:
            # Compare left and right values
            if comp_operator == 'lt':
                return left < right
            elif comp_operator == 'gt':
                return left > right
            elif comp_operator == 'eq':
                return left == right
            elif comp_operator == 'gte':
                return left >= right
            elif comp_operator == 'lte':
                return left <= right
            elif comp_operator == 'neq':
                return left != right
        except TypeError:
            raise WhereIncomparableError()

    def comp_operand(self, args) -> Value:
        if len(args) == 1:
            # Comparable value
            return args[0]
        elif len(args) == 2:
            # (Table name,) Column name
            return self.get_value_from_row(args[0], args[1])

    def comparable_value(self, args) -> Value:
        val_token: Token = args[0]
        val = val_token.value
        if val_token.type == 'INT':
            val = int(val)
        elif val_token.type == 'STR':
            val = val[1:-1]  # remove quotes
        elif val_token.type == 'DATE':
            val = datetime.strptime(val, '%Y-%m-%d')
        elif val_token.type == 'NULL':
            val = None
        return val

    def null_predicate(self, args) -> bool:
        table_name: TableName | None = args[0]
        column_name: ColumnName = args[1]
        check_is_null: bool = args[2]
        val: Value = self.get_value_from_row(table_name, column_name)
        return check_is_null == (val is None)

    def null_operation(self, args) -> bool:
        """Returns True if "IS NULL" and False if "IS NOT NULL\""""
        if args[1] is not None:  # IS NOT NULL
            return False
        else:  # IS NULL
            return True

    def get_value_from_row(self, table_name: TableName | None, column_name: ColumnName) -> Value:
        """Helper function to get value from row"""
        if table_name is None:
            # If column_name occurs only once across tables, use that table. Otherwise, raise error.
            for tn in self.table_rows:
                if column_name in self.table_rows[tn]:
                    if table_name is None:
                        table_name = tn
                    else:
                        # Column name occurs in multiple tables
                        raise WhereAmbiguousReference()
            if table_name is None:
                # Column name does not occur in any table
                raise WhereColumnNotExist()
        else:
            if table_name not in self.table_rows:
                raise WhereTableNotSpecified()
            if column_name not in self.table_rows[table_name]:
                raise WhereColumnNotExist()
        return self.table_rows[table_name][column_name]
