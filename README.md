The application is a replacement for the Microinvest Utility Center application.

Features:
* Zeroing of the partner's balance;
* Deleting of a partner's balance;
* Replenishment of the partner's balance;
* History of your partner's operations;
* Logging of an application's actions.

Support for Windows OS and MS SQL.

Compile to exe

> python -m nuitka --follow-imports  --windows-disable-console --standalone --plugin-enable=pyqt5 --mingw64 mo.py