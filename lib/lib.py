import os
import importlib

# Importing all the files inside the lib folder

base_dir = os.path.dirname(os.path.abspath(__file__))

def list_files(base_dir):
    for i in os.listdir(base_dir):
        full_path = os.path.join(base_dir, i)
        
        if os.path.isdir(full_path):
            list_files(full_path)
        else:
            file_path = full_path.split('/')[-1]
            if(file_path.split('.')[-1] == 'py'):
                module_name = file_path.replace(os.sep, ".").removesuffix(".py")
                importlib.import_module(f'lib.{module_name}')
            else:    
                print(f"Not a python file: {file_path}")
list_files(base_dir)