import os
import shutil
from PIL import Image
import pyheif

def rename_files(folder1, folder2):
    """
    Renames all files in folder2 whose name also appears in folder1.
    If file named "thisfile" appears in both folder1 and folder2 then the name of the 
    copy in folder2 is changed to "thisfile(1)". If that file also exists in folder1 and/or 
    folder2 then it is changed to "thisfile(2)" etc.    

    Args:
        folder1 (string)        : Path to first folder
        folder2 (string)        : Path to second folder
    """
    assert os.path.isdir(folder1), f'{folder1} is not a directory'
    assert os.path.isdir(folder2), f'{folder2} is not a directory'
    folder1 = os.path.abspath(folder1)
    folder2 = os.path.abspath(folder2)
    
    folder1_set = set( name for name in os.listdir(folder1) if os.path.isfile(os.path.join(folder1, name)) )
    folder2_set = set( name for name in os.listdir(folder2) if os.path.isfile(os.path.join(folder2, name)) )
    
    common_file_names = folder1_set.intersection(folder2_set)
    all_file_names = folder1_set.union(folder2_set)
    
    for f in common_file_names:
        name, ext = os.path.splitext(f)
        new_name = f
        ct = 1
        while new_name in all_file_names:
            new_name = name + '(' + str(ct) + ')' + ext
            ct += 1
        os.rename(os.path.join(folder2,f), os.path.join(folder2,new_name))
        print(f'Renamed {os.path.join(folder2,f)} to {os.path.join(folder2,new_name)}')
        
            
            
def heic_to_jpg(folder, new_dir_name=None):
    """
    Create a copy of a folder in which all .heic/.heif files are converted to .jpg files
    
    Args:
        folder (string):        Name of folder
        new_dir_name (string):  Optional name of new folder. Default is <folder>_all_jpegs
    """
    assert os.path.isdir(folder), f'{folder} must be the path to an existing directory'
    folder = os.path.abspath(folder)
    
    root, dir_name = os.path.split(folder)
    if new_dir_name is None:
        new_folder = os.path.join(root, dir_name, '_all_jpgs')
    else:
        new_folder = os.path.join(root, new_dir_name)
    assert not os.path.exists(new_folder), f'{new_folder} already exists as a path. Either remove it or provide a name for a new folder'
    os.mkdir(new_folder)
    
    for name in os.path.listdir(folder):
        pth = os.path.join(folder, name)
        new_pth = os.path.join(new_folder, name)
        
        if not (name.endswith('.heic') or name.endswith('.heif')):
            if os.path.isfile(pth):
                shutil.copyfile(pth, new_pth)
            elif os.path.isdir(pth):
                shutil.copytree(pth, new_pth)
        else:
            heif_file = pyheif.read(pth)
            image = Image.frombytes(heif_file.mode, heif_file.size, heif_file.data, "raw", heif_file.mode, heif_file.stride)
            image.save(new_pth, "JPEG")
    
    
    
    