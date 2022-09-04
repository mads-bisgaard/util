import os
import shutil
from tokenize import Name
from PIL import Image
import pyheif
from tqdm import tqdm
from utils import is_jpeg

class Picture:
    """
    Wrapper for comparing pictures only via pixels. 
    """
    def __init__(self, pth):
        self.__pth = pth
        im = Image.open(pth)
        self.__hash = hash(im.tobytes())
        self.__set_copy = None
        self.__similar_pictures = []
    
    def __hash__(self):
        return self.__hash
    
    def __eq__(self, other):
        self_im = Image.open(self.pth)
        other_im = Image.open(other.pth)
        self_bts = self_im.tobytes()
        other_bts = other_im.tobytes()
        res = self_bts == other_bts
        if res:
            self.__set_copy = other
            other.__set_copy = self
        return res
    
    def find_set_representative(self, pic_set):
        self.__set_copy = None
        if self in pic_set:
            return self.__set_copy
        else:
            return None
    
    @property
    def pth(self):
        return self.__pth
    
    @property
    def similar_pictures(self):
        return self.__similar_pictures
        
    def add_similar_picture(self, pic):
        self.__similar_pictures.append(pic)
        

def report_duplicates(jpeg_set):
    """
    Helper fcn
    """
    print('Report')
    print('='*100)
    nsims = 0
    for pic in jpeg_set:
        if len(pic.similar_pictures) > 0:
            nsims += 1
            msg1 = '"' + pic.pth  + '"' + ' has the following duplicates: \n'
            msg2 = ''
            for elm in pic.similar_pictures:
                msg2 += '\t' + '"' + elm.pth + '"' + '\n'
            print(msg1 + msg2)
    if nsims == 0:
        print('No duplicates were found')
    print('='*100)

def find_duplicates(folder1, folder2=None):
    """
    Determine duplicate pictures (pixel-wise). When only a single path is passed, it checks if there are duplicate pictures
    within that directory and prints a report. If a second directory is passed it is instead determined which pictures in the 
    second directory are also in the first.

    Args:
        folder1 (String): Path to first directory
        folder2 (String, optional): Path to second directory. Defaults to None.
    """
    assert os.path.isdir(folder1), f'{folder1} is not a directory'
    folder1 = os.path.abspath(folder1)
    
    if folder2 is None:
        jpeg_set = set()
        print('Comparing JPEG files...')
        for pth in tqdm(os.listdir(folder1)):
            pth = os.path.join(folder1, pth)
            if is_jpeg(pth):
                pic = Picture(pth)
                if pic in jpeg_set:
                    set_rep = pic.find_set_representative(jpeg_set)
                    set_rep.add_similar_picture(pic)
                else:
                    jpeg_set.add(pic)
        if len(jpeg_set) == 0:
            print('No duplicates were found')
        else:
            report_duplicates(jpeg_set)
    else:
        assert os.path.isdir(folder2), f'{folder2} is not a directory'
        folder2 = os.path.abspath(folder2)
        print(f'Computing distincts JPEG files in {folder1}...')
        jpegs1 = set()
        for elm in tqdm(os.listdir(folder1)):
            elm = os.path.join(folder1,elm)
            if is_jpeg(elm):
                jpegs1.add( Picture(elm) )
        
        print(f'Checking for duplicate JPEG files in {folder2}...')
        for elm in tqdm(os.listdir(folder2)):
            elm = os.path.join(folder2,elm)
            if is_jpeg(elm):
                pic = Picture(elm)
                if pic in jpegs1:
                    set_rep = pic.find_set_representative(jpegs1)
                    set_rep.add_similar_picture(pic)
        report_duplicates(jpegs1)
        
    
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
    
    if len(common_file_names) == 0:
        print('No duplicate file names were found')
        return
    
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
        all_file_names.add(new_name)
        print(f'Renamed {f} to {new_name} ({id+1}/{n_common_files})')
        
            
def check_gthumb_comment_dir(folder):
    """
    Check which files are missing in the '.comments' directory in a gthumbs directory 

    Args:
        folder (String): Gthumb directory
    """
    assert os.path.isdir(folder), f'{folder} must be a valid directory path'
    folder = os.path.abspath(folder)
    
    comments_folder = os.path.join(folder,'.comments')
    if not os.path.isdir(comments_folder):
        raise Exception(f'{folder} does not contain a .comments subdirectory')

    comments_file_names = set( )
    for file_name in os.listdir(comments_folder):
        if os.path.isfile(os.path.join(comments_folder,file_name)):
            name, ext = os.path.splitext(file_name)
            if ext == '.xml':
                comments_file_names.add(name)

    for file_name in os.listdir(folder):
        pth = os.path.join(folder, file_name)
        if os.path.isfile(pth):
            if not file_name in comments_file_names:
                print(f'{file_name} does not have a corresponding match in the .comments directory')
            

            
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
    
    
if __name__ == '__main__':
    find_duplicates('/home/madsbisgaard/Downloads/1.8.2020-3.9.2022')