import os
import subprocess
import zipfile
import vpk

# Define paths
vbsp_path = r"E:\Steam\steamapps\common\GarrysMod\bin\win64\vbsp.exe"
gmod_path = r"E:\Steam\steamapps\common\GarrysMod\garrysmod"
vpk_path = r"E:\Steam\steamapps\common\GarrysMod\sourceengine\hl2_misc_dir.vpk"

# Get current directory and parent directory name
current_dir = os.getcwd()
parent_dir_name = os.path.basename(os.path.dirname(current_dir))

# Construct .vmf and .bsp file paths
vmf_file = os.path.join(current_dir, parent_dir_name + ".vmf")
bsp_file = os.path.join(current_dir, parent_dir_name + ".bsp")

# Run vbsp.exe with the .vmf file as a parameter
vbsp_output = subprocess.check_output([vbsp_path, vmf_file])

# Check if "Patching WVT material" is in the output
if b"Patching WVT material" in vbsp_output:
	# Extract all the wvt patches from the .bsp file
	extracted_files = []
	with zipfile.ZipFile(bsp_file, 'r') as z:
		for name in z.namelist():
			if name.endswith('_wvt_patch.vmt'):
				z.extract(name, path=gmod_path)
				extracted_files.append(name)

	# Open the VPK file
	with vpk.open(vpk_path) as pak1:
		# Find the non-patched VMT file and place it in the same folder as the patched version
		for extracted_file in extracted_files:
			non_patched_file = 'materials' + extracted_file.split(parent_dir_name)[1].replace('_wvt_patch', '')
			# print(f"Looking for {non_patched_file} in the VPK file...")
			if non_patched_file in pak1:
				with pak1.get_file(non_patched_file) as f:
					data = f.read()
				destination_path = os.path.join(gmod_path, extracted_file)
				with open(destination_path, 'wb') as f:
					f.write(data)
				print(f"Extracted {non_patched_file} to {destination_path}")
