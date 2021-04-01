#!/usr/bin/env python3
import sys
from PySide2 import QtCore, QtWidgets, QtGui
import argparse
import signal
from src.webappmanager import initDB, getWebapps, getWebapp, addWebApp, deleteWebApp
from src.webappBrowser import WebAppBrowser
from datetime import datetime, timedelta

class AppSettings(QtWidgets.QWidget):
    deleted = QtCore.Signal()
    def __init__(self, app_widget, app):
        super().__init__()
        self.app_widget = app_widget
        self.app = app
        self.deleteButton = QtWidgets.QPushButton("Delete " + app.title)
        self.deleteButton.clicked.connect(self.delete)
        self.layout = QtWidgets.QVBoxLayout(self)
        self.layout.addWidget(self.deleteButton)

    @QtCore.Slot()
    def delete(self):
        deleteWebApp(self.app)
        self.deleted.emit()
        self.close()


class AppWidget(QtWidgets.QVBoxLayout):
    browser = None
    deleted = QtCore.Signal()
    pressStarted = None
    def __init__(self, parent, app):
        super().__init__(parent)
        self.app = app
        self.button = QtWidgets.QPushButton()
        self.button.size = 64
        self.button.setFixedSize(QtCore.QSize(self.button.size,self.button.size))
        self.button.setObjectName("appButton")
        icon = QtGui.QIcon(app.icon_path)
        if icon.pixmap(256, 256).size().height() < self.button.size:
            self.button.setStyleSheet('QPushButton#appButton { background-image: url("' + app.icon_path + '"); }')
        else:
            self.button.setStyleSheet('QPushButton#appButton {border-image: url("' + app.icon_path + '") 0 0 0 0 stretch stretch; }')
        self.addWidget(self.button, alignment=QtGui.Qt.AlignCenter)
        self.label = QtWidgets.QLabel()
        self.label.setText(app.title)
        self.label.setAlignment(QtGui.Qt.AlignCenter)
        self.addWidget(self.label)
        self.button.installEventFilter(self)

    def eventFilter(self, source, e) -> bool:
        if isinstance(e, QtGui.QMouseEvent):
            if e.type() == QtCore.QEvent.Type.MouseButtonPress:
                self.pressStarted = datetime.now()
            if e.type() == QtCore.QEvent.Type.MouseButtonRelease:
                time_elapsed = datetime.now() - self.pressStarted
                print(time_elapsed)
                if time_elapsed > timedelta(seconds=1):
                    self.settings()
                else:
                    self.launch()
                return True
        return False

    @QtCore.Slot()
    def launch(self):
        # Eventually, maybe have a list of launched browsers?
        if self.browser != None:
            return
        self.browser = WebAppBrowser(self.app)
        self.browser.show()

    @QtCore.Slot()
    def settings(self):
        self.settingsWindow = AppSettings(self, self.app)
        self.settingsWindow.show()
        self.settingsWindow.deleted.connect(self.deleted)


class AppSelector(QtWidgets.QWidget):
    refreshPending = QtCore.Signal()
    def __init__(self, parent, apps):
        super().__init__(parent)
        self.setObjectName("appSelector")
        self.apps = apps
        self.layout = QtWidgets.QVBoxLayout(self)
        self.gridlayout = QtWidgets.QGridLayout()
        self.layout.addLayout(self.gridlayout)
        self.app_buttons = []
        for i in range(len(self.apps)):
            app = self.apps[i]
            button = AppWidget(self, app)
            button.deleted.connect(self.refresh)
            self.gridlayout.addLayout(button,i//4,i%4,alignment=QtCore.Qt.AlignTop)
            self.app_buttons.append(button)
        for i in range(self.gridlayout.columnCount()):
            self.gridlayout.setColumnStretch(i, 1)
        self.layout.addStretch()

    @QtCore.Slot()
    def refresh(self):
        self.refreshPending.emit()


class AddWAPDialog(QtWidgets.QWidget):
    added = QtCore.Signal()
    def __init__(self):
        super().__init__()
        self.titleField = QtWidgets.QLineEdit()
        self.urlField = QtWidgets.QLineEdit()
        self.button = QtWidgets.QPushButton("Add Webapp")
        self.layout = QtWidgets.QFormLayout(self)
        self.layout.addRow("Title:", self.titleField)
        self.layout.addRow("URL:", self.urlField)
        self.layout.addWidget(self.button)
        self.titleField.returnPressed.connect(self.add_wap)
        self.urlField.returnPressed.connect(self.add_wap)
        self.button.clicked.connect(self.add_wap)

    @QtCore.Slot()
    def add_wap(self):
        title = self.titleField.text()
        url = self.urlField.text()
        wap = addWebApp(title, url)
        WebAppBrowser(wap)
        self.added.emit()
        self.close()


class MainWindow(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        self.setObjectName("MainWindow")

        self.button = QtWidgets.QPushButton("Add WAP!")
        self.appSelector = AppSelector(self, getWebapps())
        self.appSelector.refreshPending.connect(self.refresh)

        self.layout = QtWidgets.QVBoxLayout(self)
        self.layout.addWidget(self.appSelector)
        self.layout.addWidget(self.button)

        self.button.clicked.connect(self.magic)

    @QtCore.Slot()
    def magic(self):
        self.add_dialog = AddWAPDialog()
        self.add_dialog.resize(800, 600)
        self.add_dialog.added.connect(self.refresh)
        self.add_dialog.show()

    @QtCore.Slot()
    def refresh(self):
        oldAppSelector = self.appSelector
        self.appSelector = AppSelector(self, getWebapps())
        self.appSelector.refreshPending.connect(self.refresh)
        oldAppSelector.deleteLater()
        self.layout.replaceWidget(oldAppSelector, self.appSelector)


if __name__ == "__main__":
    import pathlib
    QtCore.QCoreApplication.setOrganizationName("RasmusRendal")
    QtCore.QCoreApplication.setApplicationName("Galago")
    app = QtWidgets.QApplication([])
    stylesheet_file = open(pathlib.Path(__file__).parent.absolute() / "stylesheet.css", "r")
    stylesheet = stylesheet_file.read()
    stylesheet_file.close()
    app.setStyleSheet(stylesheet)
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
