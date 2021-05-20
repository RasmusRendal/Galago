from PySide2 import QtSql, QtCore
import os, sys
import pathlib

# Should only be instantiated from here
class WebApp:
    def __init__(self, title, url, icon_path):
        self.title = title
        self.url = url
        self.icon_path = icon_path
        self.persist = True


def migrate():
    versionQuery = QtSql.QSqlQuery("SELECT version FROM version;")
    if not versionQuery.exec_():
        raise Exception("Version selection failed")
    version = 0
    if versionQuery.first():
        version = versionQuery.value(0)
    else:
        versionZeroQuery = QtSql.QSqlQuery("INSERT INTO version (version, id) VALUES (0, 0);")
        versionZeroQuery.exec_()
    if version == 0:
        print("Migrating from version 0 to 1")
        query = QtSql.QSqlQuery("CREATE TABLE webapps (title TEXT PRIMARY KEY, url TEXT, icon_path TEXT);")
        query.exec_()

    updateVersion = QtSql.QSqlQuery()
    updateVersion.prepare("UPDATE version SET version = :version;")
    updateVersion.bindValue(":version", 1)
    updateVersion.exec_()

def initDB():
    path = QtCore.QStandardPaths.writableLocation(QtCore.QStandardPaths.AppDataLocation)
    if not os.path.exists(path):
        os.makedirs(path)
    database = QtSql.QSqlDatabase.addDatabase("QSQLITE")
    database.setDatabaseName(path + "/galagodb.db")
    if not database.open():
        raise Exception("Database not working: " + database.lastError().driverText())
    # The ID is just a clever way to ensure only one row in the version table
    query = QtSql.QSqlQuery("CREATE TABLE IF NOT EXISTS version (version INTEGER, id INTEGER PRIMARY KEY CHECK (id = 0));")
    query.exec_()
    migrate()

def default_icon() -> str:
    return str(pathlib.Path(__file__).parent.parent / "resources/logo-rounded.png")

def getWebapps():
    query = QtSql.QSqlQuery("SELECT title, url, icon_path FROM webapps;")
    apps = []
    while query.next():
        title = query.value(0)
        url = query.value(1)
        icon_path = query.value(2)
        if icon_path != "galago" and not os.path.isfile(icon_path):
            updateIcon(title, "galago")
            icon_path = "galago"
        if icon_path == "galago":
            icon_path = default_icon()
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
Exec={0} --app "{1}"
Name={1}
Icon={2}
StartupWMClass=Galago
Terminal=false
"""

def desktopEntryLocation(title: str) -> str:
    return QtCore.QStandardPaths.writableLocation(QtCore.QStandardPaths.ApplicationsLocation) + "/galago-" + title + ".desktop"


def updateDesktopEntry(wap):
    main_file = os.path.realpath(sys.modules['__main__'].__file__)
    desktopEntryContent = desktopEntryTemplate.format(main_file, wap.title, wap.icon_path)
    path = desktopEntryLocation(wap.title)
    # If the data is already there, don't change the file
    if os.path.isfile(path):
        with open(path, "rt") as desktop_file:
            data = desktop_file.read()
            if data == desktopEntryContent:
                return
    with open(path, "wt") as desktop_file:
        desktop_file.write(desktopEntryContent)
        print("Updated desktop entry")


def updateIcon(title, icon):
    pixmap = icon.pixmap(256, 256)
    path = QtCore.QStandardPaths.writableLocation(QtCore.QStandardPaths.AppDataLocation) + "/icons/"
    if not os.path.exists(path):
        os.makedirs(path)
    icon_path = path + title + ".png"
    pixmap.save(icon_path)
    updateDesktopEntry(getWebapp(title))
    query = QtSql.QSqlQuery()
    query.prepare("UPDATE webapps SET icon_path = :icon_path WHERE title = :title;")
    query.bindValue(":icon_path", icon_path)
    query.bindValue(":title", title)
    if not query.exec_():
        raise Exception("Query failed: " + query.lastError().driverText())

def addWebApp(title, url):
    query = QtSql.QSqlQuery()
    query.prepare("INSERT INTO webapps (title, url, icon_path) VALUES (:title, :url, :icon_path);")
    query.bindValue(":title", title)
    query.bindValue(":url", url)
    query.bindValue(":icon_path", "galago")
    query.exec_()
    apps = getWebapps()
    wap = WebApp(title, url, "galago")
    updateDesktopEntry(wap)
    return wap

def deleteWebApp(app: WebApp):
    query = QtSql.QSqlQuery()
    query.prepare("DELETE FROM webapps WHERE title=:title;")
    query.bindValue(":title", app.title)
    assert query.exec_()
    desktopEntry = desktopEntryLocation(app.title)
    if os.path.isfile(desktopEntry):
        os.remove(desktopEntry)
    if os.path.isfile(app.icon_path) and app.icon_path != default_icon():
        os.remove(app.icon_path)
