import vtk
import SimpleITK as sitk
import numpy as np
import matplotlib.pyplot as plt
import registration_gui as rgui

def evaluate_registration(fixed_image, moving_image, initial_transform):
    registration_method = sitk.ImageRegistrationMethod()
    registration_method.SetInitialTransform(initial_transform)
    # registration_method.SetMetricAsCorrelation()
    # registration_method.SetMetricAsMattesMutualInformation()
    # registration_method.SetMetricAsMeanSquares()
    # registration_method.SetMetricAsANTSNeighborhoodCorrelation()

    registration_method.SetOptimizerAsGradientDescent(learningRate=1.0, numberOfIterations=100, estimateLearningRate=registration_method.Once)

    # registration_method.SetOptimizerAsConjugateGradientLineSearch()
    # registration_method.SetOptimizerAsRegularStepGradientDescent(4.0, 0.01, 200)
    # registration_method.SetOptimizerAsLBFGS2()
    # registration_method.SetOptimizerAsOnePlusOneEvolutionary()

    registration_method.SetMetricSamplingPercentage(0.01)
    registration_method.SetMetricSamplingStrategy(registration_method.RANDOM)
    registration_method.SetInterpolator(sitk.sitkLinear)
    
    # Collect metric values at each iteration
    # def command_iteration(method):
    #     l = method.GetMetricValue()
    #     print(f"{l:10.5f} ")

    # # registration_method.AddCommand(sitk.sitkIterationEvent, lambda: metric_callback(registration_method))
    # registration_method.AddCommand(sitk.sitkIterationEvent, lambda: command_iteration(registration_method))
    
    # Connect all of the observers so that we can perform plotting during registration.
    registration_method.AddCommand(sitk.sitkStartEvent, rgui.start_plot)
    registration_method.AddCommand(sitk.sitkEndEvent, rgui.end_plot)
    registration_method.AddCommand(sitk.sitkMultiResolutionIterationEvent, rgui.update_multires_iterations) 
    registration_method.AddCommand(sitk.sitkIterationEvent, lambda: rgui.plot_values(registration_method))

    final_transform = registration_method.Execute(fixed_image, moving_image)
    # Always check the reason optimization terminated.
    print('Final metric value: {0}'.format(registration_method.GetMetricValue()))
    print('Optimizer\'s stopping condition, {0}'.format(registration_method.GetOptimizerStopConditionDescription()))
    return final_transform

def main():
    # Load fixed and moving images
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
    fixed_image = sitk.Cast(sitk.GetImageFromArray(reslice_ct_array.reshape(reslice_ct.GetOutput().GetDimensions()[::-1])), sitk.sitkFloat32)

    # mr_conv_image = sitk.Cast(reslice_mr, sitk.sitkFloat32)
    reslice_mr_data = reslice_mr.GetOutput()
    reslice_mr_dimensions = reslice_mr_data.GetDimensions()

    reslice_mr_array = np.array(reslice_mr.GetOutput().GetPointData().GetScalars(), copy=True)
    reslice_mr_array = reslice_mr_array.reshape(reslice_mr_dimensions[2], reslice_mr_dimensions[1], reslice_mr_dimensions[0])
    moving_image = sitk.Cast(sitk.GetImageFromArray(reslice_mr_array.reshape(reslice_mr.GetOutput().GetDimensions()[::-1])), sitk.sitkFloat32)

    # Define initial transformation
    # initial_transform = sitk.Euler3DTransform()
    # initial_transform = sitk.VersorRigid3DTransform()
    # initial_transform = sitk.Similarity3DTransform()
    # initial_transform = sitk.ScaleVersor3DTransform()
    # initial_transform = sitk.ScaleSkewVersor3DTransform()
    # initial_transform = sitk.ComposeScaleSkewVersor3DTransform()
    # initial_transform = sitk.AffineTransform()
    # initial_transform = sitk.BSplineTransform()

    initial_transform = sitk.CenteredTransformInitializer(fixed_image, moving_image, sitk.Similarity3DTransform(), sitk.CenteredTransformInitializerFilter.MOMENTS)
    
    
    # Evaluate registration methods
    final_transform = evaluate_registration(fixed_image, moving_image, initial_transform)

    # Example: Apply transformation to moving image and show the result
    transformed_moving_image = sitk.Resample(moving_image, fixed_image, final_transform, sitk.sitkLinear, 0.0)
    moving_image = sitk.Cast(sitk.RescaleIntensity(moving_image), sitk.sitkUInt8)
    fixed_image = sitk.Cast(sitk.RescaleIntensity(fixed_image), sitk.sitkUInt8)
    transformed_moving_image = sitk.Cast(sitk.RescaleIntensity(transformed_moving_image), sitk.sitkUInt8)
    blended_image = sitk.Compose(fixed_image, transformed_moving_image, fixed_image // 2.0 + transformed_moving_image // 2.0)
    # blended_image = sitk.Add(moving_image, transformed_moving_image)
    im = sitk.GetArrayFromImage(blended_image)
    # print(metric_values)
    metric_values=0
    plt.figure(figsize=(12, 5))
    plt.subplot(1, 2, 1)
    plt.imshow(im[70,:,:], cmap='gray')
    plt.title("Transformed Moving Image")
    plt.axis("off")
    plt.subplot(1, 2, 2)
    # Plot line chart for metric values

    plt.plot(metric_values, marker='o', linestyle='-')
    plt.xlabel('Iteration')
    plt.ylabel('Metric Value')
    plt.title('Registration Metric Value vs. Iteration')
    plt.grid(True)
    plt.show()

if __name__ == "__main__":
    main()
