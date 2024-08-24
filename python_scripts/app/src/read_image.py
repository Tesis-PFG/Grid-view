
import argparse
import vtkmodules.vtkRenderingOpenGL2

from vtk import vtkDICOMImageReader
from vtkmodules.vtkCommonColor import vtkNamedColors
from vtkmodules.vtkCommonDataModel import vtkSphere
from vtkmodules.vtkIOImage import vtkImageReader2Factory
from vtkmodules.vtkImagingCore import (
    vtkImageCast,
    vtkImageShiftScale
)
from vtkmodules.vtkImagingGeneral import vtkImageGaussianSmooth
from vtkmodules.vtkImagingHybrid import vtkSampleFunction
from vtkmodules.vtkImagingMath import vtkImageMathematics
from vtkmodules.vtkInteractionStyle import vtkInteractorStyleImage
from vtkmodules.vtkRenderingCore import (
    vtkImageActor,
    vtkRenderWindow,
    vtkRenderWindowInteractor,
    vtkRenderer
)

def get_program_parameters():
    description = 'Open image'
    epilogue = '''
    Read image
    '''
    parser = argparse.ArgumentParser(description=description, epilog=epilogue,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument('filename', help='AttenuationArtifact.pgm.')
    args = parser.parse_args()
    return args.filename

def read_images():
    colors = vtkNamedColors()

    fileName = get_program_parameters()

    # Read the image.
    readerFactory = vtkImageReader2Factory()
    reader = readerFactory.CreateImageReader2(fileName)
    reader.SetFileName(fileName)
    reader.Update()

    return image

def render_image(images): 
    renderWindow = vtkRenderWindow()
    renderWindow.SetSize(600, 300)
    renderWindow.AddRenderer(images)
    renderWindow.SetWindowName('CT')

    renderWindowInteractor = vtkRenderWindowInteractor()
    style = vtkInteractorStyleImage()

    renderWindowInteractor.SetInteractorStyle(style)

    renderWindowInteractor.SetRenderWindow(renderWindow)
    renderWindowInteractor.Initialize()

    renderWindowInteractor.Start()

if __name__ == '__main__':
    PATH = 'Data/David Mayorga/Mayorga_Herrera_David_Ricardo/Resonancia_Nuclear_Magnetica_De_Cerebro_Cte_Prot_Dr_Buitrago - RPID001/T1_3D_TFE_AXI_501'

    image = read_images()

    
    