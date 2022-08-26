import os

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
    
    _, _, folder1_files = next(os.walk(folder1))
    _, _, folder2_files = next(os.walk(folder2))
    
    common_file_names = set(folder1_files).intersection(set(folder2_files))
    all_file_names = set(folder1_files).union(set(folder2_files))
    
    for f in common_file_names:
        new_name = f
        ct = 1
        while new_name in all_file_names:
            new_name = f + '(' + str(ct) + ')'
            ct += 1
        os.rename(os.path.join(folder2,f), os.path.join(folder2,new_name))
        print(f'Renamed {os.path.join(folder2,f)} to {os.path.join(folder2,new_name)}')
        
            
            
    
    
    
    