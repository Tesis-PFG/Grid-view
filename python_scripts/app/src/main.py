import sys
import vtk

from PyQt5.QtWidgets import QApplication, QMainWindow, QMdiArea, QMdiSubWindow, \
    QLabel, QGridLayout, QScrollBar
from PyQt5 import QtGui, QtWidgets, QtCore
from PyQt5 import Qt
from vtk.qt.QVTKRenderWindowInteractor import QVTKRenderWindowInteractor

class AppWindow(QMainWindow):
    count = 0

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Viewer - Test")

        self.mdi = QMdiArea()
        self.grid_d = QGridLayout()
        self.grid_d.setSpacing(5)

        self.rm = './Data/David Mayorga/Mayorga_Herrera_David_Ricardo/Resonancia_Nuclear_Magnetica_De_Cerebro_Cte_Prot_Dr_Buitrago - RPID001/T1_3D_TFE_AXI_501'
        self.ct = './Data/David Mayorga/Tac_De_Craneo_Simple - 879111/_Head_10_3'

        self.setCentralWidget(self.mdi)
        self.resize(1200, 800)
        self.menu_bar()
        self.show()


    def menu_bar(self):
        bar = self.menuBar()
        file = bar.addMenu('File')
        file_new = self.create_action('New', './icons/plus_icon.png', 'Ctrl+N', self.file_open_thr)
        file_exit = self.create_action('Exit', './icons/close-button1.png', 'Ctrl+Q', self.close)
        self.add_action(file, (file_new, file_exit))

    def create_action(self, text, icon=None, shortcut=None, implement=None, signal='triggered'):
        action = QtWidgets.QAction(text, self)
        if icon is not None:
            action.setIcon(QtGui.QIcon(icon))
        if shortcut is not None:
            action.setShortcut(shortcut)
        if implement is not None:
            getattr(action, signal).connect(implement)
        return action

    def file_open_thr(self):
        AppWindow.count = AppWindow.count + 1
        self.filename = QtWidgets.QFileDialog.getExistingDirectory(self, 'Select Folder')

        if self.filename:
            self.vtk(self.filename)

    def vtk(self, filename):
        filename = self.rm 

        self.sub = QMdiSubWindow()
        self.frame = Qt.QFrame()

        self.add_dataset(filename)
        self.vtkWidget = QVTKRenderWindowInteractor(self.frame)
        self.sub.setWidget(self.vtkWidget)
        self.ren = vtk.vtkRenderer()
        self.ren.SetBackground(0.2, 0.2, 0.2)
        self.vtkWidget.GetRenderWindow().AddRenderer(self.ren)
        self.iren = self.vtkWidget.GetRenderWindow().GetInteractor()

        # Set Titlebar
        self.sub.setWindowTitle("Dataset " + str(AppWindow.count))

        self.imageData = vtk.vtkImageData()
        self.reader = vtk.vtkDICOMImageReader()
        self.color = vtk.vtkColorTransferFunction()
        self.reader.SetDirectoryName(filename)
        self.reader.SetDataScalarTypeToUnsignedShort()
        self.reader.UpdateWholeExtent()
        self.reader.Update()
        self.imageData.ShallowCopy(self.reader.GetOutput())

        #Create Sagittal Slice Matrix
        sagittal = vtk.vtkMatrix4x4()
        sagittal.DeepCopy((0, 0, -1, 80,
                       1, 0, 0, 80,
                       0, -1, 0, 80,
                       0, 0, 0, 1))

        # Reslice image
        slice = vtk.vtkImageReslice()
        slice.SetInputConnection(self.reader.GetOutputPort())
        slice.SetOutputDimensionality(2)
        slice.SetResliceAxes(sagittal)
        slice.SetInterpolationModeToLinear()

        # Display the image
        actor = vtk.vtkImageActor()
        actor.GetMapper().SetInputConnection(slice.GetOutputPort())

        renderer = vtk.vtkRenderer()

        # Remove Renderer And Reset
        renderer.RemoveAllViewProps()
        renderer.ResetCamera()
        self.vtkWidget.GetRenderWindow().Render()
        renderer.AddActor(actor)
        self.vtkWidget.GetRenderWindow().AddRenderer(renderer)

        # Set up the interaction
        slice_interactorStyle = vtk.vtkInteractorStyleImage()
        slice_interactor = self.vtkWidget.GetRenderWindow().GetInteractor()
        slice_interactor.SetInteractorStyle(slice_interactorStyle)
        self.vtkWidget.GetRenderWindow().SetInteractor(slice_interactor)
        self.vtkWidget.GetRenderWindow().Render()
        self.ren.ResetCamera()
        self.mdi.addSubWindow(self.sub)
        self.sub.show()
        self.iren.Initialize()
        self.iren.Start()
         # ---------------------------------------------------------------
        # Create a scrollbar for controlling slice position
        scrollbar = QScrollBar()
        scrollbar.setMinimum(0)
        scrollbar.setMaximum(self.reader.GetOutput().GetDimensions()[0] - 1)
        scrollbar.setValue(0)
        scrollbar.setGeometry(0, 0, 30, 500) 
        scrollbar.valueChanged.connect(self.update_slice)

        # Add the scrollbar to the layout
        self.grid_d.addWidget(scrollbar, AppWindow.count, 2)
        # ---------------------------------------------------------------

    # ---------------------------------------------------------------
    def update_slice(self, value):
        sagittal = vtk.vtkMatrix4x4()
        sagittal.DeepCopy((0, 0, -1, 80 + value,
                           1, 0, 0, 80,
                           0, -1, 0, 80,
                           0, 0, 0, 1))

        slice.SetResliceAxes(sagittal)
        self.vtkWidget.GetRenderWindow().Render()
    # ---------------------------------------------------------------

    def add_dataset(self, filename):
        file_loc = QLabel('File Location ' + str(AppWindow.count) + ': ')
        location = QLabel(filename)

        self.grid_d.addWidget(file_loc, AppWindow.count, 0)
        self.grid_d.addWidget(location, AppWindow.count, 1)

        return self.grid_d
    
    def add_action(self, dest, actions):
        for action in actions:
            if action is None:
                dest.addSeperator()
            else:
                dest.addAction(action)

if __name__ == '__main__':

    app = QApplication(sys.argv)
    app_win = AppWindow()
    # app_win.vtk('Data/David Mayorga/Mayorga_Herrera_David_Ricardo/Resonancia_Nuclear_Magnetica_De_Cerebro_Cte_Prot_Dr_Buitrago - RPID001/T1_3D_TFE_AXI_501')
    sys.exit(app.exec())