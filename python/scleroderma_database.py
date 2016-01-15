import pymssql


_SERVER = 'sclerodata'
_DATABASE = 'sclerodata'
_USER = 'WIN-T312MF37MBJ\\pschulam'
_PASSWORD = ''


def connection():
    return pymssql.connect(_SERVER, _USER, _PASSWORD, _DATABASE)


def query(q, as_dict=True):
    with connection() as conn:
        with conn.cursor(as_dict=as_dict) as cursor:
            cursor.execute(q)
            for result in cursor:
                yield result


def table(tbl, as_dict=True):
    q = 'select * from {}'.format(tbl)
    for result in query(q, as_dict):
        yield result
