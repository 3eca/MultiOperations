__author__ = '3eca'
__github__ = 'https://github.com/3eca'
__telegram__ = '@holyNash'

if __name__ == '__main__':
    import gui

    app = gui.QApplication([])
    main_window = gui.MainWindow()
    main_window.show()

    app.exec()

