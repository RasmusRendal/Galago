from PySide2 import QtSql, QtCore

class WebApp:
    def __init__(self, wap_id, title, url):
        self.id = wap_id
        self.title = title
        self.url = url

def initDB():
    database = QtSql.QSqlDatabase.addDatabase("QSQLITE")
    path = QtCore.QStandardPaths.writableLocation(QtCore.QStandardPaths.AppDataLocation)
    database.setDatabaseName(path + "/webappifierdb.db")
    if not database.open():
        raise Exception("Database not working")
    query = QtSql.QSqlQuery("CREATE TABLE IF NOT EXISTS webapps (id TEXT PRIMARY KEY, title TEXT, url TEXT);")
    query.exec_()

def getWebapps():
    query = QtSql.QSqlQuery("SELECT * FROM webapps;")
    apps = []
    while query.next():
        wap_id = query.value(0)
        title = query.value(1)
        url = query.value(2)
        apps.append(WebApp(wap_id, title, url))
    return apps


def getWebapp(wap_id):
    selectedWebApp = None
    apps = getWebapps()
    for webapp in apps:
        if webapp.id == wap_id:
            return webapp
            break
    raise Exception("Webapp " + wap_id + " not found")

def addWebApp(wap_id, title, url):
    query = QtSql.QSqlQuery()
    query.prepare("INSERT INTO webapps (id, title, url) VALUES (:id, :title, :url);")
    query.bindValue(":id", wap_id)
    query.bindValue(":title", title)
    query.bindValue(":url", url)
    query.exec_()
    getWebapps()
