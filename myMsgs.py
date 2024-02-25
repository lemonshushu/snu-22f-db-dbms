class CreateTableSuccess:
    """[#tableName] table is created"""

    def __init__(self, table_name):
        self.table_name = table_name
        self.message = f"'{table_name}' table is created"

    def __str__(self):
        return self.message


class DuplicateColumnDefError(Exception):
    """Create table has failed: column definition is duplicated"""

    def __init__(self, column_name):
        self.column_name = column_name
        self.message = 'Create table has failed: column definition is duplicated'
        super().__init__(self.message)

    def __str__(self):
        return self.message


class DuplicatePrimaryKeyDefError(Exception):
    """Create table has failed: primary key definition is duplicated"""

    def __init__(self):
        self.message = 'Create table has failed: primary key definition is duplicated'
        super().__init__(self.message)

    def __str__(self):
        return self.message


class ReferenceTypeError(Exception):
    """Create table has failed: foreign key references wrong type"""

    def __init__(self):
        self.message = 'Create table has failed: foreign key references wrong type'
        super().__init__(self.message)

    def __str__(self):
        return self.message


class ReferenceNonPrimaryKeyError(Exception):
    """Create table has failed: foreign key references non primary key column"""

    def __init__(self):
        self.message = 'Create table has failed: foreign key references non primary key column'
        super().__init__(self.message)

    def __str__(self):
        return self.message


class ReferenceColumnExistenceError(Exception):
    """Create table has failed: foreign key references non existing column"""

    def __init__(self, column_name):
        self.column_name = column_name
        self.message = 'Create table has failed: foreign key references non existing column'
        super().__init__(self.message)

    def __str__(self):
        return self.message


class ReferenceTableExistenceError(Exception):
    """Create table has failed: foreign key references non existing table"""

    def __init__(self, table_name):
        self.table_name = table_name
        self.message = 'Create table has failed: foreign key references non existing table'
        super().__init__(self.message)

    def __str__(self):
        return self.message


class NonExistingColumnDefError(Exception):
    """Create table has failed: '{column_name}' does not exists in column definition"""

    def __init__(self, column_name):
        self.column_name = column_name
        self.message = f"Create table has failed: '{column_name}' does not exists in column definition"
        super().__init__(self.message)

    def __str__(self):
        return self.message


class TableExistenceError(Exception):
    """Same table name already exists"""

    def __init__(self, table_name):
        self.table_name = table_name
        self.message = "Create table has failed: table with the same name already exists"

    def __str__(self):
        return self.message


class DropSuccess:
    """[#tableName] table is dropped"""

    def __init__(self, table_name):
        self.table_name = table_name
        self.message = f"'{table_name}' table is dropped"

    def __str__(self):
        return self.message


class DropReferencedTableError(Exception):
    """Drop table has failed: '{table_name}' is referenced by other table"""

    def __init__(self, table_name):
        self.table_name = table_name
        self.message = f"Drop table has failed: '{table_name}' is referenced by other table"

    def __str__(self):
        return self.message


class NoSuchTable(Exception):
    """No such table"""

    def __init__(self, table_name):
        self.table_name = table_name
        self.message = "No such table"

    def __str__(self):
        return self.message


class CharLengthError(Exception):
    def __init__(self, char_len):
        self.char_len = char_len
        self.message = "Char length should be over 0"

    def __str__(self):
        return self.message


class InsertResult:
    """The row is inserted"""

    def __init__(self):
        self.message = "The row is inserted"

    def __str__(self):
        return self.message


class InsertDuplicatePrimaryKeyError(Exception):
    """Insertion has failed: Primary key duplication"""

    def __init__(self):
        self.message = 'Insertion has failed: Primary key duplication'
        super().__init__(self.message)

    def __str__(self):
        return self.message


class InsertReferentialIntegrityError(Exception):
    """Insertion has failed: Referential integrity violation"""

    def __init__(self):
        self.message = 'Insertion has failed: Referential integrity violation'
        super().__init__(self.message)

    def __str__(self):
        return self.message


class InsertTypeMismatchError(Exception):
    """Insertion has failed: Types are not matched"""

    def __init__(self):
        self.message = 'Insertion has failed: Types are not matched'
        super().__init__(self.message)

    def __str__(self):
        return self.message


class InsertColumnExistenceError(Exception):
    """Insertion has failed: '[#colName]' does not exist"""

    def __init__(self, col_name):
        self.col_name = col_name
        self.message = f"Insertion has failed: '{col_name}' does not exist"

    def __str__(self):
        return self.message


class InsertionColumnNonNullableError(Exception):
    """Insertion has failed: '[#colName]' is not nullable"""

    def __init__(self, col_name):
        self.col_name = col_name
        self.message = f"Insertion has failed: '{col_name}' is not nullable"

    def __str__(self):
        return self.message


class DeleteResult:
    """[#count] row(s) are deleted"""

    def __init__(self, count):
        self.count = count
        self.message = f"{count} row(s) are deleted"

    def __str__(self):
        return self.message


class DeleteReferentialIntegrityPassed:
    """[#count] row(s) are not deleted due to referential integrity"""

    def __init__(self, count):
        self.count = count
        self.message = f"{count} row(s) are not deleted due to referential integrity"

    def __str__(self):
        return self.message


class SelectTableExistenceError(Exception):
    '''Selection has failed: '[#tableName]' does not exist'''

    def __init__(self, table_name):
        self.table_name = table_name
        self.message = f"Selection has failed: '{table_name}' does not exist"

    def __str__(self):
        return self.message


class SelectColumnResolveError(Exception):
    '''Selection has failed: fail to resolve '[#colName]'''

    def __init__(self, col_name):
        self.col_name = col_name
        self.message = f"Selection has failed: failed to resolve '{col_name}'"

    def __str__(self):
        return self.message


class UpdateResult:
    '''[#count] row(s) are updated'''

    def __init__(self, count):
        self.count = count
        self.message = f"{count} row(s) are updated"

    def __str__(self):
        return self.message


class UpdateDuplicatePrimaryKeyError(Exception):
    '''Update has failed: Primary key duplication'''

    def __init__(self):
        self.message = 'Update has failed: Primary key duplication'
        super().__init__(self.message)

    def __str__(self):
        return self.message


class UpdateReferentialIntegrityError(Exception):
    '''Update has failed: Referential integrity violation'''

    def __init__(self):
        self.message = 'Update has failed: Referential integrity violation'
        super().__init__(self.message)

    def __str__(self):
        return self.message


class UpdateTypeMismatchError(Exception):
    '''Update has failed: Types are not matched'''

    def __init__(self):
        self.message = 'Update has failed: Types are not matched'
        super().__init__(self.message)

    def __str__(self):
        return self.message


class UpdateColumnExistenceError(Exception):
    '''Update has failed: '[#colName]' does not exist'''

    def __init__(self, col_name):
        self.col_name = col_name
        self.message = f"Update has failed: '{col_name}' does not exist"

    def __str__(self):
        return self.message


class UpdateColumnNonNullableError(Exception):
    '''Update has failed: '[#colName]' is not nullable'''

    def __init__(self, col_name):
        self.col_name = col_name
        self.message = f"Update has failed: '{col_name}' is not nullable"

    def __str__(self):
        return self.message


class UpateReferentialIntegrityPassed:
    '''[#count] row(s) are not updated due to referential integrity'''

    def __init__(self, count):
        self.count = count
        self.message = f"{count} row(s) are not updated due to referential integrity"

    def __str__(self):
        return self.message


class WhereIncomparableError(Exception):
    '''Where clause try to compare incomparable values'''

    def __init__(self):
        self.message = 'Where clause try to compare incomparable values'
        super().__init__(self.message)

    def __str__(self):
        return self.message


class WhereTableNotSpecified(Exception):
    '''Where clause try to reference tables which are not specified'''

    def __init__(self):
        self.message = 'Where clause try to reference tables which are not specified'
        super().__init__(self.message)

    def __str__(self):
        return self.message


class WhereColumnNotExist(Exception):
    '''Where clause try to reference non existing column'''

    def __init__(self):
        self.message = 'Where clause try to reference non existing column'
        super().__init__(self.message)

    def __str__(self):
        return self.message


class WhereAmbiguousReference(Exception):
    '''Where clause contains ambiguous reference'''

    def __init__(self):
        self.message = 'Where clause contains ambiguous reference'
        super().__init__(self.message)

    def __str__(self):
        return self.message


class NotUniqueTableAlias(Exception):
    '''Not unique table/alias: '[#tableName]'''

    def __init__(self, table_name):
        self.table_name = table_name
        self.message = f"Not unique table/alias: '{self.table_name}'"
        super().__init__(self.message)

    def __str__(self):
        return self.message
