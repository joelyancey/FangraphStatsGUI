#!/usr/bin/env python3
'''
Demonstrates:
- Loading data from CSV file via cli and open file dialog
- Displaying data in pretty table
- Selecting table data and returning pandas dataframe
- Performing some analysis on arbitrary user data
- Using classes from Qt documentation ('PandasModel')
- QApplication, QMainWindow, QWidget,  QFileDialog, QTableView, QPushButton, QTabWidget, QGridLayout, QHBoxLayout,
  QErrorMessage, QGroupBox, QTextEdit, QSplitter, QStatusBar

Launch the GUI:
$ python3 gui.py
'''


import sys
import argparse
import pandas as pd

from PyQt5.QtCore import QSize, Qt, pyqtSlot, QCoreApplication, QAbstractTableModel, QModelIndex
from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget, QPushButton, QTabWidget, QGridLayout, \
    QHBoxLayout, QFileDialog, QTableView, QErrorMessage, QGroupBox, QTextEdit, QSplitter, QStatusBar, \
    QAbstractItemView


class MainWindow(QMainWindow):

    def __init__(self, file=None):
        '''This is the constructor'''
        super().__init__()

        self.setupUI()

        self._file = file # path to a file on disk
        if self._file != None:
            self.import_data(self._file)
            self.load_dataframe()

        self._selected_rows = []

    def import_data(self, path):
        '''Import Data From CSV File Into Pandas Dataframe'''
        print('Reading CSV data into pandas dataframe...')
        self._dataframe = pd.read_csv(path)

    @pyqtSlot()
    def import_dialog(self):
        '''Get User File Selection Dialog
        Note: This function is a 'Slot' function. It is connected
        to the 'clicked' signal of the import_button'''
        print('Getting User File Selection...')
        dialog = QFileDialog()
        dialog.setOption(QFileDialog.DontUseNativeDialog)
        dialog.setWindowTitle('Open Data (*.csv)')
        dialog.setNameFilter('Text Files (*.csv)')
        dialog.setViewMode(QFileDialog.Detail)
        if dialog.exec() == QFileDialog.Accepted:
            self._file = dialog.selectedFiles()[0]
            self.import_data(self._file)
            self.load_dataframe()
            print("Loaded: '%s'" % self._file)
        else:
            print("Nothing Loaded")

    def load_dataframe(self):
        '''Load Dataframe Into GUI Table'''
        if isinstance(self._dataframe, pd.DataFrame):
            self.table_widget.setModel(PandasModel(self._dataframe))
            self.table_widget.setSelectionMode(QAbstractItemView.ExtendedSelection)
            self.selection_model = self.table_widget.selectionModel()
            self.selection_model.selectionChanged.connect(self.selected_rows_changed)
        else:
            error_dialog = QErrorMessage()
            error_dialog.showMessage('No data loaded!')

    def selection(self):
        '''Return Pandas Dataframe From Selection'''
        return self._dataframe.iloc[self._selection_indexes]

    def clear_selection(self):
        '''Clear User Selection'''
        self._selected_rows = []
        self.table_widget.clearSelection()
        self.display_results('')
        print('Selection Cleared')

    def selected_rows_changed(self):
        '''Slot That Connects To Selection Changed Signal'''
        print('Selection Changed!')
        selection = self.table_widget.selectedIndexes()
        self._selection_indexes = list(set([row.row() for row in selection]))

        print(self.selection())
        self.status_bar.showMessage('Selected Rows: %s' % str(self._selection_indexes))
        print('Selected Rows: %s' % str(self._selection_indexes))

        self.display_results('%s\n\n----Selected Averages----\n'
                             'Average Group 1 : %f\n'
                             'Average Group 2 : %f'
                             % (str(self.selection()), self.grp1_avg(), self.grp2_avg()))

    def grp1_avg(self):
        '''Compute Group 1 Average From Selection'''
        return float(self.selection()['Group_1'].mean())

    def grp2_avg(self):
        '''Compute Group 2 Average From Selection'''
        return float(self.selection()['Group_2'].mean())

    def display_results(self, text):
        '''Display Text In Read-only Text Widget'''
        self.results_widget.setText(text)

    def setupUI(self):
        '''Setup the UI'''
        self.setWindowTitle("Demo GUI - Spinehead")
        self.resize(QSize(700, 700))  # size of main window
        self.tab_widget = QTabWidget()
        self.setCentralWidget(self.tab_widget)
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)

        self.tab1 = QWidget()
        self.tab2 = QWidget()
        self.tab1_layout = QGridLayout()
        self.tab2_layout = QGridLayout()
        self.tab1.setLayout(self.tab1_layout)
        self.tab2.setLayout(self.tab2_layout)
        self.tab_widget.addTab(self.tab1, "Data")
        self.tab_widget.addTab(self.tab2, "Another Tab")

        self.import_button = QPushButton('Import Data')
        self.import_button.setFixedSize(QSize(120, 28))
        self.import_button.clicked.connect(self.import_dialog)

        self.clear_button = QPushButton('Clear')
        self.clear_button.setFixedSize(QSize(120, 28))
        self.clear_button.clicked.connect(self.clear_selection)

        self.quit_button = QPushButton('Quit')
        self.quit_button.setFixedSize(QSize(120, 28))
        self.quit_button.clicked.connect(QCoreApplication.instance().quit)

        self.buttons = QGroupBox('Control Panel')
        self.buttons_layout = QHBoxLayout()
        self.buttons_layout.addWidget(self.import_button)
        self.buttons_layout.addWidget(self.clear_button)
        self.buttons_layout.addWidget(self.quit_button)
        self.buttons_layout.addStretch()
        self.buttons.setLayout(self.buttons_layout)

        self.table_widget = QTableView()
        self.table_widget.horizontalHeader().setStretchLastSection(True)
        self.table_widget.setAlternatingRowColors(True)
        self.table_widget.setSelectionBehavior(QTableView.SelectRows)

        self.results_widget = QTextEdit('Results')
        self.results_widget.setReadOnly(True)

        self.splitter = QSplitter(Qt.Vertical)
        self.splitter.addWidget(self.table_widget)
        self.splitter.addWidget(self.results_widget)

        self.tab1_layout.addWidget(self.splitter, 0, 0)
        self.tab1_layout.addWidget(self.buttons, 1, 0)


class PandasModel(QAbstractTableModel):
    """A model to interface a Qt table_widget with pandas dataframe.
    Adapted from Qt Documentation Example:
    https://doc.qt.io/qtforpython/examples/example_external__pandas.html"""
    def __init__(self, dataframe: pd.DataFrame, parent=None):
        QAbstractTableModel.__init__(self, parent)
        self._dataframe = dataframe

    def rowCount(self, parent=QModelIndex()) -> int:
        if parent == QModelIndex(): return len(self._dataframe)

    def columnCount(self, parent=QModelIndex()) -> int:
        if parent == QModelIndex(): return len(self._dataframe.columns)

    def data(self, index: QModelIndex, role=Qt.ItemDataRole):
        if not index.isValid(): return None
        if role == Qt.DisplayRole: return str(self._dataframe.iloc[index.row(), index.column()])

    def headerData(self, section: int, orientation: Qt.Orientation, role: Qt.ItemDataRole):
        if role == Qt.DisplayRole:
            if orientation == Qt.Horizontal: return str(self._dataframe.columns[section])
            if orientation == Qt.Vertical: return str(self._dataframe.index[section])


if __name__== "__main__":
    app = QApplication(sys.argv)
    options = argparse.ArgumentParser()
    options.add_argument("-f", "--file", type=str, required=False)
    args = options.parse_args()

    '''Allow GUI to be launched with data file already loaded (use cli argument --file or -f)'''
    if args.file != None:
        window = MainWindow(file=args.file)
    else:
        window = MainWindow()

    window.show()
    sys.exit(app.exec())

