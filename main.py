#!/usr/bin/env python3
import sys
from PySide2 import QtCore, QtWidgets, QtGui, QtWebEngineWidgets
import argparse
import signal
from src.webappmanager import initDB, getWebapps, getWebapp, addWebApp


class WebAppBrowser(QtWidgets.QWidget):
    def __init__(self, webapp):
        super().__init__()
        self.webapp = webapp
        self.view = QtWebEngineWidgets.QWebEngineView()
        self.view.load(QtCore.QUrl(self.webapp.url))
        self.layout = QtWidgets.QVBoxLayout(self)
        self.layout.addWidget(self.view)
        self.layout.setContentsMargins(QtCore.QMargins(0, 0, 0, 0))
        print("started")


class AppSelector(QtWidgets.QWidget):
    def __init__(self, apps):
        super().__init__()
        self.apps = apps
        self.layout = QtWidgets.QGridLayout(self)
        self.app_buttons = []
        for app in self.apps:
            button = QtWidgets.QPushButton(app.title)
            self.layout.addWidget(button)
            def start():
                self.browser = WebAppBrowser(app)
                self.browser.show()
            button.clicked.connect(start)
            self.app_buttons.append(button)


class AddWAPDialog(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        self.nameField = QtWidgets.QLineEdit()
        self.titleField = QtWidgets.QLineEdit()
        self.urlField = QtWidgets.QLineEdit()
        self.button = QtWidgets.QPushButton("Add Webapp")
        self.layout = QtWidgets.QVBoxLayout(self)
        self.layout.addWidget(self.nameField)
        self.layout.addWidget(self.titleField)
        self.layout.addWidget(self.urlField)
        self.layout.addWidget(self.button)
        self.button.clicked.connect(self.add_wap)

    @QtCore.Slot()
    def add_wap(self):
        wap_id = self.nameField.text()
        title = self.titleField.text()
        url = self.urlField.text()
        addWebApp(wap_id, title, url)
        print("added")
        self.close()


class MainWindow(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()

        self.appSelector = AppSelector(getWebapps())
        self.button = QtWidgets.QPushButton("Add WAP!")

        self.layout = QtWidgets.QVBoxLayout(self)
        self.layout.addWidget(self.appSelector)
        self.layout.addWidget(self.button)

        self.button.clicked.connect(self.magic)

    @QtCore.Slot()
    def magic(self):
        self.add_dialog = AddWAPDialog()
        self.add_dialog.resize(800, 600)
        self.add_dialog.show()


if __name__ == "__main__":
    QtCore.QCoreApplication.setOrganizationName("RasmusRendal")
    QtCore.QCoreApplication.setApplicationName("Webappifier")
    app = QtWidgets.QApplication([])
    initDB()
    parser = argparse.ArgumentParser("Webapp fun")
    parser.add_argument("--app", dest='app', nargs='?', help='Title of webapp to launch')
    args = parser.parse_args()
    signal.signal(signal.SIGINT, signal.SIG_DFL)
    if args.app != None:
        selectedWebApp = getWebapp(args.app)
        widget = WebAppBrowser(selectedWebApp)
        widget.show()
        sys.exit(app.exec_())
    else:
        widget = MainWindow()
        widget.show()
        sys.exit(app.exec_())
