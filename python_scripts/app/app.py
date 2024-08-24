import vtk
import SimpleITK as sitk
import numpy as np
import os

# Rutas de las imágenes DICOM de CT y MR

PATH_RM = './Data/David Mayorga/T1_3D_TFE_AXI_601'
PATH_TC = './Data/David Mayorga/_Head_10_3'

# Leer las imágenes DICOM de CT y MR usando VTK
mr_reader = vtk.vtkDICOMImageReader()
mr_reader.SetDirectoryName(PATH_RM)
mr_reader.Update()

ct_reader = vtk.vtkDICOMImageReader()
ct_reader.SetDirectoryName(PATH_TC)
ct_reader.Update()

# Convertir las imágenes DICOM a Numpy arrays
# ct_array = vtk.util.numpy_supp}ort.vtk_to_numpy(ct_reader.GetOutput().GetPointData().GetScalars())
# mr_array = vtk.util.numpy_support.vtk_to_numpy(mr_reader.GetOutput().GetPointData().GetScalars())
ct_data = ct_reader.GetOutput()
ct_dimensions = ct_data.GetDimensions()

mr_data = mr_reader.GetOutput()
mr_dimensions = mr_data.GetDimensions()

ct_array = np.array(ct_reader.GetOutput().GetPointData().GetScalars(), copy=True)
ct_array = ct_array.reshape(ct_dimensions[2], ct_dimensions[1], ct_dimensions[0])  # Reorganizar las dimensiones si es necesario
mr_array = np.array(mr_reader.GetOutput().GetPointData().GetScalars(), copy=True)
mr_array = mr_array.reshape(mr_dimensions[2], mr_dimensions[1], mr_dimensions[0])  # Reorganizar las dimensiones si es necesario


# Obtener información espacial de las imágenes DICOM
ct_origin = np.array(ct_reader.GetOutput().GetOrigin())
ct_spacing = np.array(ct_reader.GetOutput().GetSpacing())
mr_origin = np.array(mr_reader.GetOutput().GetOrigin())
mr_spacing = np.array(mr_reader.GetOutput().GetSpacing())

# Crear imágenes SimpleITK desde los Numpy arrays
ct_image = sitk.GetImageFromArray(ct_array.reshape(ct_reader.GetOutput().GetDimensions()[::-1]))
ct_image.SetSpacing(ct_spacing[::-1])
ct_image.SetOrigin(ct_origin[::-1])

mr_image = sitk.GetImageFromArray(mr_array.reshape(mr_reader.GetOutput().GetDimensions()[::-1]))
mr_image.SetSpacing(mr_spacing[::-1])
mr_image.SetOrigin(mr_origin[::-1])

# Realizar el registro de las imágenes usando SimpleITK
registration_method = sitk.ImageRegistrationMethod()

# Configurar el método de registro (puedes ajustar los parámetros según tus necesidades)
registration_method.SetMetricAsMeanSquares()
registration_method.SetOptimizerAsRegularStepGradientDescent(learningRate=2.0, minStep=0.01, numberOfIterations=100)
registration_method.SetInterpolator(sitk.sitkLinear)

transform = sitk.Transform(3, sitk.sitkAffine)
registration_method.SetInitialTransform(transform)

ct_conv_image = sitk.Cast(ct_image, sitk.sitkFloat32)
mr_conv_image = sitk.Cast(mr_image, sitk.sitkFloat32)
registration_method.Execute(ct_conv_image, mr_conv_image)

# Aplicar la transformación a la imagen de CT usando VTK
transform_vtk = vtk.vtkTransform()
matrix = sitk.Euler3DTransform(transform.GetParameters())
# Crear una transformación de VTK
transform_vtk = vtk.vtkTransform()

# Obtener la matriz de transformación de SimpleITK y asignarla a VTK
matrix_sitk = np.array(matrix.GetMatrix()).reshape((3, 3))
matrix_vtk = vtk.vtkMatrix4x4()

# Asignar cada elemento de la matriz de SimpleITK a la matriz de VTK
for i in range(3):
    for j in range(3):
        matrix_vtk.SetElement(i, j, matrix_sitk[i, j])

# Establecer la matriz de transformación en VTK
transform_vtk.SetMatrix(matrix_vtk)

# Determinar las dimensiones máximas entre CT y MR
max_dimensions = [
    min(ct_reader.GetOutput().GetDimensions()[i], mr_reader.GetOutput().GetDimensions()[i])
    for i in range(3)
]

# Configurar el filtro de redimensionamiento para CT
resize_ct = vtk.vtkImageResize()
resize_ct.SetInputConnection(ct_reader.GetOutputPort())
resize_ct.SetOutputDimensions(max_dimensions)
# resize_ct.SetInterpolate()
resize_ct.Update()

# Configurar el filtro de redimensionamiento para MR
# resize_mr = vtk.vtkImageResize()
# resize_mr.SetInputConnection(mr_reader.GetOutputPort())
# resize_mr.SetOutputDimensions(max_dimensions)
# resize_mr.SetInterpolationModeToLinear()
# resize_mr.Update()

# Determinar las dimensiones máximas entre CT y MR
max_dimensions = [min(d1, d2) for d1, d2 in zip(ct_dimensions, mr_dimensions)]

# Configurar el filtro vtkImageReslice para CT
reslice_ct = vtk.vtkImageReslice()
reslice_ct.SetInputConnection(resize_ct.GetOutputPort())
# reslice_ct.SetOutputSpacing(max_dimensions[0] * ct_spacing[0] / ct_dimensions[0],
#                              max_dimensions[1] * ct_spacing[1] / ct_dimensions[1],
#                              max_dimensions[2] * ct_spacing[2] / ct_dimensions[2])
reslice_ct.SetOutputSpacing(max_dimensions[0] * mr_spacing[0] / mr_dimensions[0],
                             max_dimensions[1] * mr_spacing[1] / mr_dimensions[1],
                             max_dimensions[2] * mr_spacing[2] / mr_dimensions[2])
reslice_ct.SetOutputExtent(0, max_dimensions[0] - 1, 0, max_dimensions[1] - 1, 0, max_dimensions[2] - 1)
reslice_ct.SetInterpolationModeToLinear()
reslice_ct.Update()

# Configurar el filtro vtkImageReslice para MR
reslice_mr = vtk.vtkImageReslice()
reslice_mr.SetInputConnection(mr_reader.GetOutputPort())
reslice_mr.SetOutputSpacing(max_dimensions[0] * mr_spacing[0] / mr_dimensions[0],
                             max_dimensions[1] * mr_spacing[1] / mr_dimensions[1],
                             max_dimensions[2] * mr_spacing[2] / mr_dimensions[2])
reslice_mr.SetOutputExtent(0, max_dimensions[0] - 1, 0, max_dimensions[1] - 1, 0, max_dimensions[2] - 1)
reslice_mr.SetInterpolationModeToLinear()
reslice_mr.Update()

# reslice = vtk.vtkImageReslice()
# reslice.SetInputConnection(ct_reader.GetOutputPort())
# reslice.SetResliceTransform(transform_vtk)
# reslice.SetInterpolationModeToLinear()
# reslice.Update()

# Convertir la imagen de CT registrada a NIfTI usando SimpleITK
# registered_ct_array = vtk.util.numpy_support.vtk_to_numpy(reslice.GetOutput().GetPointData().GetScalars()).reshape(reslice.GetOutput().GetDimensions()[::-1])
registered_ct_array = np.array(reslice_ct.GetOutput().GetPointData().GetScalars(), copy=True)
registered_ct_array = registered_ct_array.reshape(reslice_ct.GetOutput().GetDimensions()[::-1]) 
registered_ct_image = sitk.GetImageFromArray(registered_ct_array)
registered_ct_image.SetSpacing(mr_spacing[::-1])
registered_ct_image.SetOrigin(ct_origin[::-1])

registered_mr_array = np.array(reslice_mr.GetOutput().GetPointData().GetScalars(), copy=True)
registered_mr_array = registered_mr_array.reshape(reslice_mr.GetOutput().GetDimensions()[::-1]) 
registered_mr_image = sitk.GetImageFromArray(registered_mr_array)
registered_mr_image.SetSpacing(mr_spacing[::-1])
registered_mr_image.SetOrigin(mr_origin[::-1])

# Guardar la imagen de CT registrada como NIfTI
output_path = './Data/nifti/david/CT/CT_registrado.nii'
sitk.WriteImage(registered_ct_image, output_path)
output_path = './Data/nifti/david/MR/MR_registrado.nii'
sitk.WriteImage(registered_mr_image, output_path)
