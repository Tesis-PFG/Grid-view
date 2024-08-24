import itk 
from vtk.util.numpy_support import vtk_to_numpy 

def image_from_vtk_image(vtk_image): 
    """Convert a vtk.vtkImageData to an itk.Image.""" 

    point_data = vtk_image.GetPointData() 
    array = vtk_to_numpy(point_data.GetScalars()) 
    array = array.reshape(-1) 
    is_vector = point_data.GetScalars().GetNumberOfComponents() != 1 
    dims = list(vtk_image.GetDimensions()) 
    if is_vector and dims[-1] == 1: 
        # 2D 
        dims = dims[:2] 
        dims.reverse() 
        dims.append(point_data.GetScalars().GetNumberOfComponents()) 
    else: 
        dims.reverse() 
    array.shape = tuple(dims) 
    image = itk.image_view_from_array(array, is_vector) 

    dim = image.GetImageDimension() 
    spacing = [1.0] * dim 
    spacing[:dim] = vtk_image.GetSpacing()[:dim] 
    image.SetSpacing(spacing) 
    origin = [0.0] * dim 
    origin[:dim] = vtk_image.GetOrigin()[:dim] 
    image.SetOrigin(origin) 
    # Todo: Add Direction with VTK 9 
    return image 