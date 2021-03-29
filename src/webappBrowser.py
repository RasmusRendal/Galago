from PySide2 import QtCore, QtWidgets, QtWebEngineWidgets
import os
from src.webappmanager import updateIcon

class WebAppBrowser(QtWidgets.QWidget):
    def __init__(self, webapp):
        super().__init__()
        self.webapp = webapp
        self.profile = None
        if self.webapp.persist:
            self.profile = QtWebEngineWidgets.QWebEngineProfile(webapp.title)
        else:
            self.profile = QtWebEngineWidgets.QWebEngineProfile()
        self.page = QtWebEngineWidgets.QWebEnginePage(self.profile)
        self.view = QtWebEngineWidgets.QWebEngineView()
        self.view.setPage(self.page)
        self.view.load(QtCore.QUrl(self.webapp.url))
        self.layout = QtWidgets.QVBoxLayout(self)
        self.layout.addWidget(self.view)
        self.layout.setContentsMargins(QtCore.QMargins(0, 0, 0, 0))
        self.setWindowTitle(self.webapp.title)
        self.view.iconChanged.connect(self.iconChangedListener)

    @QtCore.Slot()
    def iconChangedListener(self, icon):
        updateIcon(self.webapp.title, icon)
        self.view.iconChanged.disconnect(self.iconChangedListener)
