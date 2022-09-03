from PIL import Image

def is_jpeg(pth):
    """
    Determine whether or not a path is a JPEG

    Args:
        pth (String): Path
    """
    try:
        im = Image.open(pth)
        res = im.format == 'JPEG'
    except:
        res = False
    return res