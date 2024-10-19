import sys

from PyQt6.QtWidgets import QApplication, QWidget, QMainWindow, QVBoxLayout, QListWidgetItem
from PyQt6.uic import loadUi
from PyQt6 import QtCore

import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg, NavigationToolbar2QT
from matplotlib.figure import Figure
import matplotlib.dates as mdates

import pandas as pd
import numpy as np

RESULT_CSV_DIR = ''

class MainUI(QMainWindow):
    # Loads ui on creation
    def __init__(self):
        super(MainUI, self).__init__()
        loadUi("Client.ui", self)
        
        for client_id in self.get_client_ids():
            item = QListWidgetItem(str(client_id))
            item.setFlags(item.flags() | QtCore.Qt.ItemFlag.ItemIsUserCheckable)
            item.setCheckState(QtCore.Qt.CheckState.Checked)
            self.listWidget.addItem(item)
        
        # Use lambda to prevent immediate execution and error
        self.tempButton.clicked.connect(lambda: self.plotCanvas.update_plot("Temp", self.get_checked()))
        self.humidityButton.clicked.connect(lambda: self.plotCanvas.update_plot("Humidity", self.get_checked()))
        
        # Set up the plots with toolbars, default will be temp
        self.plotCanvas = Canvas(self.plotCanvas, "Temp", self.get_checked())
        self.plotToolbar = NavigationToolbar2QT(self.plotCanvas, self.plotToolbar)
        
        
        
    def get_client_ids(self):
        data = pd.read_csv(RESULT_CSV_DIR)
        client_id_list = data["ID"].unique()
        return sorted(client_id_list)
    
    def get_checked(self):
        item_list = []
        for i in range(self.listWidget.count()):
            item = self.listWidget.item(i)
            if item.checkState() == QtCore.Qt.CheckState.Checked:
                item_list += item.text()
        return item_list
        

class Canvas(FigureCanvasQTAgg):
    def __init__(self, parent, data_type, checked_items):
        # Load the data from the CSV file
        self.data = pd.read_csv(RESULT_CSV_DIR)
        
        # Create a figure and axis
        self.fig, self.ax = plt.subplots(figsize=(11.2, 5.7291666667))
        
        # Initialize the parent class with the figure
        super().__init__(self.fig)
        self.setParent(parent)
        
        # Plot chart
        self.plot(data_type, checked_items)
        
    
    def plot(self, data_type, checked_items):
        # Clear chart
        self.ax.clear()
        
        # Group data by ID of sensor
        self.grouped_ids = self.data.groupby('ID')
        
        self.allowed_ids = checked_items
        
        # Plot data for each ID
        for client_id, group in self.grouped_ids:
                
            if str(client_id) in self.allowed_ids:
                
                # Get data for each ID group
                self.ax.index = group['Time']
                y = group[data_type]
                
                # Plot data for each ID
                self.ax.plot(y, label=f"ID {client_id}", marker='o')
            
        
        # Customize the plot
        self.ax.set(xlabel='Time', ylabel=data_type, title=f"{data_type} Over Time")
        self.ax.grid()
        
        plt.tight_layout()
        plt.subplots_adjust(bottom=0.2)
        plt.xticks(rotation=90)
        plt.legend()
        plt.draw()
    
    def update_plot(self, data_type, check_items):
        self.data = pd.read_csv(RESULT_CSV_DIR)
        self.plot(data_type, check_items)
        
        
    
app = QApplication(sys.argv)        
ui = MainUI()
ui.show()
app.exec()