import os
import sys
import numpy as np

from mat_3d import *
from PyQt5.QtWidgets import *
from PyQt5.uic import loadUi
from vtk.qt.QVTKRenderWindowInteractor import QVTKRenderWindowInteractor

class MPRInterface(QDialog):
    def __init__(self):
        super().__init__()
        path = os.getcwd()
        self.directory = os.getcwd()
        loadUi('./app/interface/mainwindow.ui', self)
        self.setWindowTitle('MPR Interface')
        self.image = None
        self.voxel = None

        self.v1, self.v2, self.v3 , self.v4 = None, None, None, None
        self.volWindow = None
        self.dicomButton.clicked.connect(self.dicom_clicked)
        self.axial_hSlider.valueChanged.connect(self.updateimg)
        self.axial_vSlider.valueChanged.connect(self.updateimg)
        self.sagittal_hSlider.valueChanged.connect(self.updateimg)
        self.sagittal_vSlider.valueChanged.connect(self.updateimg)
        self.coronal_hSlider.valueChanged.connect(self.updateimg)
        self.coronal_vSlider.valueChanged.connect(self.updateimg)
        self.w, self.h = self.imgLabel_1.width(), self.imgLabel_1.height()

        self.axialGrid.setSpacing(0)
        self.saggitalGrid.setSpacing(0)
        self.coronalGrid.setSpacing(0)

        h = QSpacerItem(10, 10, QSizePolicy.Fixed, QSizePolicy.Fixed)
        v = QSpacerItem(10, 10, QSizePolicy.Fixed, QSizePolicy.Fixed)

        self.axial_vBox.setSpacing(0)
        self.axial_vBox.insertSpacerItem(0, v)
        self.axial_vBox.insertSpacerItem(2, v)
        self.axial_hBox.setSpacing(0)
        self.axial_hBox.insertSpacerItem(0, h)
        self.axial_hBox.insertSpacerItem(2, h)
        self.saggital_vBox.setSpacing(0)
        self.saggital_vBox.insertSpacerItem(0, v)
        self.saggital_vBox.insertSpacerItem(2, v)
        self.saggital_hBox.setSpacing(0)
        self.saggital_hBox.insertSpacerItem(0, h)
        self.saggital_hBox.insertSpacerItem(2, h)
        self.coronal_vBox.setSpacing(0)
        self.coronal_vBox.insertSpacerItem(0, v)
        self.coronal_vBox.insertSpacerItem(2, v)
        self.coronal_hBox.setSpacing(0)
        self.coronal_hBox.insertSpacerItem(0, h)
        self.coronal_hBox.insertSpacerItem(2, h)


        self.dcmInfo = None
        self.imgLabel_1.mpsignal.connect(self.cross_center_mouse)
        self.imgLabel_2.mpsignal.connect(self.cross_center_mouse)
        self.imgLabel_3.mpsignal.connect(self.cross_center_mouse)

    def set_directory(self):
        os.chdir(self.directory)

    def cross_center_mouse(self, _type):
        self.cross_recalc = False
        if _type == 'axial':
            self.axial_hSlider.setValue(self.imgLabel_1.crosscenter[0] *
                                        self.axial_hSlider.maximum() / self.imgLabel_1.width())
            self.axial_vSlider.setValue(self.imgLabel_1.crosscenter[1] *
                                        self.axial_vSlider.maximum() / self.imgLabel_1.height())
        elif _type == 'sagittal':
            self.sagittal_hSlider.setValue(self.imgLabel_2.crosscenter[0] *
                                           self.sagittal_hSlider.maximum() / self.imgLabel_2.width())
            self.sagittal_vSlider.setValue(self.imgLabel_2.crosscenter[1] *
                                           self.sagittal_vSlider.maximum() / self.imgLabel_2.height())
        elif _type == 'coronal':
            self.coronal_hSlider.setValue(self.imgLabel_3.crosscenter[0] *
                                          self.coronal_hSlider.maximum() / self.imgLabel_3.width())
            self.coronal_vSlider.setValue(self.imgLabel_3.crosscenter[1] *
                                          self.coronal_vSlider.maximum() / self.imgLabel_3.height())
        else:
            pass

        self.imgLabel_1.crosscenter = [
            self.axial_hSlider.value() * self.imgLabel_1.width() / self.axial_hSlider.maximum(),
            self.axial_vSlider.value() * self.imgLabel_1.height() / self.axial_vSlider.maximum()]
        self.imgLabel_2.crosscenter = [
            self.sagittal_hSlider.value() * self.imgLabel_2.width() / self.sagittal_hSlider.maximum(),
            self.sagittal_vSlider.value() * self.imgLabel_2.height() / self.sagittal_vSlider.maximum()]
        self.imgLabel_3.crosscenter = [
            self.coronal_hSlider.value() * self.imgLabel_3.width() / self.coronal_hSlider.maximum(),
            self.coronal_vSlider.value() * self.imgLabel_3.height() / self.coronal_vSlider.maximum()]
        self.updateimg()

        self.cross_recalc = True

    def dicom_clicked(self):
        self.load_dicomfile()

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
        iren = QVTKRenderWindowInteractor(self.imgLabel_4)
        renWin.SetInteractor(iren)

        # // Picker
        # picker = vtk.vtkCellPicker()
        # picker.SetTolerance(0.005)

        # # // Properties
        # ipwProp = vtk.vtkProperty()
        RendererArray[3].AddActor(volumeActor)
        iren.Initialize()
        iren.Start()






    def load_dicomfile(self):
        file_dialog = QFileDialog()
        file_paths = file_dialog.getExistingDirectory(self, "Select Folder")
        file_paths_2 = file_dialog.getExistingDirectory(self, "Select Folder 2")

        registro(file_paths, file_paths_2)
        self.read_nifti()

        


        # self.voxel = self.linear_convert(None)
        # self.processedvoxel = self.voxel.copy()

        # self.update_shape()

        # self.imgLabel_1.setMouseTracking(True)
        # self.imgLabel_2.setMouseTracking(True)
        # self.imgLabel_3.setMouseTracking(True)

        # self.updateimg()
        # self.set_directory()
        # self.volWindow.imgs = None
        # self.volWindow.patient = None
        # self.updatelist()

    def update_shape(self):
        # self.v1, self.v2, self.v3 = self.processedvoxel.shape
        # self.sagittal_vSlider.setMaximum(self.v1-1)
        # self.coronal_vSlider.setMaximum(self.v1-1)
        # self.sagittal_hSlider.setMaximum(self.v2-1)
        # self.axial_vSlider.setMaximum(self.v2-1)
        # self.coronal_hSlider.setMaximum(self.v3-1)
        # self.axial_hSlider.setMaximum(self.v3-1)
        # self.sagittal_vSlider.setValue(self.sagittal_vSlider.maximum()//2)
        # self.coronal_vSlider.setValue(self.coronal_vSlider.maximum()//2)
        # self.sagittal_hSlider.setValue(self.sagittal_hSlider.maximum()//2)
        # self.axial_vSlider.setValue(self.axial_vSlider.maximum()//2)
        # self.coronal_hSlider.setValue(self.coronal_hSlider.maximum()//2)
        # self.axial_hSlider.setValue(self.axial_hSlider.maximum()//2)
        pass

    def updateimg(self):
        a_loc = self.sagittal_vSlider.value()
        c_loc = self.axial_vSlider.value()
        s_loc = self.axial_hSlider.value()

        # axial = (self.processedvoxel[a_loc, :, :]).astype(np.uint8).copy()
        # sagittal = (self.processedvoxel[:, :, s_loc]).astype(np.uint8).copy()
        # coronal = (self.processedvoxel[:, c_loc, :]).astype(np.uint8).copy()

        # self.imgLabel_1.slice_loc = [s_loc, c_loc, a_loc]
        # self.imgLabel_2.slice_loc = [s_loc, c_loc, a_loc]
        # self.imgLabel_3.slice_loc = [s_loc, c_loc, a_loc]

        # if self.cross_recalc:
        #     self.imgLabel_1.crosscenter = [self.w*s_loc//self.v3, self.h*c_loc//self.v2]
        #     self.imgLabel_2.crosscenter = [self.w*c_loc//self.v2, self.h*a_loc//self.v1]
        #     self.imgLabel_3.crosscenter = [self.w*s_loc//self.v3, self.h*a_loc//self.v1]

        # if self.colormap is None:
        #     self.imgLabel_1.processedImage = axial
        #     self.imgLabel_2.processedImage = sagittal
        #     self.imgLabel_3.processedImage = coronal

        # self.imgLabel_1.display_image(1)
        # self.imgLabel_2.display_image(1)
        # self.imgLabel_3.display_image(1)
        pass

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MPRInterface()
    window.show()
    sys.exit(app.exec_())