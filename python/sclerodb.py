"""Connect to the scleroderma database @ JHU.

The code here only works if the Microsoft SQL server running on the
Teasle VM on Rambo is listening on port 1433 of your machine. You'll
most likely need to make this happen by tunneling to the Teasle IP at
port 1433 through rambo and hooking it up locally.

"""
import pymssql


_SERVER = 'sclerodata'
_DATABASE = 'sclerodata'
_DOMAIN = 'WIN-T312MF37MBJ\\'


def connection(user, pw):
    """Establish connection to the sclerodata database."""
    return pymssql.connect(_SERVER, _DOMAIN + user, pw, _DATABASE)


def run_query(conn, query):
    """Yield all rows of a query run against the database."""
    with conn.cursor(as_dict=True) as cursor:
        cursor.execute(query)
        for row in cursor:
            yield row


def tables(conn):
    """Get the names of all tables."""
    query = 'select * from information_schema.tables'
    result = run_query(conn, query)
    return [row['TABLE_NAME'] for row in result]


def columns(conn, table):
    """Get the information on columns of a table."""
    query = 'select * from information_schema.columns'
    result = run_query(conn, query)
    return [row for row in result if row['TABLE_NAME'] == table]


def get_table(conn, table):
    """Query for an entire table."""
    query = 'select * from {}'.format(table)
    return run_query(conn, query)
