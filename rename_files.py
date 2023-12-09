import os
import re

path = r'I:\DATA\潜热\0.5D'
for year_index in os.listdir(path):
    sub_path = os.path.join(path, year_index)
    for file in os.listdir(sub_path):
        os.rename(os.path.join(sub_path, file), os.path.join(sub_path, f'LH{year_index}_{file[8: ]}'))

print('done!')