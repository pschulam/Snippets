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


def get_table(conn, table, as_dict=True):
    """Yield all rows of a table in the sclerodata database."""
    query = 'select * from {}'.format(table)
    with conn.cursor(as_dict=as_dict) as cursor:
        cursor.execute(query)
        for row in cursor:
            yield row
