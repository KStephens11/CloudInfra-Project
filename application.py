import sys

from PyQt6.QtWidgets import QApplication, QWidget, QMainWindow, QVBoxLayout
from PyQt6.uic import loadUi

import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg, NavigationToolbar2QT
from matplotlib.figure import Figure
import matplotlib.dates as mdates

import pandas as pd
import numpy as np

RESULT_CSV_DIR = 'DIRECTORY HERE'

class MainUI(QMainWindow):
    # Loads ui on creation
    def __init__(self):
        super(MainUI, self).__init__()
        loadUi("Client.ui", self)
        
        # Use lambda to prevent immediate execution and error
        self.tempButton.clicked.connect(lambda: self.plotCanvas.update_plot("Temp"))
        self.humidityButton.clicked.connect(lambda: self.plotCanvas.update_plot("Humidity"))
        
        # Set up the plots with toolbars, default will be temp
        self.plotCanvas = Canvas(self.plotCanvas, "Temp")
        self.plotToolbar = NavigationToolbar2QT(self.plotCanvas, self.plotToolbar)
        

class Canvas(FigureCanvasQTAgg):
    def __init__(self, parent, data_type):
        # Load the data from the CSV file
        self.data = pd.read_csv(RESULT_CSV_DIR)
        
        # Create a figure and axis
        self.fig, self.ax = plt.subplots(figsize=(11.2, 5.7291666667))
        
        # Initialize the parent class with the figure
        super().__init__(self.fig)
        self.setParent(parent)
        
        # Plot chart
        self.plot(data_type)
        
    
    def plot(self, data_type):
        # Clear chart
        self.ax.clear()
        
        # Group data by ID of sensor
        self.grouped_ids = self.data.groupby('ID')
        
        # Plot data for each ID
        for client_id, group in self.grouped_ids:
            
            # Get data for each ID group
            x = group['Time']
            y = group[data_type]
            
            # Plot data for each ID
            self.ax.plot(x, y, label=f"ID {client_id}", marker='o')
            
        
        # Customize the plot
        self.ax.set(xlabel='Time', ylabel=data_type, title=f"{data_type} Over Time")
        self.ax.grid()
        
        plt.tight_layout()
        plt.subplots_adjust(bottom=0.2)
        plt.xticks(rotation=90)
        plt.legend()
        plt.draw()
    
    def update_plot(self, data_type):
        self.data = pd.read_csv(RESULT_CSV_DIR)
        self.plot(data_type)
        
        
    
app = QApplication(sys.argv)        
ui = MainUI()
ui.show()
app.exec()