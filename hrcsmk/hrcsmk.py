import os
import shutil
import sys
import stat
import subprocess
import logging
import pyperclip

# Check if a command line argument was provided
if len(sys.argv) > 1:
    filename = sys.argv[1]
else:
    # Ask for the name of the .vmf file
    filename = input("Enter the name of the .vmf file: ")

# If the filename ends with _hrcs, remove it
if filename.endswith("_hrcs"):
    filename = filename[:-5]

# Define the source and destination directories
source_dir = os.path.join(os.pardir, "HL2-MapPack")
dest_dir = os.path.join(os.curdir, filename + "_hrcs", "mapsrc")

# Create the destination directory if it doesn't exist
os.makedirs(dest_dir, exist_ok=True)

# Define the source and destination file paths
source_file = os.path.join(source_dir, filename + ".vmf")
dest_file = os.path.join(dest_dir, filename + "_hrcs.vmf")

# Copy the .vmf file
shutil.copy2(source_file, dest_file)

# Remove the "Read Only" attribute from the copied file
os.chmod(dest_file, stat.S_IWRITE)

# Copy the "HRCS checklisk.txt" file into the <vmffilename_hrcs> folder
checklist_file = os.path.join(os.curdir, filename + "_hrcs", "HRCS checklisk.txt")
shutil.copy2("HRCS checklisk.txt", checklist_file)

# After copying the .vmf and .txt files

# Read the .vmf file and count occurrences of "info_player_start" and "game_ragdoll_manager"
with open(dest_file, 'r') as file:
    vmf_content = file.read()
info_player_start_count = vmf_content.count("info_player_start")
game_ragdoll_manager_count = vmf_content.count("game_ragdoll_manager")

# If "info_player_start" appears only once, modify the .txt file
if info_player_start_count == 1:
    with open(checklist_file, 'r') as file:
        lines = file.readlines()
    # Remove the line that says 'remove non-beginning info_player_start'
    lines = [line for line in lines if line.strip() != 'remove non-beginning info_player_start']
    with open(checklist_file, 'w') as file:
        file.writelines(lines)

# If "game_ragdoll_manager" does not appear, modify the .txt file
if game_ragdoll_manager_count == 0:
    with open(checklist_file, 'r') as file:
        lines = file.readlines()
    # Remove the line that says 'set ragdoll manager to -1'
    lines = [line for line in lines if line.strip() != 'set ragdoll manager to -1']
    with open(checklist_file, 'w') as file:
        file.writelines(lines)

# List of lines to be removed
remove_lines = [
    "extract wvt patches",
    "run hrcsmk command with name of half-life 2 map",
    "copy to project folder",
    "save map with hrcs suffix",
    'change "fademaxdist" (0), "fademindist" (-1), "PerformanceMode" (2)',
    'find lowest "lightmapscale" in the level',
    "change changelevel triggers to maps with hrcs suffix",
    "change cubemaps to 256x256",
    "remove all func_occluder",
    "remove fog culling",
    "change func_wall to func_brush",
    "convert prop_detail to prop_static"
]

# Remove the specified lines from the copied file
with open(checklist_file, 'r') as file:
    lines = file.readlines()
lines = [line for line in lines if line.strip() not in remove_lines]
with open(checklist_file, 'w') as file:
    file.writelines(lines)

# Function to handle opening folders
def open_folder(path):
    # Check if the folder exists
    if os.path.exists(path):
        # Open the folder
        subprocess.Popen(f'explorer "{os.path.realpath(path)}"')
    else:
        print("The folder does not exist.")

original_directory = os.getcwd()
os.chdir(filename + "_hrcs")
project_directory = os.getcwd()
os.chdir(original_directory)

# Change the current working directory to the "mapsrc" directory
os.chdir(dest_dir)

# Set up logging
log_file = os.path.join(project_directory, 'output.log')
logging.basicConfig(filename=log_file, level=logging.INFO)

# Function to handle the subprocess calls
def run_subprocess(command):
    process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    while True:
        output = process.stdout.readline()
        if output == b'' and process.poll() is not None:
            break
        if output:
            print(output.strip().decode())
            logging.info(output.strip().decode())
    rc = process.poll()
    return rc

# Run the "maxvis" command with Python
run_subprocess(["python", "E:/freesw/bin/maxvis.py"])

os.chdir(project_directory)

# Run the "entconv" command with Python
run_subprocess(["python", "E:/freesw/bin/entconv.py"])

os.chdir(original_directory)

os.chdir(dest_dir)

# Run the "wvtextract" command with Python
run_subprocess(["python", "E:/freesw/bin/wvtextract.py"])

# Change the current working directory to the filename + "_hrcs" directory
pyperclip.copy(filename + "_hrcs")

# Open the new project folder
os.chdir(project_directory)
open_folder(os.getcwd())

def add_to_mount_cfg(filename):
    # Define the path to the mount.cfg file
    cfg_path = "E:\\Steam\\steamapps\\common\\GarrysMod\\garrysmod\\cfg\\mount.cfg"

    # Define the new line to be added
    new_line = f"\t{filename}_hrcs\tE:\\Steam\\steamapps\\common\\GarrysMod\\{filename}_hrcs"

    # Read the content of the file
    with open(cfg_path, "r") as file:
        lines = file.readlines()

    # Find the index of the line containing "}"
    end_index = next(i for i, line in enumerate(lines) if "}" in line)

    # Insert the new line before the "}"
    lines.insert(end_index, new_line + "\n")

    # Write the modified content back to the file
    with open(cfg_path, "w") as file:
        file.writelines(lines)

    print(f"The line '{new_line}' was successfully added to the mount.cfg file.")

add_to_mount_cfg(filename)

def open_program(program_path, dest_dir):
    # Check if the program exists
    if os.path.exists(program_path):
        # Open the program with dest_dir as a command line argument
        subprocess.Popen([program_path, dest_dir])
    else:
        print("The program does not exist.")
        
import psutil

def is_process_running(process_name):
    # Iterate over all running process
    for proc in psutil.process_iter():
        try:
            # Check if process name contains the given name string.
            if process_name.lower() in proc.name().lower():
                return True
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            pass
    return False;

os.chdir(original_directory)

# Check if "Hammer.exe" is running, and if not, open with map file
if is_process_running("Hammer.exe"):
    print('It is ' + str(is_process_running("Hammer.exe")) + ' that Hammer is already running')
else:
    open_program("E:\\Steam\\steamapps\\common\\GarrysMod\\bin\\hammer.exe", dest_file)

# Open useful and necessary files
open_program("E:\\Program Files\\Notepad++\\notepad++.exe", log_file)
open_program("E:\\Program Files\\Notepad++\\notepad++.exe", checklist_file)
open_program("E:\\Program Files\\Notepad++\\notepad++.exe", dest_file)
