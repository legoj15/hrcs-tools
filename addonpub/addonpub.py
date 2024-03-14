import os
import subprocess
import sys
import shutil
import webbrowser
import re

def run_gmad_and_gmpublish():
    # Get the current directory name as the folder name
    folder_name = os.path.basename(os.getcwd())

    # Hardcoded path to the GarrysMod directory
    gmod_path = "E:\\Steam\\steamapps\\common\\GarrysMod\\"

    # Hardcoded path to the bin\win64 directory
    bin_path = gmod_path + "bin\\win64"

    # Full paths to the gmad.exe and gmpublish.exe files
    gmad_path = os.path.join(bin_path, "gmad.exe")
    gmpublish_path = os.path.join(bin_path, "gmpublish.exe")

    # Check if the <foldername>.jpeg file exists
    jpeg_path = os.path.join(gmod_path, f"{folder_name}_thumb.jpg")
    if not os.path.isfile(jpeg_path):
        # Check in the screenshots directory
        jpeg_path = os.path.join("screenshots", f"{folder_name}_thumb.jpg")
        if not os.path.isfile(jpeg_path):
            # Check in the \screenshots\gmod directory
            jpeg_path = os.path.join("screenshots\\gmod", f"{folder_name}_thumb.jpg")
            if not os.path.isfile(jpeg_path):
                sys.exit(f"Error: {foldername}_thumb.jpg file does not exist. Please check the existence of the file.")

    # Move the file to the GarrysMod directory
    shutil.move(jpeg_path, gmod_path)

    # Parameters for the gmad.exe and gmpublish.exe commands
    gmad_params = [gmad_path, os.path.join(gmod_path, folder_name)]
    gmpublish_params = [gmpublish_path, "create", "-icon", os.path.join(gmod_path, f"{folder_name}_thumb.jpg"), "-addon", os.path.join(gmod_path, f"{folder_name}.gma")]

    # Run gmad.exe and wait for it to complete
    subprocess.run(gmad_params, check=True)

    # Run gmpublish.exe and capture its output
    gmpublish_output = subprocess.check_output(gmpublish_params).decode('utf-8')
    print(gmpublish_output)

    # Extract the URL from the output and open it in the browser
    url_match = re.search(r'(http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+)', gmpublish_output)
    if url_match:
        webbrowser.open(url_match.group(0))

run_gmad_and_gmpublish()
