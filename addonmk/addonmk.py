import os
import shutil
import subprocess

def open_folder(path):
	# Check if the folder exists
	if os.path.exists(path):
		# Open the folder
		subprocess.Popen(f'explorer "{os.path.realpath(path)}"')
	else:
		print("The folder does not exist.")

# Get the current directory name
current_dir = os.path.basename(os.getcwd())

# Define the new directories
new_dir = os.path.join("E:\\Steam\\steamapps\\common\\GarrysMod", current_dir)
maps_dir = os.path.join(new_dir, "maps")
thumb_dir = os.path.join(maps_dir, "thumb")

# Create the directories
os.makedirs(thumb_dir, exist_ok=True)

# Define the .bsp file path
bsp_file = os.path.join("E:\\Steam\\steamapps\\common\\GarrysMod\\garrysmod\\maps", current_dir + ".bsp")

# Define the .nav file path
nav_file = os.path.join("E:\\Steam\\steamapps\\common\\GarrysMod\\garrysmod\\maps", current_dir + ".nav")

# Check if the .bsp file exists and move it
if os.path.isfile(bsp_file):
    shutil.move(bsp_file, maps_dir)
else:
	print("BSP not found")

# Check if the .nav file exists and move it
if os.path.isfile(nav_file):
    shutil.move(nav_file, maps_dir)
else:
	print("Navmesh not found")

# Define the .png file path
png_file = os.path.join("screenshots", current_dir + ".png")

# Define the .jpg file path
jpg_file = os.path.join("screenshots", current_dir + ".jpg")

# Check if the .png file exists
if os.path.isfile(png_file):
    # If the .jpg file exists, move the .png file
    if os.path.isfile(jpg_file):
        shutil.move(png_file, thumb_dir)
    # If the .jpg file does not exist, copy the .png file
    else:
        shutil.copy(png_file, thumb_dir)

open_folder(new_dir)
