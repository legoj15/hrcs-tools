import os

# Get the current directory name
current_dir = os.path.basename(os.getcwd())

# Define the entity to be added
map_model = """
entity
{{
	"classname" "prop_static"
	"angles" "0 270 0"
	"disablevertexlighting" "1"
	"model" "models/legoj15/maps/{0}/{0}_model.mdl"
	"skin" "1"
	"solid" "0"
	"origin" "0 0 0"
}}
""".format(current_dir)

# Open the .vmf file in the mapsrc subdirectory
with open(os.path.join('mapsrc', current_dir + '.vmf'), 'a') as file:
    # Append the translucent map model to the end of the file
    file.write(map_model)
