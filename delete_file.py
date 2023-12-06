import os
import re
import glob

path = r'E:\LAI'

for sub_folder in os.listdir(path):
    sub_path = os.path.join(path, sub_folder)
    for file in os.listdir(sub_path):
        if len(file) <= 15:
            print(file)
            os.remove(os.path.join(sub_path, file))
print('done!')