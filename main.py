#!/usr/bin/env python3
import sys
from PySide2 import QtCore, QtWidgets, QtGui, QtWebEngineWidgets
import argparse
import signal



class WebApp:
    def __init__(self, title, url):
        self.url = url
        self.title = title

apps = []
apps.append(WebApp("hackernews", "https://news.ycombinator.com"))
apps.append(WebApp("tildes", "https://tildes.net"))



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


class MainWindow(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()

        self.appSelector = AppSelector(apps)
        self.button = QtWidgets.QPushButton("Click me!")
        self.urlbar = QtWidgets.QLineEdit()
        self.urlbar.setText("https://news.ycombinator.com")

        self.layout = QtWidgets.QVBoxLayout(self)
        self.layout.addWidget(self.appSelector)
        self.layout.addWidget(self.urlbar)
        self.layout.addWidget(self.button)

        self.button.clicked.connect(self.magic)

    @QtCore.Slot()
    def magic(self):
        url = self.urlbar.text()
        print(url)
        self.browser = WebAppBrowser(url)
        self.browser.resize(800, 600)
        self.browser.show()


if __name__ == "__main__":
    parser = argparse.ArgumentParser("Webapp fun")
    parser.add_argument("--app", dest='app', nargs='?', help='Title of webapp to launch')
    args = parser.parse_args()
    app = QtWidgets.QApplication([])
    signal.signal(signal.SIGINT, signal.SIG_DFL)
    if args.app != None:
        webAppTitle = args.app
        selectedWebApp = None
        print("Searching for " + args.app)
        for webapp in apps:
            if webapp.title == webAppTitle:
                selectedWebApp = webapp
                break
        if selectedWebApp == None:
            raise Exception("Unknown app selected")
        widget = WebAppBrowser(selectedWebApp)
        widget.show()
        sys.exit(app.exec_())
    else:
        widget = MainWindow()
        widget.show()
        sys.exit(app.exec_())
