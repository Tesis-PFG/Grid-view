import vtk
import SimpleITK as sitk
import numpy as np


PATH_TC = './INVESTIGACION/Lieidy Orozco/CT Orozco_Pantano_Leidy_Johanna/Craneo - 879111/_Head_1000_5'

PATH_RM = './INVESTIGACION/Lieidy Orozco/Orozco_Pantano_Leidy_Johanna/Resonancia_Nuclear_Magnetica_De_Cerebro - RPID001/T1_3D_TFE_AXI_501'
# Leer las imágenes DICOM de CT y MR usando VTK
ct_reader = vtk.vtkDICOMImageReader()
ct_reader.SetDirectoryName(PATH_TC)
ct_reader.Update()

mr_reader = vtk.vtkDICOMImageReader()
mr_reader.SetDirectoryName(PATH_RM)
mr_reader.Update()

ct_data = ct_reader.GetOutput()
ct_dimensions = ct_data.GetDimensions()

mr_data = mr_reader.GetOutput()
mr_dimensions = mr_data.GetDimensions()

fixed_image = np.array(ct_reader.GetOutput().GetPointData().GetScalars(), copy=True)
fixed_image = fixed_image.reshape(ct_dimensions[2], ct_dimensions[1], ct_dimensions[0])  # Reorganizar las dimensiones si es necesario
moving_image = np.array(mr_reader.GetOutput().GetPointData().GetScalars(), copy=True)
moving_image = moving_image.reshape(mr_dimensions[2], mr_dimensions[1], mr_dimensions[0]) 


# Obtener información espacial de las imágenes DICOM
ct_origin = np.array(ct_reader.GetOutput().GetOrigin())
ct_spacing = np.array(ct_reader.GetOutput().GetSpacing())
mr_origin = np.array(mr_reader.GetOutput().GetOrigin())
mr_spacing = np.array(mr_reader.GetOutput().GetSpacing())

# Crear imágenes SimpleITK desde los Numpy arrays
ct_image = sitk.GetImageFromArray(fixed_image.reshape(ct_reader.GetOutput().GetDimensions()[::-1]))
ct_image.SetSpacing(ct_spacing[::-1])
ct_image.SetOrigin(ct_origin[::-1])

mr_image = sitk.GetImageFromArray(moving_image.reshape(mr_reader.GetOutput().GetDimensions()[::-1]))
mr_image.SetSpacing(mr_spacing[::-1])
mr_image.SetOrigin(mr_origin[::-1])

max_dimensions = [
    min(ct_reader.GetOutput().GetDimensions()[i], mr_reader.GetOutput().GetDimensions()[i])
    for i in range(3)
]

# Configure resizing filter for CT using VTK
# resize_ct = vtk.vtkImageResize()
# resize_ct.SetInputData(vtk_image)
# resize_ct.SetOutputDimensions(max_dimensions)
# resize_ct.Update()
# # Configure resizing filter for CT using VTK
resize_ct = vtk.vtkImageResize()
resize_ct.SetInputConnection(ct_reader.GetOutputPort())
resize_ct.SetOutputDimensions(max_dimensions)
resize_ct.Update()

# Configurar el filtro vtkImageReslice para CT
reslice_ct = vtk.vtkImageReslice()
reslice_ct.SetInputConnection(resize_ct.GetOutputPort())
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

reslice_ct_data = reslice_ct.GetOutput()
reslice_ct_dimensions = reslice_ct_data.GetDimensions()

reslice_ct_array = np.array(reslice_ct.GetOutput().GetPointData().GetScalars(), copy=True)
reslice_ct_array = reslice_ct_array.reshape(reslice_ct_dimensions[2], reslice_ct_dimensions[1], reslice_ct_dimensions[0])
fixed_image_sitk = sitk.Cast(sitk.GetImageFromArray(reslice_ct_array.reshape(reslice_ct.GetOutput().GetDimensions()[::-1])), sitk.sitkFloat32)

# mr_conv_image = sitk.Cast(reslice_mr, sitk.sitkFloat32)
reslice_mr_data = reslice_mr.GetOutput()
reslice_mr_dimensions = reslice_mr_data.GetDimensions()

reslice_mr_array = np.array(reslice_mr.GetOutput().GetPointData().GetScalars(), copy=True)
reslice_mr_array = reslice_mr_array.reshape(reslice_mr_dimensions[2], reslice_mr_dimensions[1], reslice_mr_dimensions[0])
moving_image_sitk = sitk.Cast(sitk.GetImageFromArray(reslice_mr_array.reshape(reslice_mr.GetOutput().GetDimensions()[::-1])), sitk.sitkFloat32)

initial_transform = sitk.CenteredTransformInitializer(fixed_image_sitk, moving_image_sitk, sitk.Euler3DTransform(), sitk.CenteredTransformInitializerFilter.MOMENTS)


# initial_transform = sitk.CenteredTransformInitializer(fixed_image, moving_image, sitk.Euler3DTransform(), sitk.CenteredTransformInitializerFilter.MOMENTS)

registration_method = sitk.ImageRegistrationMethod()
registration_method.SetMetricAsMattesMutualInformation(numberOfHistogramBins=50)
registration_method.SetMetricSamplingStrategy(registration_method.RANDOM)
registration_method.SetMetricSamplingPercentage(0.01)
registration_method.SetInterpolator(sitk.sitkLinear)
registration_method.SetOptimizerAsGradientDescent(learningRate=1.0, numberOfIterations=100, estimateLearningRate=registration_method.Once)
registration_method.SetOptimizerScalesFromPhysicalShift()

registration_method.SetInitialTransform(initial_transform)

final_transform = registration_method.Execute(fixed_image_sitk, moving_image_sitk)

window_level = 2450
window_width = 1100
ct_skull = sitk.IntensityWindowing(fixed_image_sitk, window_level - window_width / 2, window_level + window_width / 2)

# Apply transformation to moving volume
transformed_moving_image = sitk.Resample(moving_image_sitk, fixed_image_sitk, final_transform, sitk.sitkLinear, 0.0)
output_path = './Data/nifti/patient/MR_registrado.nii'
sitk.WriteImage(transformed_moving_image, output_path)
output_path = './Data/nifti/patient/CT_registrado.nii'
sitk.WriteImage(fixed_image_sitk, output_path)

# Blend or overlay images
# fused_image = sitk.Compose(ct_skull, transformed_moving_image, 0.5, 0.5)
# blended_image = sitk.Add(ct_skull, transformed_moving_image)
# output_dicom_path = './Data/nifti/patient/fused/'
# writer = sitk.ImageSeriesWriter()

# # Set metadata for the DICOM series
# writer.SetMetaDataDictionary(blended_image.GetMetaDataDictionary())

# # Write the image as a DICOM series
# writer.SetOutputDirectory(output_dicom_path)
# writer.Execute(blended_image)
