# Clase 8: Django "cree" que usa mysqlclient, aunque por debajo use pymysql.
try:
    import pymysql
    pymysql.install_as_MySQLdb()
except ImportError:  # si usas mysqlclient (o SQLite para pruebas) no hace falta
    pass
