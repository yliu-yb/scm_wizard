from PyQt5 import QtWidgets
from matplotlib.figure import Figure
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as Canvas
import matplotlib
import matplotlib.pylab as pylab
# Ensure using PyQt5 backend
matplotlib.use('QT5Agg')

# Matplotlib canvas class to create figure
SMALL_SIZE = 16
MEDIUM_SIZE = 16
BIGGER_SIZE = 16
class MplCanvas(Canvas):
    def __init__(self):
        self.fig = Figure()
        
        params = {  'figure.titlesize': BIGGER_SIZE,
                    'legend.fontsize': MEDIUM_SIZE,
                    'axes.labelsize':  SMALL_SIZE,
                    'axes.titlesize':  MEDIUM_SIZE,
                    'xtick.labelsize': SMALL_SIZE,
                    'ytick.labelsize': SMALL_SIZE}
        pylab.rcParams.update(params)
        Canvas.__init__(self, self.fig)
        Canvas.setSizePolicy(self, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
        Canvas.updateGeometry(self)

class MplWidget(QtWidgets.QWidget):
    def __init__(self, parent=None):
        QtWidgets.QWidget.__init__(self, parent)   # Inherit from QWidget
        self.canvas = MplCanvas()                  # Create canvas object
        self.vbl = QtWidgets.QVBoxLayout()         # Set box for plotting
        self.vbl.addWidget(self.canvas)
        self.setLayout(self.vbl)