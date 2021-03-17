from PySide2 import QtSql, QtCore
import os, sys

# Should only be instantiated from here
class WebApp:
    def __init__(self, wap_id, title, url, icon_path):
        self.id = wap_id
        self.title = title
        self.url = url
        self.icon_path = icon_path

def initDB():
    path = QtCore.QStandardPaths.writableLocation(QtCore.QStandardPaths.AppDataLocation)
    if not os.path.exists(path):
        os.makedirs(path)
    database = QtSql.QSqlDatabase.addDatabase("QSQLITE")
    database.setDatabaseName(path + "/webappifierdb.db")
    if not database.open():
        raise Exception("Database not working: " + database.lastError().driverText())
    query = QtSql.QSqlQuery("CREATE TABLE IF NOT EXISTS webapps (id TEXT PRIMARY KEY, title TEXT, url TEXT, icon_path TEXT);")
    query.exec_()

def getWebapps():
    query = QtSql.QSqlQuery("SELECT id, title, url, icon_path FROM webapps;")
    apps = []
    while query.next():
        wap_id = query.value(0)
        title = query.value(1)
        url = query.value(2)
        icon_path = query.value(3)
        print("Getting: " + icon_path)
        apps.append(WebApp(wap_id, title, url, icon_path))
    return apps


def getWebapp(wap_id):
    selectedWebApp = None
    apps = getWebapps()
    for webapp in apps:
        if webapp.id == wap_id:
            return webapp
            break
    raise Exception("Webapp " + wap_id + " not found")

desktopEntryTemplate = """[Desktop Entry]
Type=Application
Exec={0} --app {1}
Name={2}
Icon={3}
StartupWMClass=webappifier
Terminal=false
"""

def updateDesktopEntry(wap):
    main_file = os.path.realpath(sys.modules['__main__'].__file__)
    desktopEntryContent = desktopEntryTemplate.format(main_file, wap.id, wap.title, wap.icon_path)
    path = QtCore.QStandardPaths.writableLocation(QtCore.QStandardPaths.ApplicationsLocation) + "/webappifier-" + wap.id + ".desktop"
    desktop_file = open(path, "wt")
    desktop_file.write(desktopEntryContent)
    desktop_file.close()


def updateIcon(wap_id, icon_path):
    query = QtSql.QSqlQuery()
    print("Setting for: " + wap_id)
    print("setting to: " + icon_path)
    query.prepare("UPDATE webapps SET icon_path = :icon_path WHERE id = :id;")
    query.bindValue(":icon_path", icon_path)
    query.bindValue(":id", wap_id)
    if not query.exec_():
        raise Exception("Query failed: " + query.lastError().driverText())
    updateDesktopEntry(getWebapp(wap_id))

def addWebApp(wap_id, title, url):
    query = QtSql.QSqlQuery()
    query.prepare("INSERT INTO webapps (id, title, url, icon_path) VALUES (:id, :title, :url, :icon_path);")
    query.bindValue(":id", wap_id)
    query.bindValue(":title", title)
    query.bindValue(":url", url)
    query.bindValue(":icon_path", "gpodder")
    query.exec_()
    apps = getWebapps()
    wap = WebApp(wap_id, title, url, "gpodder")
    updateDesktopEntry(wap)
    return wap
