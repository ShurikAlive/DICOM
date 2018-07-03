import gdcm
import numpy
import sys
import os
from PIL import Image, ImageOps


def get_gdcm_to_numpy_typemap():
    """Returns the GDCM Pixel Format to numpy array type mapping."""
    _gdcm_np = {gdcm.PixelFormat.UINT8  :numpy.uint8,
                gdcm.PixelFormat.INT8   :numpy.int8,
                gdcm.PixelFormat.UINT16 :numpy.uint16,
                gdcm.PixelFormat.INT16  :numpy.int16,
                gdcm.PixelFormat.UINT32 :numpy.uint32,
                gdcm.PixelFormat.INT32  :numpy.int32,
                gdcm.PixelFormat.FLOAT32:numpy.float32,
                gdcm.PixelFormat.FLOAT64:numpy.float64 }
    return _gdcm_np

def get_numpy_array_type(gdcm_pixel_format):
    """Returns a numpy array typecode given a GDCM Pixel Format."""
    return get_gdcm_to_numpy_typemap()[gdcm_pixel_format]

def gdcm_to_numpy(image):
    """Converts a GDCM image to a numpy array.
    """
    pf = image.GetPixelFormat().GetScalarType()
    print 'pf', pf
    print image.GetPixelFormat().GetScalarTypeAsString()
    assert pf in get_gdcm_to_numpy_typemap().keys(), \
           "Unsupported array type %s"%pf
    d = image.GetDimension(0), image.GetDimension(1)
    print 'Image Size: %d x %d' % (d[0], d[1])
    dtype = get_numpy_array_type(pf)
    gdcm_array = image.GetBuffer()
    result = numpy.frombuffer(gdcm_array, dtype=dtype)
    maxV = float(result[result.argmax()])
    ## linear gamma adjust
    #result = result + .5*(maxV-result)
    ## log gamma
    result = numpy.log(result+50) ## 50 is apprx background level
    maxV = float(result[result.argmax()])
    result = result*(2.**8/maxV) ## histogram stretch
    result.shape = d
    return result

def readFile(filename):
    r = gdcm.ImageReader()
    r.SetFileName( filename )
    if not r.Read():  sys.exit(1)

    numpy_array = gdcm_to_numpy( r.GetImage() )
  
    pilImage = Image.frombuffer('L',
                           numpy_array.shape,
                           numpy_array.astype(numpy.uint8),
                           'raw','L',0,1)

    pilImage = ImageOps.autocontrast(pilImage, cutoff=.1)
    pilImage.save(filename+'.jpg')
    print(filename+'.jpg')

def readFilesInDir(path):
    names = os.listdir(path)
    for name in names:
        fullname = os.path.join(path, name) # получаем полное имя
        if os.path.isfile(fullname):
            readFile(fullname)
        if os.path.isdir(fullname):
            readFilesInDir(fullname)

if __name__ == "__main__":
  #readFile('75336.dcm')
  #readFile('64118.dcm')
  readFilesInDir('D:\Python\TestDicom\TEST_DB')

