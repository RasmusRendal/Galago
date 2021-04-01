# Galago
![Logo](https://raw.githubusercontent.com/RasmusRendal/Galago/master/resources/logo-rounded.png)

Galago is a web app viewer & manager specifically designed for the mobile Linux use case.
It is QtWebEngine-based and offers the ability to create custom desktop files.
This software is work in progress, but contributions are welcome.

## Installation
On PostMarketOS, to install and launch the application, execute the following commands:
```
$ sudo apk add git python3 py3-pyside2 qt5-qtbase-sqlite
$ git clone https://github.com/RasmusRendal/Galago.git # Clone the Git repository
$ cd Galago # Change into the Repo
$ ./main.py # Execute the main python script
```

## Files created
Galago creates desktop entries for all the webapps you create, with the naming scheme `galago-<NAME>.desktop`, placed in `$XDG_DATE_HOME/applications/`.
All other files are stored in `$XDG_DATA_HOME/RasmusRendal/Galago`.
