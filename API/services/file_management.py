from os import listdir
import os
from os.path import isfile, join
from typing import List

from pydantic import BaseModel

from entities.FileData import FileData

def test():
    print('Test function')

__path__ = {} 
__path__['crawl_data'] = './data' 
__path__['process_data'] = './process_data'
__file_name__ = {}
__file_name__['tgdd_categories'] = 'tgdd_categories'
__file_name__['tgdd_end_page_link'] = 'tgdd_end_page_link'
__file_name__['tgdd_product_link'] = 'tgdd_product_link'
__file_name__['tgdd_description'] = 'tgdd_description'
__file_name__['tgdd_description_preprocessed'] = 'tgdd_description_preprocessed'

def get_human_readable_size(size: int) -> str:
    for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
        if size < 1024.0:
            return f"{size:.2f} {unit}"
        size /= 1024.0
    return f"{size:.2f} {unit}"

def getAllFile(type: str = None) -> List[FileData]:
    files = [f for f in listdir(__path__[type]) if isfile(join(__path__[type], f))]
    file_data_list = []
    for file in files:
        file_path = join(__path__[type], file)
        file_size = get_human_readable_size(os.path.getsize(file_path))
        file_data = FileData(name=file, dir=__path__[type], size=file_size)
        file_data_list.append(file_data)
    return file_data_list
