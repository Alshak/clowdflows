from collections import defaultdict
from django import forms
import mysql.connector as sql

class DBConnection:
    '''
    Database credentials.
    '''
    def __init__(self, user, password, host, database):
        self.user = user
        self.password = password
        self.host = host
        self.database = database

    def connect(self):
        return sql.connect(user=self.user, password=self.password, host=self.host, database=self.database)

class DBContext:
    def __init__(self, connection):
        '''
        Initializes the fields:
            tables:           list of selected tables
            cols:             dict of columns for each table
            all_cols:         dict of columns for each table (even unselected)
            col_vals:         available values for each table/column 
            connected:        dict of table pairs and the connected columns
            fkeys:            foreign keys in a given table
            pkeys:            private key for a given table
            target_table:     selected table for learning
            target_att:       selected column for learning
            target_att_val:   selected target att value 
        '''
        self.connection = connection
        con = connection.connect()
        cursor = con.cursor()
        cursor.execute('SHOW tables')
        self.tables = [table for (table,) in cursor]
        self.cols = {}
        for table in self.tables:
            cursor.execute("SELECT column_name FROM information_schema.columns WHERE table_name = '%s'" % table)
            self.cols[table] = [col for (col,) in cursor]
        self.all_cols = dict(self.cols)
        self.col_vals = {}
        for table, cols in self.cols.items():
            self.col_vals[table] = {}
            for col in cols:
                cursor.execute("SELECT DISTINCT %s FROM %s" % (col, table))
                self.col_vals[table][col] = [val for (val,) in cursor]
        self.connected = {}
        cursor.execute(
           "SELECT table_name, column_name, referenced_table_name, referenced_column_name \
            FROM information_schema.KEY_COLUMN_USAGE \
            WHERE referenced_table_name IS NOT NULL")
        self.fkeys = defaultdict(set)
        for (table, col, ref_table, ref_col) in cursor:
            self.connected[(table, ref_table)] = (col, ref_col)
            self.connected[(ref_table, table)] = (ref_col, col)
            self.fkeys[table].add(col)
        self.pkeys = {}
        cursor.execute(
            "SELECT table_name, column_name \
             FROM information_schema.KEY_COLUMN_USAGE \
             WHERE constraint_name='PRIMARY' and table_schema='%s'" % connection.database)
        for (table, pk) in cursor:
            self.pkeys[table] = pk
        self.target_table = self.tables[0]
        self.target_att = None
        self.target_att_val = None
        con.close()

    def update(self, postdata):
        '''
        Updates the default selections with user's selections.
        '''
        widget_id = postdata.get('widget_id')[0]
        self.target_table = postdata.get('target_table%s' % widget_id)[0]
        self.target_att = postdata.get('target_att%s' % widget_id)[0]
        self.target_att_val = postdata.get('target_att_val%s' % widget_id)[0]
        self.tables = postdata.get('tables%s' % widget_id, [])
        # Propagate the selected tables
        for table in self.cols.keys():
            if table not in self.tables:
                del self.cols[table]
        for pair in self.connected.keys():
            if pair[0] in self.tables and pair[1] in self.tables:
                continue
            del self.connected[pair]
        for table in self.tables:
            self.cols[table] = postdata.get('%s_columns%s' % (table, widget_id), [])

    def __repr__(self):
        return str((self.target_table, self.target_att, self.tables, self.cols, self.connected))

