import os
import time
import subprocess
import ctypes
import psutil
from pynput.keyboard import Controller as KeyboardController, Key
from pynput.mouse import Controller as MouseController, Button

def tail(file):
    file.seek(0, os.SEEK_END)
    while True:
        line = file.readline()
        if not line:
            time.sleep(0.1)
            continue
        yield line

# Check if 'output.txt' exists in the current directory
if not os.path.exists('output.txt'):
	# If not, run 'possub.py'
	possub_path = r"E:\freesw\bin\possub.py"
	subprocess.run(['python', possub_path], check=True)

def get_active_window_process_name():
	hWnd = ctypes.windll.user32.GetForegroundWindow()
	pid = ctypes.c_ulong()
	ctypes.windll.user32.GetWindowThreadProcessId(hWnd, ctypes.byref(pid))
	process = psutil.Process(pid.value)
	return process.name()

def countdown(t):
	while t:
		mins, secs = divmod(t, 60)
		timer = '{:02d}:{:02d}'.format(mins, secs)
		print(timer, end="\r")
		time.sleep(1)
		t -= 1

def check_and_clear_log(filename):
    # Check if file exists
    if not os.path.isfile(filename):
        # If not, create it
        open(filename, 'w').close()
        print(f"The file {filename} was created.")
    else:
        # If it does, clear its contents
        open(filename, 'w').close()
        print(f"The contents of the file {filename} were cleared.")

def wait_for_load(logfile_path, search_text):
	if not os.path.isfile(logfile_path):
		raise FileNotFoundError(f"The {logfile_path} does not exist. Try again, perhaps {logfile_path} was not created yet.")

	with open(logfile_path, 'r') as file:
		lines = tail(file)
		for line in lines:
			print(line)
			if search_text in line:
				print("Loaded")
				break

def load_config_and_map(map):
	# Open the console
	keyboard.press('`')
	keyboard.release('`')
	time.sleep(0.25)

	# Execute the screenshot.cfg
	keyboard.type('exec screenshot.cfg')
	keyboard.press(Key.enter)
	keyboard.release(Key.enter)
	time.sleep(0.25)

	# Load the map with the _hrcs suffix
	keyboard.type(f'map {map}')
	keyboard.press(Key.enter)
	keyboard.release(Key.enter)
	time.sleep(0.25)

def normalize_position():
	# Jump to fix z axis
	keyboard.press(' ')
	time.sleep(0.25)
	keyboard.release(' ')
	time.sleep(3)

	# Open the console
	keyboard.press('`')
	keyboard.release('`')
	time.sleep(0.25)

	# Run the getpos command
	keyboard.type('getpos')
	keyboard.press(Key.enter)
	keyboard.release(Key.enter)
	time.sleep(0.25)

def check_if_process_running(process_name):
    '''Check if there is any running process that contains the given name process_name.'''
    for proc in psutil.process_iter(['name']):
        try:
            if process_name.lower() in proc.info['name'].lower():
                return True
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            pass
    return False;

# Get the current directory name
dir_name = os.path.basename(os.getcwd())

# Remove '_hrcs' from the end of the directory name if it exists
if dir_name.endswith('_hrcs'):
	map_name = dir_name[:-5]
else:
	map_name = dir_name



# Launch Garry's Mod
check_and_clear_log(r'E:\Steam\steamapps\common\GarrysMod\garrysmod\console.log')
subprocess.Popen(["E:\\Steam\\steamapps\\common\\GarrysMod\\bin\\win64\\gmod.exe", '-w', '2560', '-h', '1440', '-conclearlog', '-condebug', '-hideconsole'])
print("Waiting for Garry's Mod to load...")
wait_for_load(r'E:\Steam\steamapps\common\GarrysMod\garrysmod\console.log', 'Not playing a local game.')
countdown(5)  # Adjust this value as needed

keyboard = KeyboardController()

load_config_and_map(dir_name)

# Wait for the map to load
wait_for_load(r'E:\Steam\steamapps\common\GarrysMod\garrysmod\console.log', 'Redownloading all lightmaps')
countdown(5)  # Adjust this value as needed

normalize_position()

# Check the console.log file
with open(r'E:\Steam\steamapps\common\GarrysMod\garrysmod\console.log', 'r') as file:
	for line in file:
		if line.startswith('setpos'):
			gmod_setpos = line.strip()
			print(f"HRCS info_player_start position: {gmod_setpos}")
			break

# Remove all weapons
keyboard.type('RemoveAllWeapons')
keyboard.press(Key.enter)
keyboard.release(Key.enter)
time.sleep(0.25)

# Enable noclip
keyboard.type('noclip')
keyboard.press(Key.enter)
keyboard.release(Key.enter)
time.sleep(0.25)

# Close the console
keyboard.press('`')
keyboard.release('`')
time.sleep(0.25)

with open('output.txt', 'r') as file:
	screenshot_counter = 0
	total_screenshots = sum(1 for line in file if line.strip().startswith('setpos'))
	file.seek(0)  # Reset file pointer to the beginning

	for line in file:
		command = line.strip()
		if command == 'SUBTRACTED':
			command = 'quit'
			print("All screenshots have been taken. Quitting the game...")

		# Check if the currently focused window belongs to hl2.exe or gmod.exe
		while True:
			process_name = get_active_window_process_name()
			if process_name in ['hl2.exe', 'gmod.exe']:
				break
			print("Script is paused because hl2.exe or gmod.exe is not the currently focused program.")
			time.sleep(1)

		# Open the console
		keyboard.press('`')
		keyboard.release('`')
		time.sleep(0.25)

		# Type the command into the console
		keyboard.type(command)

		# Press Enter to execute the command
		keyboard.press(Key.enter)
		keyboard.release(Key.enter)
		time.sleep(0.25)
		
		if command == 'quit':
			break
			
		# Close the console
		keyboard.press('`')
		keyboard.release('`')
		time.sleep(0.25)

		if command.startswith('setpos'):
			screenshot_counter += 1
			print(f"Taking screenshot {screenshot_counter}/{total_screenshots}...")

		# Wait 5 seconds
		print("Waiting for 5 seconds before taking a screenshot...")
		countdown(5)

		# Press F5 to take a screenshot
		keyboard.press(Key.f5)
		keyboard.release(Key.f5)
		time.sleep(0.25)

# Split the setpos and setang commands
gmod_setpos_command, _ = gmod_setpos.split(';')

# Extract the numbers from the setpos command
gmod_setpos_nums = [float(num) for num in gmod_setpos_command.split()[1:]]

while check_if_process_running('gmod.exe'):
    print("Waiting for Garry's Mod to close")
    time.sleep(1)

time.sleep(1)



#Launch Half-Life 2
check_and_clear_log(r'E:\Steam\steamapps\common\Half-Life 2\hl2\console.log')
subprocess.Popen(["E:\\Steam\\steamapps\\common\\Half-Life 2\\hl2.exe", '-novid', '-conclearlog', '-condebug'])
print("Waiting for Half-Life 2 to load...")
wait_for_load(r'E:\Steam\steamapps\common\Half-Life 2\hl2\console.log', 'Redownloading all lightmaps')
countdown(5)  # Adjust this value as needed

load_config_and_map(map_name)

print(f"Waiting for {map_name} to load...")
wait_for_load(r'E:\Steam\steamapps\common\Half-Life 2\hl2\console.log', 'Redownloading all lightmaps')
countdown(5)  # Adjust this value as needed

normalize_position()

# Check the console.log file
with open(r'E:\Steam\steamapps\common\Half-Life 2\hl2\console.log', 'r') as file:
	for line in file:
		if line.startswith('setpos'):
			hl2_setpos = line.strip()
			print(f"Half-Life 2 {map_name} info_player_start position: {hl2_setpos}")
			break

# Do the same for the hl2_setpos line
hl2_setpos_command, _ = hl2_setpos.split(';')
hl2_setpos_nums = [float(num) for num in hl2_setpos_command.split()[1:]]

# Calculate the differences
diffs = [g - h for g, h in zip(gmod_setpos_nums, hl2_setpos_nums)]

# If the absolute difference is less than 2, consider the setpos values to be the same
if all(abs(d) < 2 for d in diffs):
	filename = 'output.txt'
else:
	print(f"Half-Life 2 {map_name} info_player_start position differs from the HRCS map!!!")
	# Apply the offset to each setpos line in output.txt and write to output_hl2.txt
	with open('output.txt', 'r') as infile, open('output_hl2.txt', 'w') as outfile:
		for line in infile:
			if line.startswith('setpos'):
				setpos_part, setang_part = line.split(';')  # Split the line at the semicolon
				nums = [float(num) for num in setpos_part.split()[1:]]  # Only consider the setpos numbers
				nums = [n + d for n, d in zip(nums, diffs)]
				outfile.write('setpos ' + ' '.join(map(str, nums)) + ';' + setang_part)  # Keep the rest of the line unchanged
			else:
				outfile.write(line)
	filename = 'output_hl2.txt'

# Enable noclip
keyboard.type('noclip')
keyboard.press(Key.enter)
keyboard.release(Key.enter)
time.sleep(0.25)

# Close the console
keyboard.press('`')
keyboard.release('`')
time.sleep(0.25)

mouse = MouseController()

# Select weapon bucket 1
keyboard.press('1')
keyboard.release('1')
time.sleep(0.25)
# Select crowbar/super physcannon from weapon bucket 1
mouse.click(Button.left, 1)

# Check if 'output_hl2.txt' exists in the current directory
if os.path.exists('output_hl2.txt'):
	filename = 'output_hl2.txt'
else:
	filename = 'output.txt'

# Open the file and execute each command
with open(filename, 'r') as file:
	screenshot_counter = 0
	total_screenshots = sum(1 for line in file if line.strip().startswith('setpos'))
	file.seek(0)  # Reset file pointer to the beginning

	for line in file:
		command = line.strip()
		if command == 'SUBTRACTED':
			command = 'quit'
			print("All screenshots have been taken. Quitting the game...")

		# Check if the currently focused window belongs to hl2.exe or gmod.exe
		while True:
			process_name = get_active_window_process_name()
			if process_name in ['hl2.exe', 'gmod.exe']:
				break
			print("Script is paused because hl2.exe or gmod.exe is not the currently focused program.")
			time.sleep(1)

		# Open the console
		keyboard.press('`')
		keyboard.release('`')
		time.sleep(0.25)

		# Type the command into the console
		keyboard.type(command)

		# Press Enter to execute the command
		keyboard.press(Key.enter)
		keyboard.release(Key.enter)
		time.sleep(0.25)

		if command == 'quit':
			break
			
		# Close the console
		keyboard.press('`')
		keyboard.release('`')
		time.sleep(0.25)

		if command.startswith('setpos'):
			screenshot_counter += 1
			print(f"Taking screenshot {screenshot_counter}/{total_screenshots}...")

		# Wait 5 seconds
		print("Waiting for 5 seconds before taking a screenshot...")
		countdown(5)

		# Press F5 to take a screenshot
		keyboard.press(Key.f5)
		keyboard.release(Key.f5)
		time.sleep(0.25)

while check_if_process_running('hl2.exe'):
    print("Waiting for Half-Life 2 to close")
    time.sleep(1)

time.sleep(1)



# Launch Half-Life 2: Update
check_and_clear_log(r'E:\Steam\steamapps\common\Half-Life 2 Update\hl2\console.log')
subprocess.Popen(["E:\\Steam\\steamapps\\common\\Half-Life 2 Update\\hl2.exe", '-novid', '-conclearlog', '-condebug'])
print("Waiting for Half-Life 2: Update to load...")
wait_for_load(r'E:\Steam\steamapps\common\Half-Life 2 Update\hl2\console.log', 'Redownloading all lightmaps')
countdown(5)  # Adjust this value as needed

load_config_and_map(map_name)

# Wait for the map to load
print(f"Waiting for {map_name} to load...")
wait_for_load(r'E:\Steam\steamapps\common\Half-Life 2 Update\hl2\console.log', 'Redownloading all lightmaps')
countdown(5)  # Adjust this value as needed

normalize_position()

# Monitor the console.log file
with open(r'E:\Steam\steamapps\common\Half-Life 2 Update\hl2\console.log', 'r') as file:
	for line in file:
		if line.startswith('setpos'):
			hl2u_setpos = line.strip()
			print(f"Half-Life 2: Update {map_name} info_player_start position: {hl2u_setpos}")
			break

# Do the same for the hl2u_setpos line
hl2u_setpos_command, _ = hl2u_setpos.split(';')
hl2u_setpos_nums = [float(num) for num in hl2u_setpos_command.split()[1:]]

# Calculate the differences
diffs = [g - h for g, h in zip(gmod_setpos_nums, hl2u_setpos_nums)]

# If the absolute difference is less than 2, consider the setpos values to be the same
if all(abs(d) < 2 for d in diffs):
	filename = 'output.txt'
else:
	print(f"Half-Life 2: Update {map_name} info_player_start position differs from the HRCS map!!!")
	# Apply the offset to each setpos line in output.txt and write to output_hl2u.txt
	with open('output.txt', 'r') as infile, open('output_hl2u.txt', 'w') as outfile:
		for line in infile:
			if line.startswith('setpos'):
				setpos_part, setang_part = line.split(';')  # Split the line at the semicolon
				nums = [float(num) for num in setpos_part.split()[1:]]  # Only consider the setpos numbers
				nums = [n - d for n, d in zip(nums, diffs)]  # Subtract the difference
				outfile.write('setpos ' + ' '.join(map(str, nums)) + ';' + setang_part)  # Keep the rest of the line unchanged
			else:
				outfile.write(line)
	filename = 'output_hl2u.txt'

# Enable noclip
keyboard.type('noclip')
keyboard.press(Key.enter)
keyboard.release(Key.enter)
time.sleep(0.25)

# Close the console
keyboard.press('`')
keyboard.release('`')
time.sleep(0.25)

# Select weapon bucket 1
keyboard.press('1')
keyboard.release('1')
time.sleep(0.25)
# Select crowbar/super physcannon from weapon bucket 1
mouse.click(Button.left, 1)

# Check if 'output_hl2u.txt' exists in the current directory
if os.path.exists('output_hl2u.txt'):
	filename = 'output_hl2u.txt'
else:
	filename = 'output.txt'

# Open the file and execute each command
with open(filename, 'r') as file:
	screenshot_counter = 0
	total_screenshots = sum(1 for line in file if line.strip().startswith('setpos'))
	file.seek(0)  # Reset file pointer to the beginning

	for line in file:
		command = line.strip()
		if command == 'SUBTRACTED':
			command = 'quit'
			print("All screenshots have been taken. Quitting the game...")

		# Check if the currently focused window belongs to hl2.exe or gmod.exe
		while True:
			process_name = get_active_window_process_name()
			if process_name in ['hl2.exe', 'gmod.exe']:
				break
			print("Script is paused because hl2.exe or gmod.exe is not the currently focused program.")
			time.sleep(1)

		# Open the console
		keyboard.press('`')
		keyboard.release('`')
		time.sleep(0.25)

		# Type the command into the console
		keyboard.type(command)

		# Press Enter to execute the command
		keyboard.press(Key.enter)
		keyboard.release(Key.enter)
		time.sleep(0.25)

		if command == 'quit':
			break
			
		# Close the console
		keyboard.press('`')
		keyboard.release('`')
		time.sleep(0.25)

		if command.startswith('setpos'):
			screenshot_counter += 1
			print(f"Taking screenshot {screenshot_counter}/{total_screenshots}...")

		# Wait 5 seconds
		print("Waiting for 5 seconds before taking a screenshot...")
		countdown(5)

		# Press F5 to take a screenshot
		keyboard.press(Key.f5)
		keyboard.release(Key.f5)
		time.sleep(0.25)

while check_if_process_running('hl2.exe'):
    print("Waiting for Half-Life 2: Update to close")
    time.sleep(1)

time.sleep(1)



# Launch Garry's Mod for thumbnail screenshot
print("Launching Garry's Mod for thumbnail screenshot")
subprocess.Popen(["E:\\Steam\\steamapps\\common\\GarrysMod\\bin\\win64\\gmod.exe", '-w', '1440', '-h', '1440', '+map', dir_name])
