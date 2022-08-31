import os
import shutil
from PIL import Image
import pyheif
from tqdm import tqdm

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
    
    choice = None
    msg = f'Rename {len(common_file_names)} files in {folder2}? [Yes/No]\n'
    while choice is None:
        s = input(msg)
        if s.lower() in {'y', 'yes'}:
            choice = True
        elif s.lower() in {'n', 'no'}:
            choice = False
        else:
            msg = 'Input must be either "Yes","Y", "No" or "N"\n'
    assert choice, 'You must accept the renaming for it to take place'
    
    n_common_files = len(common_file_names)
    print(f'Renaming {n_common_files} files in {folder2}')
    for id, f in enumerate(common_file_names):
        name, ext = os.path.splitext(f)
        new_name = f
        ct = 1
        while new_name in all_file_names:
            new_name = name + '(' + str(ct) + ')' + ext
            ct += 1
        os.rename(os.path.join(folder2,f), os.path.join(folder2,new_name))
        print(f'Renamed {f} to {new_name} ({id+1}/{n_common_files})')
        
            
            
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
        new_dir_name = dir_name + '_all_jpgs'
    
    new_folder = os.path.join(root, new_dir_name)
    assert not os.path.exists(new_folder), f'{new_folder} already exists as a path. Either remove it or provide a name for a new folder'
    os.mkdir(new_folder)
    
    
    print(f'Converting/copying contents')
    print(f'{folder} -> {new_folder}')
    f_ct = 0
    heic_ct = 0
    
    for file_name in tqdm(os.listdir(folder)):
        f_ct += 1
        pth = os.path.join(folder, file_name)

        if not (file_name.lower().endswith('.heic') or file_name.lower().endswith('.heif')):
            new_pth = os.path.join(new_folder, file_name)
            if os.path.isfile(pth):
                shutil.copyfile(pth, new_pth)
            elif os.path.isdir(pth):
                shutil.copytree(pth, new_pth)
        else:
            heic_ct += 1
            name, _ = os.path.splitext(file_name)
            new_pth = os.path.join(new_folder, name + '.JPG')
            try:
                heif_file = pyheif.read(pth)
                image = Image.frombytes(heif_file.mode, heif_file.size, heif_file.data, "raw", heif_file.mode, heif_file.stride)
            except Exception as ex:
                print(f'Could not convert {pth} from heif to jpg')
                raise ex
            image.save(new_pth, "JPEG")
    
    print(f'Copied {f_ct-heic_ct} elements')
    print(f'Converted {heic_ct} .HEIC/.HEIF files .JPG files')
    
    
    