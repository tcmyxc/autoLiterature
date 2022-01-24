import os

path = "./pdf"
# 文件夹中所有文件的文件名
file_names = os.listdir(path)

for name in file_names:
    old_name = name
    if "_" in old_name:
        # print(old_name)
        new_name = str(name).replace("_", "：")
        print(new_name)
        os.renames(os.path.join(path, name),os.path.join(path, new_name)) 
