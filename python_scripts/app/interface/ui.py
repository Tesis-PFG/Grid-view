import vtk
import numpy as np
import SimpleITK as sitk

from mat_3d import *
from PyQt5.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget, QPushButton, QFileDialog
from vtk.qt.QVTKRenderWindowInteractor import QVTKRenderWindowInteractor


class MPRInterface(QMainWindow):
    def __init__(self):
        super().__init__()
        self.planeWidgetArray = [None]*3
        self.presliceCursorWidgetArray = [None]*3

        self.setWindowTitle("MPR Interface")
        self.setGeometry(20, 20, 20, 20)

        self.setupUI()

    def setupUI(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)

        self.vtk_widget = QVTKRenderWindowInteractor(central_widget)
        layout.addWidget(self.vtk_widget)

        self.renderer = vtk.vtkRenderer()
        self.vtk_widget.GetRenderWindow().AddRenderer(self.renderer)
        self.interactor = self.vtk_widget.GetRenderWindow().GetInteractor()

        load_button = QPushButton("Load Scans", central_widget)
        load_button.clicked.connect(self.loadScans)
        layout.addWidget(load_button)
        # layout.addWidget(load_button, 2, 0, 1, 2)

    def read_nifti(self):

        #Reading dicom
        myFile = './Data/nifti/patient/fused.nii'
        reader = vtk.vtkNIFTIImageReader()
        reader.SetFileName(myFile)
        reader.Update()
        myDicom = reader.GetOutput()
        # Crear un filtro para invertir los ejes X, Y y Z
        flip = vtk.vtkImageFlip()
        flip.SetInputData(myDicom)
        # flip.SetFilteredAxis(0)  # Invertir el eje X
        flip.SetFilteredAxis(1)  # Invertir el eje Y
        flip.SetFilteredAxis(2)  # Invertir el eje Z
        flip.Update()

        writer = vtk.vtkNIFTIImageWriter()
        writer.SetFileName(myFile)
        writer.SetInputData(flip.GetOutput())
        writer.Write()

        reader = vtk.vtkNIFTIImageReader()
        reader.SetFileName(myFile)
        reader.Update()
        myDicom = reader.GetOutput()

        imageDims = myDicom.GetDimensions()

        # Visualizar la imagen invertida
        outline = vtk.vtkOutlineFilter()
        outline.SetInputData(flip.GetOutput())

        # // Bounding box
        outline = vtk.vtkOutlineFilter()
        outline.SetInputConnection(reader.GetOutputPort())

        outlineMapper = vtk.vtkPolyDataMapper()
        outlineMapper.SetInputConnection(outline.GetOutputPort())

        outlineActor = vtk.vtkActor()
        outlineActor.SetMapper(outlineMapper)
        outlineActor.GetProperty().SetColor(1,1,0)

        # // Mapper and actors for volume
        volumeMapper = vtk.vtkPolyDataMapper()
        volumeMapper.SetInputConnection(reader.GetOutputPort())

        volumeActor = vtk.vtkActor()
        volumeActor.SetMapper(volumeMapper)

        # // Renderers
        renWin = vtk.vtkRenderWindow()
        RendererArray = [None]*4
        for i in range(0,4):
            RendererArray[i] = vtk.vtkRenderer()
            renWin.AddRenderer(RendererArray[i])
        renWin.SetMultiSamples(0)

        # // Render window interactor
        iren = vtk.vtkRenderWindowInteractor()
        renWin.SetInteractor(iren)

        # // Picker
        picker = vtk.vtkCellPicker()
        picker.SetTolerance(0.005)

        # // Properties
        ipwProp = vtk.vtkProperty()

        # // 3D plane widgets
        
        for i in range(0,3):
            self.planeWidgetArray[i] = vtk.vtkImagePlaneWidget()
            self.planeWidgetArray[i].SetInteractor(iren)
            self.planeWidgetArray[i].SetPicker(picker)
            self.planeWidgetArray[i].RestrictPlaneToVolumeOn()
            color = [0, 0, 0 ]
            color[i] = 1
            self.planeWidgetArray[i].GetPlaneProperty().SetColor(color)
            self.planeWidgetArray[i].SetTexturePlaneProperty(ipwProp)
            self.planeWidgetArray[i].TextureInterpolateOff()
            self.planeWidgetArray[i].SetResliceInterpolateToLinear()
            self.planeWidgetArray[i].SetInputConnection(reader.GetOutputPort())
            self.planeWidgetArray[i].SetPlaneOrientation(i)
            self.planeWidgetArray[i].SetSliceIndex(int(imageDims[i] / 2))
            self.planeWidgetArray[i].DisplayTextOn()
            self.planeWidgetArray[i].SetDefaultRenderer(RendererArray[3])
            self.planeWidgetArray[i].SetWindowLevel(1358, -27, 0)
            self.planeWidgetArray[i].On()
            self.planeWidgetArray[i].InteractionOff()

        self.planeWidgetArray[1].SetLookupTable(self.planeWidgetArray[0].GetLookupTable()) 
        self.planeWidgetArray[2].SetLookupTable(self.planeWidgetArray[0].GetLookupTable())

        # // ResliceCursor
        resliceCursor = vtk.vtkResliceCursor()
        center = reader.GetOutput().GetCenter()
        resliceCursor.SetCenter(center[0], center[1], center[2])
        resliceCursor.SetThickMode(0)
        resliceCursor.SetThickness(10, 10, 10)
        resliceCursor.SetHole(0)
        resliceCursor.SetImage(reader.GetOutput())

        # // 2D Reslice cursor widgets
        resliceCursorRepArray = [None]*3
        self.presliceCursorWidgetArray = [None]*3
        viewUp = [[0, 0, 1],[0, 0,-1],[0, 1, 0]]


        for i in range(0, 3):
            self.presliceCursorWidgetArray[i] = vtk.vtkResliceCursorWidget()
            resliceCursorRepArray[i] = vtk.vtkResliceCursorLineRepresentation()
            self.presliceCursorWidgetArray[i].SetInteractor(iren)
            self.presliceCursorWidgetArray[i].SetRepresentation(resliceCursorRepArray[i])
            resliceCursorRepArray[i].GetResliceCursorActor().GetCursorAlgorithm().SetResliceCursor(resliceCursor)
            resliceCursorRepArray[i].GetResliceCursorActor().GetCursorAlgorithm().SetReslicePlaneNormal(i)
            minVal = reader.GetOutput().GetScalarRange()[0]
            reslice = resliceCursorRepArray[i].GetReslice()
            reslice.SetInputConnection(reader.GetOutputPort())
            reslice.SetBackgroundColor(minVal, minVal, minVal, minVal)
            reslice.AutoCropOutputOn()
            reslice.Update()
            self.presliceCursorWidgetArray[i].SetDefaultRenderer(RendererArray[i])
            self.presliceCursorWidgetArray[i].SetEnabled(1)
            RendererArray[i].GetActiveCamera().SetFocalPoint(0, 0, 0)
            camPos = [0, 0, 0]
            camPos[i] = 1
            RendererArray[i].GetActiveCamera().SetPosition(camPos[0], camPos[1], camPos[2])
            RendererArray[i].GetActiveCamera().ParallelProjectionOn()
            RendererArray[i].GetActiveCamera().SetViewUp(viewUp[i][0], viewUp[i][1], viewUp[i][2])
            RendererArray[i].ResetCamera()
            self.presliceCursorWidgetArray[i].AddObserver('InteractionEvent', self.resliceCursorCallback)
            range_color = reader.GetOutput().GetScalarRange()
            resliceCursorRepArray[i].SetWindowLevel(range_color[1] - range_color[0], (range_color[0] + range_color[1]) / 2.0, 0)
            resliceCursorRepArray[i].SetWindowLevel(range_color[1] - range_color[0], (range_color[0] + range_color[1]) / 2.0, 0)
            resliceCursorRepArray[i].SetLookupTable(resliceCursorRepArray[0].GetLookupTable())
            self.planeWidgetArray[i].GetColorMap().SetLookupTable(resliceCursorRepArray[0].GetLookupTable())
            
        # // Background
        RendererArray[0].SetBackground(0.3, 0.1, 0.1)
        RendererArray[1].SetBackground(0.1, 0.3, 0.1)
        RendererArray[2].SetBackground(0.1, 0.1, 0.3)
        RendererArray[3].AddActor(volumeActor)
        RendererArray[3].AddActor(outlineActor)
        RendererArray[3].SetBackground(0.1, 0.1, 0.1)
        renWin.SetSize(900, 900)

        # // Render
        RendererArray[2].SetViewport(0, 0, 0.5, 0.5)
        RendererArray[3].SetViewport(0.5, 0, 1, 0.5)
        RendererArray[1].SetViewport(0, 0.5, 0.5, 1)
        RendererArray[0].SetViewport(0.5, 0.5, 1, 1)
        renWin.Render()

        # // Camera in 3D view
        RendererArray[3].GetActiveCamera().Elevation(110)
        RendererArray[3].GetActiveCamera().SetViewUp(0, 0, 1)
        RendererArray[3].GetActiveCamera().Azimuth(45)
        RendererArray[3].GetActiveCamera().Dolly(1.15)
        RendererArray[3].ResetCameraClippingRange()

        iren.Initialize()
        iren.Start()
        

    # Reslice cursor callback    
    def resliceCursorCallback(self,obj,event):
        for i in range(0,3):
            
            ps = self.planeWidgetArray[i].GetPolyDataAlgorithm()
            origin = self.presliceCursorWidgetArray[i].GetResliceCursorRepresentation().GetPlaneSource().GetOrigin()
            ps.SetOrigin(origin)
            point1 = self.presliceCursorWidgetArray[i].GetResliceCursorRepresentation().GetPlaneSource().GetPoint1()
            ps.SetPoint1(point1)
            point2 = self.presliceCursorWidgetArray[i].GetResliceCursorRepresentation().GetPlaneSource().GetPoint2()
            ps.SetPoint2(point2)
            self.planeWidgetArray[i].UpdatePlacement()
    
    def loadScans(self):
        file_dialog = QFileDialog()
        file_paths = file_dialog.getExistingDirectory(self, "Select Folder")
        file_paths_2 = file_dialog.getExistingDirectory(self, "Select Folder 2")

        registro(file_paths, file_paths_2)
        self.read_nifti()

if __name__ == "__main__":
    app = QApplication([])
    window = MPRInterface()
    window.show()
    app.exec_()
