import os
import time
import pyperclip
import pyautogui
import psutil
import shutil
import subprocess

# The first string of text to copy to the clipboard
first_path = r'E:\Steam\steamapps\common\GarrysMod\sourceengine'

# Get the current folder name
folder_name = os.path.basename(os.getcwd())

# Construct the full path of the vmf file
vmf_file_path = os.path.join(os.getcwd(), 'mapsrc', f'{folder_name}_model.vmf')

# The path of the program to open
program_path = r'E:\legoj\Documents\SourceModding\VMFtoSMD\VMFtoSMD.exe'

# Open the program
os.startfile(program_path)

# Wait for the program to open
time.sleep(2)

# Press tab three times
for _ in range(3):
    pyautogui.press('tab')
    time.sleep(0.1)

# Press enter
pyautogui.press('enter')

# Wait 2 seconds
time.sleep(2)

# Paste in the vmf file path
pyperclip.copy(vmf_file_path)
pyautogui.hotkey('ctrl', 'v')

# Press enter
pyautogui.press('enter')

# Press tab three times
for _ in range(3):
    pyautogui.press('tab')
    time.sleep(0.1)

# Press space
pyautogui.press('space')

# Press tab two more times
for _ in range(2):
    pyautogui.press('tab')
    time.sleep(0.1)

# Press space
pyautogui.press('space')

# Press tab nine more times
for _ in range(9):
    pyautogui.press('tab')
    time.sleep(0.1)

# Paste the first path
pyperclip.copy(first_path)
pyautogui.hotkey('ctrl', 'v')

# Press tab seven more times
for _ in range(7):
    pyautogui.press('tab')
    time.sleep(0.1)

# Press space
pyautogui.press('space')

# Press tab seven more times
for _ in range(7):
    pyautogui.press('tab')
    time.sleep(0.1)

# Press space
pyautogui.press('space')

# Wait 2 seconds
time.sleep(2)

# Kill the VMFtoSMD.exe process
for proc in psutil.process_iter():
    if proc.name() == "VMFtoSMD.exe":
        proc.kill()

# Wait for the .smd file to be created
time.sleep(2)

# Construct the paths of the .smd file and the new folder
smd_file_path = os.path.join(os.getcwd(), 'mapsrc', f'{folder_name}_model.smd')
new_folder_path = os.path.join(os.getcwd(), 'modelsrc', 'legoj15', 'maps', folder_name)

# Create the new folder if it doesn't exist
os.makedirs(new_folder_path, exist_ok=True)

# If the destination file already exists, remove it
if os.path.exists(os.path.join(new_folder_path, f'{folder_name}_model.smd')):
    os.remove(os.path.join(new_folder_path, f'{folder_name}_model.smd'))

# Move the .smd file to the new folder
shutil.move(smd_file_path, new_folder_path)

# Notify the user that the file has been moved
print(f'{folder_name}_model.smd has been moved to {new_folder_path}')

# Construct the path of the .qc file
qc_file_path = os.path.join(new_folder_path, f'{folder_name}_model.qc')

# Create the .qc file and write the specified content to it
with open(qc_file_path, 'w') as f:
    f.write(f'$modelname legoj15\\maps\\{folder_name}\\{folder_name}_model\n')
    f.write('$staticprop\n')
    f.write('$casttextureshadows\n')
    f.write(f'$body translucents {folder_name}_model.smd\n')
    f.write('$cdmaterials "models\legoj15\maps"\n')
    f.write(f'$sequence idle {folder_name}_model.smd\n')

# Read the .smd file and gather all the unique material names
with open(os.path.join(new_folder_path, f'{folder_name}_model.smd'), 'r') as f:
    lines = f.readlines()
    materials = []
    for line in lines[lines.index('triangles\n')+1:]:
        if line.strip() == 'end':
            break
        material = line.strip().split()[0]
        if material not in materials and material != '0':
            materials.append(material)

# If there are over 32 unique materials in the SMD, warn the user
if len(materials) > 32:
    print('Warning: There are over 32 unique materials in the SMD.')

# Write the $texturegroup node to the .qc file
with open(qc_file_path, 'a') as f:
    f.write('$texturegroup skinfamilies\n')
    f.write('{\n')
    f.write('\t{ ' + ' '.join(f'"{material}"' for material in materials) + ' }\n')
    f.write('\t{ ' + ' '.join('"translucentmaps"' for _ in materials) + ' }\n')
    f.write('}\n')

# Run studiomdl.exe with the specified parameters
subprocess.run([r'E:\Steam\steamapps\common\GarrysMod\bin\studiomdl.exe', '-game', r'E:\Steam\steamapps\common\GarrysMod\garrysmod', '-nop4', '-fastbuild', qc_file_path])

# Wait for the output files to be created
time.sleep(2)

# Construct the paths of the output files and the new folder
output_files = [f'{folder_name}_model.dx90.vtx', f'{folder_name}_model.mdl', f'{folder_name}_model.vvd']
output_folder_path = f'E:\Steam\steamapps\common\GarrysMod\{folder_name}\models\legoj15\maps\{folder_name}'

# Create the new folder if it doesn't exist
os.makedirs(output_folder_path, exist_ok=True)

# Move the output files to the new folder
for file in output_files:
    # If the destination file already exists, remove it
    if os.path.exists(os.path.join(output_folder_path, file)):
        os.remove(os.path.join(output_folder_path, file))
        
    shutil.move(os.path.join(f'E:\Steam\steamapps\common\GarrysMod\garrysmod\models\legoj15\maps\{folder_name}', file), output_folder_path)
    
    # Notify the user that the file has been moved
    print(f'{file} has been moved to {output_folder_path}')


# Open the lights_custom.rad file and add a new line to it
#with open(r'E:\Steam\steamapps\common\GarrysMod\garrysmod\lights_custom.rad', 'r+') as f:
#    lines = f.readlines()
#    lines.append(f'forcetextureshadow legoj15/maps/{folder_name}/{folder_name}_model.mdl\n')
#    lines.sort()
#    f.seek(0)
#    f.writelines(lines)
