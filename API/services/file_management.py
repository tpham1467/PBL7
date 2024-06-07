from os import listdir
import os
from os.path import isfile, join
from typing import List
from database import mysql_connector

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
    
    file_data_list = mysql_connector.getAll('file_data')
    result = []
    for file in file_data_list:
        result.append(FileData(file[1], file[2], file[3], file[4]))
    return result

def insertFileDataService(dir: str):
    """
    following the dir, insert file data if not exist

    Args:
    dir (str): The path to the file.

    Returns:
    void
    """
    try:
        if not os.path.isfile(dir):
            raise FileNotFoundError(f"The file '{dir}' does not exist.")
        file_name = os.path.basename(dir)
        result = mysql_connector.get_all_by_conditional(
            'file_data', 
            f"name LIKE '%{dir}%'", ['*'])
        file_size = os.path.getsize(dir)

        if (len(result)== 0):
            mysql_connector.insert_file_data(name=file_name, dir=dir, size=file_size)

    except Exception as e:
        print(f"Error: {e}")
        return None, None
    
def get_file_by_name(name: str):
    result = mysql_connector.get_all_by_conditional(
            'file_data', 
            f"name = '{name}'", ['*'])
    file = FileData(result[0][1], result[0][2], result[0][3], result[0][4])
    print (f"found file {file.name} dir {file.dir}")
    return file

def process_data_file_name(dir: str):
    return os.path.basename(dir)