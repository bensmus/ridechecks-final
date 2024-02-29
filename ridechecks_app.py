from typing import List, Dict, Tuple
import yaml
import re
from  bisect import bisect_left
from PySide6.QtCore import Signal, QSize
from PySide6.QtGui import Qt
from PySide6.QtWidgets import (
    QWidget,
    QApplication,
    QVBoxLayout,
    QHBoxLayout,
    QLineEdit,
    QLabel,
    QScrollArea,
    QPushButton,
    QComboBox,
    QWidget,
    QTabWidget,
    QTableWidget,
    QTableWidgetItem,
    QCheckBox,
    QHeaderView,
    QFrame,
)

app = QApplication([])


def get_line_edit_dict(line_edit_widgets: List[QLineEdit]) -> Dict[str, str] | None:
    """
    Returns dictionary if all line_edit_widgets are non-empty otherwise returns None.
    Dictionary has placeholder text as keys, user text as values.
    """
    line_edit_dict: Dict[str, str] = {}
    for widget in line_edit_widgets:
        placeholder_text = widget.placeholderText()
        text = widget.text()
        if text == '':
            return # User didn't finish entering text.
        line_edit_dict[placeholder_text] = text
    return line_edit_dict


class LineEditSubmitWidget(QWidget):
    submit = Signal(dict)

    def __init__(self, button_text: str, placeholder_texts: List[str]):
        super().__init__()  

        self.horiz_layout = QHBoxLayout(self)
        self.horiz_layout.setAlignment(Qt.AlignmentFlag.AlignLeft)

        for placeholder_text in placeholder_texts:
            line_edit = QLineEdit()
            line_edit.setMaximumWidth(300)
            line_edit.setPlaceholderText(placeholder_text)
            self.horiz_layout.addWidget(line_edit)
        
        button = QPushButton(button_text)
        button.setMaximumWidth(300)
        self.horiz_layout.addWidget(button)

        def handle_button_clicked():
            line_edit_widgets = self._get_line_edit_widgets()
            if line_edit_dict := get_line_edit_dict(line_edit_widgets):
                self.submit.emit(line_edit_dict)
                for widget in line_edit_widgets:
                    widget.clear()
        
        button.clicked.connect(handle_button_clicked)
    
    def _get_line_edit_widgets(self) -> List[QLineEdit]:
        line_edits: List[QLineEdit] = []
        for widget in [self.horiz_layout.itemAt(i).widget() for i in range(self.horiz_layout.count())]:
            if isinstance(widget, QLineEdit):
                line_edits.append(widget)
        return line_edits

                    
class DropdownSubmitWidget(QWidget):
    submit = Signal(str)

    def __init__(self, button_text: str, dropdown_options: List[str]):
        super().__init__()  
        
        self.dropdown = QComboBox()
        self.dropdown.setMaximumWidth(300)
        for option in dropdown_options:
            self.add_option(option)
        
        button = QPushButton(button_text)
        button.setMaximumWidth(300)

        layout = QHBoxLayout(self)
        layout.setAlignment(Qt.AlignmentFlag.AlignLeft)
        layout.addWidget(self.dropdown)
        layout.addWidget(button)

        def handle_button_clicked():
            if not self._is_empty():
                self.submit.emit(self.dropdown.currentText())
        
        button.clicked.connect(handle_button_clicked)

    def _is_empty(self) -> bool:
        return self.dropdown.currentIndex() < 0

    def _get_options(self) -> List[str]:
        return [self.dropdown.itemText(i) for i in range(self.dropdown.count())]
    
    def add_option(self, option_to_add: str):
        options = self._get_options()
        index = bisect_left(options, option_to_add)
        self.dropdown.insertItem(index, option_to_add)

    def delete_option(self, option_to_delete: str) -> None:
        """
        Deletes option if option exists.
        """
        for i, option in enumerate(self._get_options()):
            if option_to_delete == option:
                self.dropdown.removeItem(i)
                break


class DisplayValueWidget(QWidget):
    def __init__(self, label_text: str, initial_value: str):
        super().__init__()  

        description_label = QLabel(label_text)
        self.value_label = QLabel(initial_value)

        layout = QHBoxLayout(self)
        layout.setAlignment(Qt.AlignmentFlag.AlignLeft)
        layout.addWidget(description_label)
        layout.addWidget(self.value_label)
    
    def read_value(self):
        return self.value_label.text()

    def write_value(self, value: str):
        self.value_label.setText(value)


class ScrollableLinesWidget(QWidget):
    def __init__(self, lines: List[str]):
        super().__init__()
        
        layout = QVBoxLayout(self)

        label_container = QWidget()

        self.label_layout = QVBoxLayout(label_container)    
        self.label_layout.setAlignment(Qt.AlignmentFlag.AlignTop)

        scroll_area = QScrollArea(self)
        scroll_area.setWidgetResizable(True)
        scroll_area.setWidget(label_container)

        layout.addWidget(scroll_area)

        for line in lines:
            self.add_line(line)
    
    def _insert_line(self, row: int, line: str):
        label = QLabel(self)
        label.setText(line)
        self.label_layout.insertWidget(row, label)
    
    def _label_widgets(self):
        return [self.label_layout.itemAt(i).widget() for i in range(self.label_layout.count())]
    
    def add_line(self, line: str):
        """Maintains alphabetical order"""
        lines = [label.text() for label in self._label_widgets()]
        row = bisect_left(lines, line)
        self._insert_line(row, line)
    
    def delete_line(self, regex: str):
        labels = self._label_widgets()
        for label in labels:
            if re.match(regex, label.text()):
                label.deleteLater()
                break
    
    def read_lines(self) -> List[str]:
        return [label.text() for label in  self._label_widgets()]


class RideTimesWidget(ScrollableLinesWidget):
    ride_time_separator = ', '

    @staticmethod
    def _to_line(ride: str, time: int) -> str:
        return (ride + RideTimesWidget.ride_time_separator + str(time))
    
    @staticmethod
    def _from_line(line: str) -> Tuple:
        ride, time_str = line.split(RideTimesWidget.ride_time_separator)
        return ride, int(time_str)
    
    def __init__(self, ride_times: Dict[str, int]):
        lines = [RideTimesWidget._to_line(ride, time) for (ride, time) in ride_times.items()]
        super().__init__(lines)
    
    def add_ride(self, ride: str, time: int):
        self.add_line(RideTimesWidget._to_line(ride, time))
    
    def delete_ride(self, ride: str):
        self.delete_line(ride)

    def read_ride_times(self) -> Dict[str, int]:
        lines = self.read_lines()
        ride_time_tuples = [RideTimesWidget._from_line(line) for line in lines]
        return {ride: time for (ride, time) in ride_time_tuples}


class DayWidget(QWidget):
    
    #### START DAY WIDGET INIT ####

    def __init__(self, day: str, day_info: Dict, workers: List[str], rides: List[str]):
        """
        day_info has the keys: 'Time', 'Unavailable Workers', 'Unavailable Rides'
        """
        super().__init__()

        layout = QVBoxLayout(self)

        self.day = day
        day_label = QLabel(day)
        day_label.setStyleSheet("font-size: 14pt;")
        day_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        #### TIME ####

        self.time_display = DisplayValueWidget('Time till opening:', str(day_info['Time']))
        time_set = LineEditSubmitWidget('Set check duration', ['Check duration'])
        time_frame = QFrame()
        time_frame.setFrameStyle(QFrame.Box)
        time_layout = QVBoxLayout(time_frame)
        time_layout.addWidget(self.time_display)
        time_layout.addWidget(time_set)

        def handle_set_time(line_edit_dict):
            time = line_edit_dict['Check duration']
            self.time_display.write_value(time)
        
        time_set.submit.connect(handle_set_time)
        
        #### ABSENT WORKERS  ####

        unavailable_workers = day_info['Unavailable Workers']
        workers_can_set_absent = list(set(workers) - set(unavailable_workers))
        self.unavailable_workers_display = ScrollableLinesWidget(unavailable_workers)
        self.unavailable_workers_add = DropdownSubmitWidget('Set worker absent', workers_can_set_absent)
        self.unavailable_workers_remove = DropdownSubmitWidget('Set worker present', unavailable_workers)
        unavailable_workers_frame = QFrame()
        unavailable_workers_frame.setFrameStyle(QFrame.Box)
        unavailable_workers_layout = QVBoxLayout(unavailable_workers_frame)
        unavailable_workers_layout.addWidget(self.unavailable_workers_display)
        unavailable_workers_layout.addWidget(self.unavailable_workers_add)
        unavailable_workers_layout.addWidget(self.unavailable_workers_remove)

        def handle_set_absent(worker_name):
            self.unavailable_workers_display.add_line(worker_name)
            self.unavailable_workers_add.delete_option(worker_name)
            self.unavailable_workers_remove.add_option(worker_name)
        
        self.unavailable_workers_add.submit.connect(handle_set_absent)

        def handle_set_present(worker_name):
            self.unavailable_workers_display.delete_line(worker_name)
            self.unavailable_workers_remove.delete_option(worker_name)
            self.unavailable_workers_add.add_option(worker_name)
        
        self.unavailable_workers_remove.submit.connect(handle_set_present)

        #### CLOSED RIDES #### 

        unavailable_rides = day_info['Unavailable Rides']
        rides_can_set_closed = list(set(rides) - set(unavailable_rides))
        self.unavailable_rides_display = ScrollableLinesWidget(unavailable_rides)
        self.unavailable_rides_add = DropdownSubmitWidget('Set ride closed', rides_can_set_closed) 
        self.unavailable_rides_remove = DropdownSubmitWidget('Set ride open', unavailable_rides) 
        unavailable_rides_frame = QFrame()
        unavailable_rides_frame.setFrameStyle(QFrame.Box)
        unavailable_rides_layout = QVBoxLayout(unavailable_rides_frame)
        unavailable_rides_layout.addWidget(self.unavailable_rides_display)
        unavailable_rides_layout.addWidget(self.unavailable_rides_add)
        unavailable_rides_layout.addWidget(self.unavailable_rides_remove)

        def handle_set_closed(ride_name):
            self.unavailable_rides_display.add_line(ride_name)
            self.unavailable_rides_add.delete_option(ride_name)
            self.unavailable_rides_remove.add_option(ride_name)
        
        self.unavailable_rides_add.submit.connect(handle_set_closed)

        def handle_set_open(ride_name):
            self.unavailable_rides_display.delete_line(ride_name)
            self.unavailable_rides_add.add_option(ride_name)
            self.unavailable_rides_remove.delete_option(ride_name)
        
        self.unavailable_rides_remove.submit.connect(handle_set_open)

        layout.addWidget(day_label)
        layout.addWidget(time_frame)
        layout.addWidget(unavailable_workers_frame)
        layout.addWidget(unavailable_rides_frame)

    #### END DAY WIDGET INIT ####
    
    def add_ride(self, ride_name: str):
        self.unavailable_rides_add.add_option(ride_name)

    def delete_ride(self, ride_name: str):
        self.unavailable_rides_add.delete_option(ride_name)
        self.unavailable_rides_remove.delete_option(ride_name)
        self.unavailable_rides_display.delete_line(ride_name)
    
    def add_worker(self, worker_name: str):
        self.unavailable_workers_add.add_option(worker_name)
    
    def delete_worker(self, worker_name: str):
        self.unavailable_workers_add.delete_option(worker_name)
        self.unavailable_workers_remove.delete_option(worker_name)
        self.unavailable_workers_display.delete_line(worker_name)
    
    def read_day_info(self) -> Tuple[str, Dict]:
        time = int(self.time_display.read_value())
        unavailable_workers = self.unavailable_workers_display.read_lines()
        unavailable_rides = self.unavailable_rides_display.read_lines()
        return self.day, {'Time': time, 'Unavailable Workers': unavailable_workers, 'Unavailable Rides': unavailable_rides}


class WeeklyInfoWidget(QWidget):
    def __init__(self, weekly_info: Dict[str, Dict], workers: List[str], rides: List[str]):
        super().__init__()

        self.layout = QHBoxLayout(self)

        for day, day_info in weekly_info.items():
            self.layout.addWidget(DayWidget(day, day_info, workers, rides))
    
    def _get_day_widgets(self) -> List[DayWidget]:
        return [self.layout.itemAt(i).widget() for i in range(self.layout.count())]

    def add_ride(self, ride_name: str):
        for day_widget in self._get_day_widgets():
            day_widget.add_ride(ride_name)
    
    def add_worker(self, worker_name: str):
        for day_widget in self._get_day_widgets():
            day_widget.add_worker(worker_name)
    
    def delete_ride(self, ride_name: str):
        for day_widget in self._get_day_widgets():
            day_widget.delete_ride(ride_name)
    
    def delete_worker(self, worker_name: str):
        for day_widget in self._get_day_widgets():
            day_widget.delete_worker(worker_name)
    
    def read_weekly_info(self) -> Dict[str, Dict]:
        weekly_info = {}
        for day_widget in self._get_day_widgets():
            day, day_info = day_widget.read_day_info()
            weekly_info[day] = day_info
        return weekly_info


class CheckboxGridWidget(QWidget):
    def __init__(self, rows: List[str], columns: List[str]):
        super().__init__()

        self.tableWidget = QTableWidget(self)

        row_count = len(rows)
        column_count = len(columns)

        self.tableWidget.setRowCount(row_count)
        self.tableWidget.setColumnCount(column_count)

        for row, row_name in enumerate(rows):      
            self._init_row(row, row_name)

        self.tableWidget.setHorizontalHeaderLabels(columns)

        # Adjust column width to content
        self.tableWidget.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeToContents)
    
    def _get_checkbox(self, row: int, column: int) -> QWidget:
        return self.tableWidget.cellWidget(row, column)
    
    def _init_row(self, row: int, row_name: str):
        """Add vertical header and checkboxes"""
        item = QTableWidgetItem(row_name)
        self.tableWidget.setVerticalHeaderItem(row, item)
        column_count = self.tableWidget.columnCount()
        for column in range(column_count):
            checkbox = QCheckBox()
            self.tableWidget.setCellWidget(row, column, checkbox)

    def set_checkbox(self, checked: bool, row: int, column: int):
            self._get_checkbox(row, column).setChecked(checked)
    
    def read_checkbox(self, row: int, column: int):
        return self._get_checkbox(row, column).isChecked()

    def delete_row(self, row: int):
        self.tableWidget.removeRow(row)
    
    def insert_row(self, row: int, row_name: str):
        self.tableWidget.insertRow(row)
        self._init_row(row, row_name)

    def delete_column(self, column: int):
        self.tableWidget.removeColumn(column)

    def insert_column(self, column: int, column_name: str):
        self.tableWidget.insertColumn(column)
        self.tableWidget.setHorizontalHeaderItem(column, QTableWidgetItem(column_name))
        row_count = self.tableWidget.rowCount()
        for row in range(row_count):
            checkbox = QCheckBox()
            self.tableWidget.setCellWidget(row, column, checkbox)
    
    def read_row_names(self) -> List[str]:
        row_names = []
        row_count = self.tableWidget.rowCount()
        for row in range(row_count):
            item = self.tableWidget.verticalHeaderItem(row)
            row_names.append(item.text())
        return row_names

    def read_column_names(self) -> List[str]:
        column_names = []
        column_count = self.tableWidget.columnCount()
        for column in range(column_count):
            item = self.tableWidget.horizontalHeaderItem(column)
            column_names.append(item.text())
        return column_names


class WorkerPermissionGrid(CheckboxGridWidget):
    def __init__(self, worker_permissions: Dict[str, List[str]], rides: List[str]):
        workers = sorted(list(worker_permissions.keys()))
        rides = sorted(rides)

        super().__init__(workers, rides)

        # Setting grid checks based on worker_permissions.
        for i, worker in enumerate(workers):
            for j, ride in enumerate(rides):
                self.set_checkbox(ride in worker_permissions[worker], i, j)
    
    def add_worker(self, worker_name: str):
        worker_names = self.read_row_names()
        row = bisect_left(worker_names, worker_name)
        self.insert_row(row, worker_name)
    
    def add_ride(self, ride_name: str):
        ride_names = self.read_column_names()
        column = bisect_left(ride_names, ride_name)
        self.insert_column(column, ride_name)

    def delete_worker(self, worker_name: str):
        worker_names = self.read_row_names()
        row = worker_names.index(worker_name)
        self.delete_row(row)
    
    def delete_ride(self, ride_name: str):
        ride_names = self.read_column_names()
        column = ride_names.index(ride_name)
        self.delete_column(column)
    
    def read_permissions(self) -> Dict[str, List[str]]:
        ride_names = self.read_column_names()
        worker_names = self.read_row_names()
        worker_permissions: Dict[str, List[str]] = {}
        for row, worker_name in enumerate(worker_names):
            worker_permissions[worker_name] = []
            for column, ride_name in enumerate(ride_names):
                if self.read_checkbox(row, column):
                    worker_permissions[worker_name].append(ride_name)
        return worker_permissions
    
    # https://stackoverflow.com/questions/20462895/pyqt-custom-widget-disappears-when-added-with-alignment
    def sizeHint(self):
        return QSize(200, 200)


class WorkerPermissionsWidget(QWidget):
    add_worker_signal = Signal(str)
    delete_worker_signal = Signal(str)

    def __init__(self, worker_permissions: Dict[str, List[str]], rides: List[str]):
        super().__init__()

        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignmentFlag.AlignTop)

        workers = list(worker_permissions.keys())
        self.worker_permissions_grid = WorkerPermissionGrid(worker_permissions, rides)
        
        worker_add = LineEditSubmitWidget('Add worker', ['Worker name'])
        worker_delete = DropdownSubmitWidget('Delete worker', workers)

        layout.addWidget(self.worker_permissions_grid)
        layout.addWidget(worker_add)
        layout.addWidget(worker_delete)

        def handle_add_worker(line_edit_dict):
            worker_name = line_edit_dict['Worker name']
            self.add_worker_signal.emit(worker_name)
            self.worker_permissions_grid.add_worker(worker_name)
            worker_delete.add_option(worker_name)
        
        worker_add.submit.connect(handle_add_worker)

        def handle_delete_worker(worker_name):
            self.delete_worker_signal.emit(worker_name)
            self.worker_permissions_grid.delete_worker(worker_name)
            worker_delete.delete_option(worker_name)
        
        worker_delete.submit.connect(handle_delete_worker)
    
    def delete_ride(self, ride_name):
        self.worker_permissions_grid.delete_ride(ride_name)
            
    def add_ride(self, ride_name):
        self.worker_permissions_grid.add_ride(ride_name)
    
    def read_permissions(self) -> Dict[str, List[str]]:
        return self.worker_permissions_grid.read_permissions()


class RidesWidget(QWidget):
    ride_add_signal = Signal(str)
    ride_delete_signal = Signal(str)

    def __init__(self, ride_times: Dict[str, int]):
        super().__init__()

        ride_times = dict(sorted(ride_times.items(), key=lambda x: x[0])) # Sort list of tuples based on first element, then dict it.
        layout = QVBoxLayout(self)
        
        rides = list(ride_times.keys())
        self.rides_display = RideTimesWidget(ride_times)
        ride_add = LineEditSubmitWidget('Add ride', ['Ride name', 'Ride check duration'])
        ride_delete = DropdownSubmitWidget('Delete ride', rides)

        layout.addWidget(self.rides_display)
        layout.addWidget(ride_add)
        layout.addWidget(ride_delete)

        def handle_add_ride(line_edit_dict):
            ride = line_edit_dict['Ride name']
            time = line_edit_dict['Ride check duration']
            self.rides_display.add_ride(ride, time)
            ride_delete.add_option(ride)
            self.ride_add_signal.emit(ride)
        
        ride_add.submit.connect(handle_add_ride)

        def handle_delete_ride(ride):
            self.rides_display.delete_ride(ride)
            ride_delete.delete_option(ride)
            self.ride_delete_signal.emit(ride)
        
        ride_delete.submit.connect(handle_delete_ride)
    
    def read_ride_times(self) -> Dict[str, int]:
        return self.rides_display.read_ride_times()


class MainWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('Ridechecks App')
        self.setGeometry(0, 0, 1000, 800)

        tab_widget = QTabWidget()

        with open('state.yaml') as f:
            yaml_data = yaml.safe_load(f)
        
        print(yaml_data)

        ride_times: Dict[str, int] = yaml_data['Ride Times']
        worker_permissions: Dict[str, List[str]] = yaml_data['Worker Permissions']
        rides = list(ride_times.keys())
        workers = list(worker_permissions.keys())

        weekly_info_widget = WeeklyInfoWidget(yaml_data['Weekly Info'], workers, rides)
        worker_permissions_widget = WorkerPermissionsWidget(worker_permissions, ride_times)
        rides_widget = RidesWidget(ride_times)

        rides_widget.ride_add_signal.connect(worker_permissions_widget.add_ride)
        rides_widget.ride_delete_signal.connect(worker_permissions_widget.delete_ride)

        rides_widget.ride_add_signal.connect(weekly_info_widget.add_ride)
        worker_permissions_widget.add_worker_signal.connect(weekly_info_widget.add_worker)
        rides_widget.ride_delete_signal.connect(weekly_info_widget.delete_ride)
        worker_permissions_widget.delete_worker_signal.connect(weekly_info_widget.delete_worker)

        tab_widget.addTab(weekly_info_widget, 'Weekly Info')
        tab_widget.addTab(worker_permissions_widget, 'Worker Permissions')
        tab_widget.addTab(rides_widget, 'Rides')

        save_button = QPushButton(self)
        save_button.setText('Save')

        layout = QVBoxLayout(self)
        layout.addWidget(tab_widget)
        layout.addWidget(save_button)

        def save_state():
            weekly_info = weekly_info_widget.read_weekly_info()
            worker_permissions = worker_permissions_widget.read_permissions()
            ride_times = rides_widget.read_ride_times()
            yaml_data = {'Weekly Info': weekly_info, 'Worker Permissions': worker_permissions, 'Ride Times': ride_times}
            with open('state.yaml', 'w') as f:
                yaml.safe_dump(yaml_data, f, sort_keys=False)
        
        save_button.clicked.connect(save_state)
        save_button.setMaximumWidth(300)
        save_button.setStyleSheet("background-color: lightblue;")


window = MainWindow()
window.show()
app.exec()