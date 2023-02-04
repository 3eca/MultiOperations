__author__ = '3eca'
__github__ = 'https://github.com/3eca'
__telegram__ = '@holyNash'

from logging import getLogger, FileHandler, Formatter, INFO
from os import makedirs, path, environ, chdir, listdir
from re import search
from PyQt6.QtCore import QRect, Qt
from PyQt6.QtGui import QFont
from PyQt6.QtWidgets import (QMainWindow, QLabel, QLineEdit, QPushButton,
                             QMessageBox, QComboBox, QTableWidget, QDialog,
                             QTableWidgetItem, QApplication, QTextBrowser)

from database import DB


class MainWindow(QMainWindow):
    __height_label = 15
    __height_input = 18
    __height_button = 25

    def __init__(self) -> None:
        super().__init__()

        self.__path_data = environ['APPDATA'] + '\\Multi Operations'
        self.__check_files()

        self.__logger = getLogger()
        self.__logger.setLevel(INFO)
        self.__handler = FileHandler('logs')
        self.__handler.setLevel(INFO)
        self.__handler.setFormatter(
            Formatter('[%(asctime)s - %(levelname)s]: %(message)s')
        )
        self.__logger.addHandler(self.__handler)
        self.__template = 'partner=%s operation=%s count=%s'

        self.__db_session = None
        self.__status_db = None
        self.__white_color = 'background-color: #fff;'
        self.__partners_dict = {}
        self.__selected_partners = []
        self.__history_partner = {}
        self.__value_accrual = None
        self.__value_write_off = None

        self.setWindowTitle('Multi Operations')
        self.setStyleSheet('background-color: rgb(159, 159, 159);')
        self.setFixedSize(510, 450)
        self.__font = QFont()
        self.__font.setPointSize(12)

        self.__server = QLabel('SQL server:', self)
        self.__db = QLabel('DB name:', self)
        self.__user = QLabel('User:', self)
        self.__pwd = QLabel('Password:', self)
        self.__partners = QLabel('Partners group:', self)
        self.__server_input = QLineEdit(self)
        self.__db_input = QLineEdit(self)
        self.__user_input = QLineEdit(self)
        self.__pwd_input = QLineEdit(self)
        self.__check_db_button = QPushButton('Check connection', self)
        self.__update_button = QPushButton('Refresh', self)
        self.__btn_zeroing = QPushButton('Zeroing', self)
        self.__btn_accrual = QPushButton('Accrual', self)
        self.__btn_write_off = QPushButton('Write-off', self)
        self.__btn_history = QPushButton('History', self)
        self.__btn_logs = QPushButton('Logs', self)
        self.__btn_all_select = QPushButton('Select\n all', self)
        self.__btn_help = QPushButton('Help', self)
        self.__partners_box = QComboBox(self)
        self.__table = QTableWidget(self)

        self.__set_property()

    def __check_files(self) -> None:
        """
        Check available directory and files for work app.
        """
        if not path.exists(self.__path_data):
            makedirs(self.__path_data)

        chdir(self.__path_data)
        configuration = 'config'
        if configuration not in listdir():
            with open(configuration, 'w', encoding='cp1251') as file:
                file.write('')

        logs = 'logs'
        if logs not in listdir():
            with open(logs, 'w', encoding='cp1251') as file:
                file.write('')

    @staticmethod
    def __write_config(config: str) -> None:
        """
        Write config
        :param config: text config
        """
        configuration = 'config'
        with open(configuration, 'w', encoding='cp1251') as file:
            file.write(config)

    def __window_error(self, message: str = None) -> None:
        """
        Create modal window with text error when fail connection to db.
        :param message: text for modal window.
        """
        try:
            if not message:
                self.__check_db_button.setStyleSheet('background-color: red;'
                                                     'padding-bottom: 4px;'
                                                     )
                QMessageBox.critical(self,
                                     'Error',
                                     str(self.__db_session.error),
                                     QMessageBox.StandardButton.Ok
                                     )
            else:
                QMessageBox.critical(self,
                                     'Error',
                                     message,
                                     QMessageBox.StandardButton.Ok
                                     )
        except AttributeError:
            pass

    def __window_accrual(self) -> None:
        """
        Create modal window with query for value accrual partner.
        """
        if self.__status_db:
            window = QMessageBox(self)
            window.setObjectName('window_accrual')
            window.setIcon(QMessageBox.Icon.Information)
            window.setWindowTitle('Accrual balance')
            window.setText('Input value:')
            window.setStandardButtons(
                QMessageBox.StandardButton.Ok | QMessageBox.StandardButton.Cancel
            )

            value_accrual = QLineEdit(window)
            value_accrual.setStyleSheet(self.__white_color)
            value_accrual.setFont(self.__font)
            value_accrual.setGeometry(70, 30, 50, 20)

            value_accrual.setFocus()
            return_value = window.exec()

            if return_value == QMessageBox.StandardButton.Ok:
                self.__value_accrual = value_accrual.text()
        else:
            self.__window_error('No connection to db')

    def __window_write_off(self) -> None:
        """
        Create modal window with query for value write-off partner.
        """
        self.__value_write_off = None
        window = QMessageBox(self)
        window.setObjectName('window_write_off')
        window.setIcon(QMessageBox.Icon.Information)
        window.setWindowTitle('Write-off balance')
        window.setText('Input value:')
        window.setStandardButtons(
            QMessageBox.StandardButton.Ok | QMessageBox.StandardButton.Cancel
        )

        value_write_off = QLineEdit(window)
        value_write_off.setStyleSheet(self.__white_color)
        value_write_off.setFont(self.__font)
        value_write_off.setGeometry(70, 30, 50, 20)

        value_write_off.setFocus()
        return_value = window.exec()

        if return_value == QMessageBox.StandardButton.Ok:
            self.__value_write_off = value_write_off.text()

    def __window_history(self) -> None:
        """
        Create modal window with history for partner.
        """
        self.__get_status_checkbox()

        if self.__selected_partners and self.__status_db:
            if len(self.__selected_partners) != 1:
                self.__window_error(message='Selected over 1 partner(s).')
            else:
                self.__get_history()
                window = QDialog(self)
                window.setWindowTitle('History partner')
                window.setFixedSize(700, 500)
                window.setObjectName('window_history')

                period_label = QLabel('Period:', window)
                period_label.setGeometry(QRect(10, 465, 50, self.__height_label))
                period_label.setFont(self.__font)

                period_input = QLineEdit(window)
                period_input.setGeometry(QRect(60, 465, 180, self.__height_input))
                period_input.setFont(self.__font)
                period_input.setStyleSheet(self.__white_color)
                period_input.setPlaceholderText('2023-01-31 2023-12-31')

                table = QTableWidget(window)
                table.setObjectName('table_history')
                table.setGeometry(QRect(0, 0, 700, 455))
                table.setFont(self.__font)
                table.setStyleSheet(self.__white_color)
                table.setColumnCount(6)
                table.setRowCount(len(self.__history_partner))
                table.setColumnWidth(0, 80)
                table.setColumnWidth(1, 80)
                table.setColumnWidth(2, 220)
                table.setColumnWidth(3, 50)
                table.setColumnWidth(4, 100)
                table.setColumnWidth(5, 165)
                table.setHorizontalHeaderLabels(
                    [
                        'User',
                        'Document',
                        'Date',
                        'Count',
                        'Operation',
                        'Object',
                    ]
                )
                table.verticalHeader().setVisible(False)

                button = QPushButton('Apply filter', window)
                button.setGeometry(QRect(250, 463, 150, self.__height_button))
                button.setStyleSheet(
                    self.__white_color +
                    'padding-bottom: 4px;'
                )
                button.setFont(self.__font)
                button.clicked.connect(
                    lambda: self.__filling_window_history(
                        table,
                        period_input.text()
                    )
                )

                row = 0
                for history in self.__history_partner:
                    table.setItem(row, 0, QTableWidgetItem(history[0]))
                    table.setItem(row, 1, QTableWidgetItem(str(history[1])))
                    table.setItem(row, 2, QTableWidgetItem(str(history[2])))
                    table.setItem(row, 3, QTableWidgetItem(str(int(history[3]))))
                    table.setItem(row, 4, QTableWidgetItem(history[4]))
                    table.setItem(row, 5, QTableWidgetItem(history[5]))
                    row += 1

                window.exec()
        elif not self.__status_db:
            self.__window_error('No connection to db.')
        else:
            self.__window_error('Not selected partner(s).')

    def __window_help(self) -> None:
        """
        Create modal window help.
        """
        info = '''
        Partners group: available partner groups
        
        Refresh: updating the list of the selected group of partners
        Zeroing: reset partner(s) balance
        Accrual: replenishment of partner(s) balance
        Write-off: write-off of partner(s) balance
        History: viewing partner history
        Logs: viewing the history of actions in the program
        
        Directory path: %s
        ''' % self.__path_data
        QMessageBox.information(
            self,
            'Help',
            info,
            QMessageBox.StandardButton.Ok
                                )

    def __window_log(self) -> None:
        """
        Create modal window with program logs.
        """
        window = QDialog(self)
        window.setWindowTitle('Logs')
        window.setFixedSize(800, 340)

        text_edit = QTextBrowser(window)
        text_edit.setGeometry(QRect(0, 0, 800, 300))
        text_edit.setFont(self.__font)
        text_edit.setStyleSheet(self.__white_color)

        with open('logs', encoding='cp1251') as log:
            [text_edit.append(line.rstrip()) for line in log.readlines()]

        label_date = QLabel('Date:', window)
        label_partner = QLabel('Partner:', window)
        input_date = QLineEdit(window)
        input_partner = QLineEdit(window)
        button = QPushButton('Apply filter', window)

        for element in (label_date, label_partner, input_date, input_partner, button):
            element.setFont(self.__font)

        for element in (input_date, input_partner, button):
            element.setStyleSheet(self.__white_color)

        label_date.setGeometry(QRect(10, 310, 55, self.__height_label))
        label_partner.setGeometry(QRect(200, 310, 65, self.__height_label))
        input_date.setGeometry(QRect(60, 310, 130, self.__height_input))
        input_partner.setGeometry(QRect(270, 310, 130, self.__height_input))
        button.setGeometry(QRect(450, 307, 140, self.__height_button))

        button.clicked.connect(lambda: self.__filter_log(
            text_edit, input_date.text(), input_partner.text()
        ))

        window.show()

    @staticmethod
    def __filter_log(widget: QTextBrowser, date: str, partner: str) -> None:
        """
        Get logs with apply filters.
        :param widget: link object.
        :param date: date for search in logs.
        :param partner: partner for search in logs.
        """
        widget.clear()
        if date and partner:
            with open('logs', encoding='cp1251') as log:
                [widget.append(line.rstrip()) for line in log.readlines() if
                 search(date, line) and search(partner, line)]
        elif date:
            with open('logs', encoding='cp1251') as log:
                [widget.append(line.rstrip()) for line in log.readlines() if
                 search(date, line)]
        elif partner:
            with open('logs', encoding='cp1251') as log:
                [widget.append(line.rstrip()) for line in log.readlines() if
                 search(partner, line)]
        else:
            pass

    def __filling_window_history(self,
                                 table: QTableWidget,
                                 period: str = None) -> None:
        """
        Filling window data.
        :param table: link object.
        :param period: Date period.
        """
        self.__get_history(period=period)
        table.setRowCount(len(self.__history_partner))
        row = 0
        for history in self.__history_partner:
            table.setItem(row, 0, QTableWidgetItem(history[0]))
            table.setItem(row, 1, QTableWidgetItem(str(history[1])))
            table.setItem(row, 2, QTableWidgetItem(str(history[2])))
            table.setItem(row, 3, QTableWidgetItem(str(int(history[3]))))
            table.setItem(row, 4, QTableWidgetItem(history[4]))
            row += 1

    def __filling_combobox_ticket(self, widget: QComboBox) -> None:
        """
        Filling combobox data.
        :param widget: link object.
        """
        if not self.__status_db:
            with self.__db_session as session:
                widget.addItems(
                    [group for groups in session.select(
                        'select name from goodsgroups') for group in groups]
                )

    def __set_property(self) -> None:
        """
        Set text for labels, input lines.
        Placing labels, input lines.
        Add action to buttons.
        """
        labels = [
            self.__server,
            self.__db,
            self.__user,
            self.__pwd,
        ]
        inputs = [
            self.__server_input,
            self.__db_input,
            self.__user_input,
            self.__pwd_input,
        ]
        elements = []
        elements.extend(
            [
                *inputs,
                self.__check_db_button,
                self.__partners_box,
                self.__update_button,
                self.__table,
            ]
        )
        buttons_style = [
            self.__check_db_button,
            self.__btn_zeroing,
            self.__btn_accrual,
            self.__btn_write_off,
            self.__btn_history,
            self.__btn_logs,
            self.__btn_help,
            self.__btn_all_select,
        ]
        buttons_positions = [
            self.__btn_zeroing,
            self.__btn_accrual,
            self.__btn_write_off,
            self.__btn_history,
            self.__btn_logs,
        ]

        for position_x in range(30, 251, 220):
            for position_y in range(5, 26, 20):
                for element in labels:
                    element.setGeometry(QRect(
                        position_x,
                        position_y,
                        100,
                        self.__height_label
                    ))
                    element.setFont(self.__font)
                    labels.remove(labels[0])
                    break

        for position_x in range(120, 331, 200):
            for position_y in range(5, 26, 20):
                for element in inputs:
                    element.setGeometry(QRect(
                        position_x,
                        position_y,
                        130,
                        self.__height_input
                    ))
                    inputs.remove(inputs[0])
                    break

        for position_y in range(110, 231, 30):
            for button in buttons_positions:
                button.setGeometry(QRect(
                    410,
                    position_y,
                    95,
                    self.__height_button
                ))
                buttons_positions.remove(buttons_positions[0])
                break

        for element in elements:
            if element == self.__table:
                element.setStyleSheet(
                    'QTableWidget {background-color: #fff;}'
                    'QAbstractItemView::indicator {width: 37px; height: 37px;}'
                    'QScrollBar {background-color: #fff;}'
                )
            else:
                element.setStyleSheet(self.__white_color)
            element.setFont(self.__font)

        for button in buttons_style:
            button.setFont(self.__font)
            button.setStyleSheet(
                self.__white_color +
                'padding-bottom: 4px;'
            )

        with open('config', encoding='cp1251') as config:
            lines = config.readlines()
            if len(lines) == 4:
                self.__server_input.setText(lines[0].rstrip())
                self.__db_input.setText(lines[1].rstrip())
                self.__user_input.setText(lines[2].rstrip())
                self.__pwd_input.setText(lines[3].strip())

        self.__check_db_button.setGeometry(170, 50, 170, self.__height_button)
        self.__partners.setGeometry(QRect(30, 80, 140, 20))
        self.__partners_box.setGeometry(QRect(170, 80, 130, 20))
        self.__update_button.setGeometry(
            QRect(320, 80, 80, self.__height_button)
        )
        self.__table.setGeometry(QRect(5, 110, 400, 330))

        self.__table.setColumnCount(3)
        self.__table.setColumnWidth(0, 1)
        self.__table.setColumnWidth(1, 260)
        self.__table.setColumnWidth(2, 99)
        self.__table.setHorizontalHeaderLabels(['#', 'Partner', 'Balance'])
        self.__table.verticalHeader().setVisible(False)

        self.__partners.setFont(self.__font)

        self.__btn_all_select.setGeometry(
            QRect(410, 350, 95, self.__height_button * 2)
        )
        self.__btn_help.setGeometry(QRect(410, 415, 95, self.__height_button))

        self.__check_db_button.clicked.connect(self.__check_connection)
        self.__update_button.clicked.connect(self.__get_partners)
        self.__btn_history.clicked.connect(self.__window_history)
        self.__btn_logs.clicked.connect(self.__window_log)
        self.__btn_help.clicked.connect(self.__window_help)
        self.__btn_zeroing.clicked.connect(self.__zeroing)
        self.__btn_accrual.clicked.connect(self.__accrual)
        self.__btn_write_off.clicked.connect(self.__write_off)
        self.__btn_all_select.clicked.connect(self.__select_all_partners)

    def __select_all_partners(self) -> None:
        """
        Set select all row for operations.
        """
        if self.__status_db:
            for row in range(self.__table.rowCount()):
                self.__table.item(row, 0).setCheckState(Qt.CheckState.Checked)

    def __write_off(self) -> None:
        """
        Write-off inserted value balance selected partners.
        """
        self.__get_status_checkbox()
        if self.__selected_partners and self.__status_db:
            self.__window_write_off()
            if self.__value_write_off:
                to_query = (0, 36, -1, 1)
                for partner in self.__selected_partners:
                    with self.__db_session as session:
                        self.__logger.info(
                            self.__template % (
                                partner[0], 'write-off', self.__value_write_off
                            )
                        )
                        session.execute(
                            'insert into payments(Acct, OperType, PartnerID, Qtty, '
                            'Mode, Sign, Date, UserID, ObjectID, UserRealTime, Type, '
                            'TransactionNumber, EndDate)'
                            f'values({to_query[0]},'
                            f'{to_query[1]}, '
                            f'(select id from partners where company=\'{partner[0]}\'),'
                            f'{self.__value_write_off},'
                            f'{to_query[2]},'
                            f'{to_query[3]},'
                            'GETDATE(),'
                            f'{to_query[3]},'
                            f'{to_query[3]},'
                            'GETDATE(),'
                            f'{to_query[3]},'
                            '\'Write-off IT Admin\','
                            'GETDATE())'
                        )

                self.__get_partners()
                QMessageBox.information(
                    self, 'Operation done', 'Done', QMessageBox.StandardButton.Ok
                )
        elif not self.__status_db:
            self.__window_error('No connection to db.')
        else:
            self.__window_error('Not selected partner(s).')

    def __zeroing(self) -> None:
        """
        Total write-off balance selected partners.
        """
        self.__get_status_checkbox()
        if self.__selected_partners and self.__status_db:
            to_query = (0, 36, -1, 1)
            for partner in self.__selected_partners:
                with self.__db_session as session:
                    self.__logger.info(
                        self.__template % (partner[0], 'Zeroing', partner[1])
                    )
                    session.execute(
                        'insert into payments(Acct, OperType, PartnerID, Qtty, '
                        'Mode, Sign, Date, UserID, ObjectID, UserRealTime, Type, '
                        'TransactionNumber, EndDate)'
                        f'values({to_query[0]},'
                        f'{to_query[1]}, '
                        f'(select id from partners where company=\'{partner[0]}\'),'
                        f'{partner[1]},'
                        f'{to_query[2]},'
                        f'{to_query[3]},'
                        'GETDATE(),'
                        f'{to_query[3]},'
                        f'{to_query[3]},'
                        'GETDATE(),'
                        f'{to_query[3]},'
                        '\'Zeroing IT Admin\','
                        'GETDATE())'
                    )

            self.__get_partners()
            QMessageBox.information(
                self, 'Operation done', 'Done', QMessageBox.StandardButton.Ok
            )
        elif not self.__status_db:
            self.__window_error('No connection to db.')
        else:
            self.__window_error('Not selected partner(s).')

    def __accrual(self) -> None:
        """
        Accrual inserted value balance for selected partners.
        """
        self.__value_accrual = None
        self.__get_status_checkbox()
        to_query = (0, 36, 1)

        if self.__selected_partners and self.__status_db:
            self.__window_accrual()

            if self.__value_accrual:
                for partner in self.__selected_partners:
                    with self.__db_session as session:
                        self.__logger.info(
                            self.__template % (
                                partner[0], 'Accrual', self.__value_accrual
                            )
                        )
                        session.execute(
                            'insert into payments(Acct, OperType, PartnerID, Qtty, '
                            'Mode, Sign, Date, UserID, ObjectID, UserRealTime, Type, '
                            'TransactionNumber, EndDate)'
                            f'values({to_query[0]},'
                            f'{to_query[1]}, '
                            f'(select id from partners where company=\'{partner[0]}\'),'
                            f'{self.__value_accrual},'
                            f'{to_query[2]},'
                            f'{to_query[2]},'
                            'GETDATE(),'
                            f'{to_query[2]},'
                            f'{to_query[2]},'
                            'GETDATE(),'
                            f'{to_query[2]},'
                            '\'Accrual IT Admin\','
                            'GETDATE())'
                        )

                self.__get_partners()
                QMessageBox.information(
                    self, 'Operation done', 'Done', QMessageBox.StandardButton.Ok
                )
        elif not self.__status_db:
            self.__window_error('No connection to db.')
        else:
            self.__window_error('Not selected partner(s).')

    def __get_status_checkbox(self) -> None:
        """
        Append into list selected partners.
        """
        self.__selected_partners.clear()
        if self.__status_db:
            for row in range(self.__table.rowCount()):
                if self.__table.item(row,
                                     0).checkState() == Qt.CheckState.Checked:
                    self.__selected_partners.append(
                        (
                            self.__table.item(row, 1).text(),
                            self.__table.item(row, 2).text()
                        )
                    )

    def __get_partners(self) -> None:
        """
        Get all partners where match to selected group from combobox into dict.
        """
        if self.__status_db:
            with self.__db_session as session:
                self.__partners_dict = {
                    name: int(balance) for name, balance in session.select(
                        'select p.company, SUM(Qtty*Mode) '
                        'from payments pa '
                        'join partners p on pa.partnerid=p.id '
                        'join partnersgroups pg on p.groupid=pg.id '
                        "where p.code != '' "
                        f"and pg.name=\'{self.__partners_box.currentText()}\' "
                        'group by p.company')
                }

        else:
            self.__partners_dict = {}

        self.__update_table()

    def __get_history(self, period: str = None) -> None:
        """
        Get history partner from db.
        :period: date period.
        """
        if self.__status_db:
            if not period:
                for partner in self.__selected_partners:
                    with self.__db_session as session:
                        self.__history_partner = session.select(
                            'select \'IT Admin\''
                            ',pa.acct'
                            ',pa.userrealtime'
                            ',pa.qtty'
                            ',case pa.mode when 1 then \'Accrual\' else \'Write-off\' end '
                            ',o.name '
                            'from partners p '
                            'join payments pa on p.id=pa.partnerid '
                            'join users u on pa.userid=u.id '
                            'join objects o on pa.objectid=o.id '
                            f'where p.company=\'{partner[0]}\' '
                            'and u.name in (\'Служебный пользователь\', \'Service user\') '
                            'union all '
                            'select u.name'
                            ',pa.acct'
                            ',pa.userrealtime'
                            ',pa.qtty'
                            ',case pa.mode when 1 then \'Accrual\' else \'Sale\' end '
                            ',o.name '
                            'from partners p '
                            'join payments pa on p.id=pa.partnerid '
                            'join users u on pa.userid=u.id '
                            'join objects o on pa.objectid=o.id '
                            f'where p.company=\'{partner[0]}\' '
                            'and pa.mode!=1 '
                            'and pa.opertype=2 '
                            'order by pa.userrealtime'
                        )
            else:
                if period.count(' '):
                    for partner in self.__selected_partners:
                        with self.__db_session as session:
                            self.__history_partner = session.select(
                                'select \'IT Admin\''
                                ',pa.acct'
                                ',pa.userrealtime'
                                ',pa.qtty'
                                ',case pa.mode when 1 then \'Accrual\' else \'Write-off\' end '
                                ',o.name '
                                'from partners p '
                                'join payments pa on p.id=pa.partnerid '
                                'join users u on pa.userid=u.id '
                                'join objects o on pa.objectid=o.id '
                                f'where p.company=\'{partner[0]}\' '
                                'and u.namein (\'Служебный пользователь\', \'Service user\') '
                                f'and date between convert(date,\'{period.split()[0]}\',102) and convert(date,\'{period.split()[1]}\',102) '
                                'union all '
                                'select u.name'
                                ',pa.acct'
                                ',pa.userrealtime'
                                ',pa.qtty'
                                ',case pa.mode when 1 then \'Accrual\' else \'Sale\' end '
                                ',o.name '
                                'from partners p '
                                'join payments pa on p.id=pa.partnerid '
                                'join users u on pa.userid=u.id '
                                'join objects o on pa.objectid=o.id '
                                f'where p.company=\'{partner[0]}\' '
                                'and pa.mode!=1 '
                                'and pa.opertype=2 '
                                f'and date between convert(date,\'{period.split()[0]}\',102) and convert(date,\'{period.split()[1]}\',102) '
                                'order by pa.userrealtime'
                            )
                else:
                    for widget in self.findChildren(QDialog):
                        if widget.objectName() == 'window_history':
                            QMessageBox.critical(widget,
                                                'Invalid format period',
                                                f'Invalid format period {period}',
                                                QMessageBox.StandardButton.Ok
                                               )

    def __update_table(self):
        """
        Filling table data from dict.
        """
        self.__table.setRowCount(len(self.__partners_dict))
        row = 0
        for partner, balance in self.__partners_dict.items():
            check_box = QTableWidgetItem()
            check_box.setFlags(
                Qt.ItemFlag.ItemIsUserCheckable |
                Qt.ItemFlag.ItemIsEnabled
            )
            check_box.setCheckState(Qt.CheckState.Unchecked)
            self.__table.setItem(row, 0, check_box)
            self.__table.setItem(row, 1, QTableWidgetItem(partner))
            self.__table.setItem(row, 2, QTableWidgetItem(str(balance)))
            row += 1

    def __init_db(self) -> None:
        """
        Create connection to db.
        """
        self.__db_session = DB(server=self.__server_input.text(),
                               database=self.__db_input.text(),
                               user=self.__user_input.text(),
                               password=self.__pwd_input.text())

    def __check_connection(self) -> None:
        """
        Check connection to db.
        """
        self.__init_db()

        conf = f'{self.__server_input.text()}\n' \
               f'{self.__db_input.text()}\n' \
               f'{self.__user_input.text()}\n' \
               f'{self.__pwd_input.text()}'
        self.__write_config(conf)

        if not self.__status_db:
            with self.__db_session as session:
                if session:
                    self.__status_db = session.select(
                        'select state_desc '
                        'from sys.databases '
                        f'where name = \'{self.__db_input.text()}\'')[0][0]
                    if self.__status_db == 'ONLINE':
                        self.__check_db_button.setStyleSheet(
                            'background-color: green;'
                            'padding-bottom: 4px;'
                        )
                        self.__partners_box.addItems(
                            [partner for partners in session.select(
                                'select pg.name '
                                'from partnersgroups pg'
                            ) for partner in partners]
                        )
                else:
                    self.__check_db_button.clicked.connect(self.__window_error)
                    self.__status_db = None


if __name__ == '__main__':
    pass
