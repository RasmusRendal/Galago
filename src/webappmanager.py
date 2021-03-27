from PySide2 import QtSql, QtCore
import os, sys

# Should only be instantiated from here
class WebApp:
    def __init__(self, title, url, icon_path):
        self.title = title
        self.url = url
        self.icon_path = icon_path
        self.persist = True

def initDB():
    path = QtCore.QStandardPaths.writableLocation(QtCore.QStandardPaths.AppDataLocation)
    if not os.path.exists(path):
        os.makedirs(path)
    database = QtSql.QSqlDatabase.addDatabase("QSQLITE")
    database.setDatabaseName(path + "/webappifierdb.db")
    if not database.open():
        raise Exception("Database not working: " + database.lastError().driverText())
    query = QtSql.QSqlQuery("CREATE TABLE IF NOT EXISTS webapps (title TEXT PRIMARY KEY, url TEXT, icon_path TEXT);")
    query.exec_()

def getWebapps():
    query = QtSql.QSqlQuery("SELECT title, url, icon_path FROM webapps;")
    apps = []
    while query.next():
        title = query.value(0)
        url = query.value(1)
        icon_path = query.value(2)
        print("Getting: " + icon_path)
        apps.append(WebApp(title, url, icon_path))
    return apps


def getWebapp(title):
    selectedWebApp = None
    apps = getWebapps()
    for webapp in apps:
        if webapp.title == title:
            return webapp
            break
    raise Exception("Webapp " + title + " not found")

desktopEntryTemplate = """[Desktop Entry]
Type=Application
Exec={0} --app {1}
Name={1}
Icon={2}
StartupWMClass=webappifier
Terminal=false
"""

def updateDesktopEntry(wap):
    main_file = os.path.realpath(sys.modules['__main__'].__file__)
    desktopEntryContent = desktopEntryTemplate.format(main_file, wap.title, wap.icon_path)
    path = QtCore.QStandardPaths.writableLocation(QtCore.QStandardPaths.ApplicationsLocation) + "/webappifier-" + wap.title + ".desktop"
    desktop_file = open(path, "wt")
    desktop_file.write(desktopEntryContent)
    desktop_file.close()


def updateIcon(title, icon_path):
    query = QtSql.QSqlQuery()
    query.prepare("UPDATE webapps SET icon_path = :icon_path WHERE title = :title;")
    query.bindValue(":icon_path", icon_path)
    query.bindValue(":title", title)
    if not query.exec_():
        raise Exception("Query failed: " + query.lastError().driverText())
    updateDesktopEntry(getWebapp(title))

def addWebApp(title, url):
    query = QtSql.QSqlQuery()
    query.prepare("INSERT INTO webapps (title, url, icon_path) VALUES (:title, :url, :icon_path);")
    query.bindValue(":title", title)
    query.bindValue(":url", url)
    query.bindValue(":icon_path", "gpodder")
    query.exec_()
    apps = getWebapps()
    wap = WebApp(title, url, "gpodder")
    updateDesktopEntry(wap)
    return wap
