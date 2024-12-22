from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                           QHBoxLayout, QLabel, QLineEdit, QPushButton, QMessageBox)
from PyQt6.QtCore import QDate
import pandas as pd
import os
import sys
import matplotlib
matplotlib.use('Qt5Agg')
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from datetime import datetime


class HealthTracker(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Health Metrics Tracker")
        self.setGeometry(100, 100, 800, 600)

        # Initialize data storage
        self.data_file = "health_metrics.csv"
        self.load_data()

        # Create main widget and layout
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        layout = QVBoxLayout(main_widget)

        # Input controls
        input_widget = QWidget()
        input_layout = QHBoxLayout(input_widget)

        # Metric input
        input_layout.addWidget(QLabel("Metric:"))
        self.metric_entry = QLineEdit("Weight")
        input_layout.addWidget(self.metric_entry)

        # Value input
        input_layout.addWidget(QLabel("Value:"))
        self.value_entry = QLineEdit()
        input_layout.addWidget(self.value_entry)

        # Date input
        input_layout.addWidget(QLabel("Date (YYYY-MM-DD):"))
        self.date_entry = QLineEdit(datetime.now().strftime("%Y-%m-%d"))
        input_layout.addWidget(self.date_entry)

        # Add button
        add_button = QPushButton("Add Entry")
        add_button.clicked.connect(self.add_entry)
        input_layout.addWidget(add_button)

        layout.addWidget(input_widget)

        # Graph widget
        self.figure, self.ax = plt.subplots(figsize=(10, 6))
        self.canvas = FigureCanvas(self.figure)
        layout.addWidget(self.canvas)

        self.update_graph()

    def load_data(self):
        if os.path.exists(self.data_file):
            self.df = pd.read_csv(self.data_file)
        else:
            self.df = pd.DataFrame(columns=["Date", "Metric", "Value"])

    def save_data(self):
        self.df.to_csv(self.data_file, index=False)

    def add_entry(self):
        try:
            date = pd.to_datetime(self.date_entry.text())
            metric = self.metric_entry.text()
            value = float(self.value_entry.text())

            new_entry = pd.DataFrame(
                {"Date": [date], "Metric": [metric], "Value": [value]}
            )

            self.df = pd.concat([self.df, new_entry], ignore_index=True)
            self.save_data()
            self.update_graph()

            # Clear input fields
            self.value_entry.clear()
            self.date_entry.setText(datetime.now().strftime("%Y-%m-%d"))

            QMessageBox.information(self, "Success", "Entry added successfully!")

        except ValueError as e:
            QMessageBox.critical(self, "Error", "Please check your input values!")

    def update_graph(self):
        self.ax.clear()

        # Filter data for current metric
        metric_data = self.df[self.df["Metric"] == self.metric_entry.text()]

        if not metric_data.empty:
            metric_data = metric_data.sort_values("Date")
            self.ax.plot(
                pd.to_datetime(metric_data["Date"]), metric_data["Value"], marker="o"
            )
            self.ax.set_xlabel("Date")
            self.ax.set_ylabel(self.metric_entry.text())
            self.ax.set_title(f"{self.metric_entry.text()} Over Time")
            plt.xticks(rotation=45)
            plt.tight_layout()

        self.canvas.draw()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = HealthTracker()
    window.show()
    sys.exit(app.exec())
