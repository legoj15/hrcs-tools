import os
import shutil
import sys
import stat
import subprocess
import re

def read_file(filename):
	with open(filename, 'r') as file:
		content = file.read()
	return content.split('\n')

def write_file(output_filename, lines):
	with open(output_filename, 'w') as file:
		for line in lines:
			file.write(line + '\n')

def process_prop_detail(line, inside_entity, prop_detail_count):
	stripped = line.strip()
	if stripped == '"classname" "prop_detail"':
		inside_entity = True
		line = line.replace('prop_detail', 'prop_static')
		line += '\n    "solid" "0"'
		prop_detail_count += 1
	return line, inside_entity, prop_detail_count

def process_env_cubemap(line, inside_cubemap, cubemapsize_exists, cubemap_count):
	stripped = line.strip()
	if inside_cubemap and stripped.startswith('"cubemapsize"'):
		cubemapsize_exists = True
		line = '    "cubemapsize" "9"\n'
		cubemap_count += 1
	elif inside_cubemap and stripped.startswith('"origin"') and not cubemapsize_exists:
		line = '    "cubemapsize" "9"\n' + line
		cubemapsize_exists = True
		cubemap_count += 1
	return line, inside_cubemap, cubemapsize_exists, cubemap_count

def process_trigger_changelevel(line, inside_entity, trigger_changelevel_count, map_names):
	stripped = line.strip()
	if stripped == '"classname" "trigger_changelevel"':
		inside_entity = True
	elif inside_entity and stripped.startswith('"map"'):
		map_name = stripped.split('"')[3]
		line = line.replace(map_name, map_name + '_hrcs')
		trigger_changelevel_count += 1
		map_names.append(map_name + '_hrcs')
	return line, inside_entity, trigger_changelevel_count, map_names

def process_env_fog_controller(lines, farz_values):
	inside_fog_controller = False
	for i, line in enumerate(lines):
		stripped = line.strip()
		if stripped == '"classname" "env_fog_controller"':
			inside_fog_controller = True
		elif inside_fog_controller and stripped.startswith('"farz"'):
			farz_values.append(stripped.split('"')[3])
			lines[i] = ''
		elif stripped == '}':
			inside_fog_controller = False
	return lines, farz_values

def convert_func_lod(input_filename, output_filename):
    with open(input_filename, 'r') as file:
        data = file.read()

    entities = data.split('entity')
    named_func_lods = []
    non_solid_func_lods = 0
    total_func_lods = 0
    for i, entity in enumerate(entities[1:], start=1):  # Skip the first split part
        if '"classname" "func_lod"' in entity:
            total_func_lods += 1
            if 'targetname' in entity:
                named_func_lods.append(re.search(r'"targetname"\s*"(.+?)"', entity).group(1))
                continue
            if re.search(r'"Solid"\s*"1"', entity):
                non_solid_func_lods += 1
                entities[i] = entity.replace('"classname" "func_lod"', '"classname" "func_brush"')
                entities[i] = re.sub(r'"Solid"\s*"1"', '"Solidity" "1"', entities[i])
            else:
                entities[i] = entity.replace('"classname" "func_lod"', '"classname" "func_detail"')
                entities[i] = re.sub(r'"Solid"\s*".*?"', '', entities[i])  # Remove "Solid" field
                entities[i] = re.sub(r'"gmod_.*?"\s*".*?"', '', entities[i])  # Remove "gmod_" fields
            entities[i] = re.sub(r'"DisappearDist"\s*".*?"', '', entities[i])  # Remove "DisappearDist" field

    with open(output_filename, 'w') as file:
        file.write('entity'.join(entities))

    print(f"Total func_lod entities: {total_func_lods}")
    print(f"Unnamed non-solid func_lod entities: {non_solid_func_lods}")
    if named_func_lods:
        print(f"Named func_lod entities: {len(named_func_lods)}")
        print(f"Names of the named func_lod entities: {named_func_lods}")
    else:
        # Only modify the HRCS checklisk.txt file if no named func_lods were encountered
        with open('HRCS checklisk.txt', 'r') as file:
            lines = file.readlines()

        # Remove the line "convert func_lod to func_detail" from the txt file
        lines = [line for line in lines if line.strip() != "convert func_lod to func_detail"]

        # Write the modified lines back to the file
        with open('HRCS checklisk.txt', 'w') as file:
            file.writelines(lines)

def remove_func_occluder(filename):
	with open(filename, 'r+') as file:
		content = file.read()
		pattern = r'entity\s*\{[^}]*"classname" "func_occluder".*?(?=entity|cameras)'
		matches = re.findall(pattern, content, flags=re.DOTALL)
		content = re.sub(pattern, '', content, flags=re.DOTALL)
		file.seek(0)
		file.write(content)
		file.truncate()
	return len(matches)

def convert_func_wall(input_filename, output_filename):
	with open(input_filename, 'r') as file:
		data = file.read()

	entities = data.split('entity')
	total_func_walls = 0
	for i, entity in enumerate(entities[1:], start=1):  # Skip the first split part
		if '"classname" "func_wall"' in entity:
			total_func_walls += 1
			entities[i] = entity.replace('"classname" "func_wall"', '"classname" "func_brush"')

	with open(output_filename, 'w') as file:
		file.write('entity'.join(entities))

	print(f"Total func_wall entities converted to func_brush: {total_func_walls}")

def find_func_areaportalwindow_and_target(content):
    # Join the list of lines into a single string
    content = '\n'.join(content)
    
    pattern = r'(entity\s*\{[^}]*"classname" "func_areaportalwindow"(.*?))("target" "([^"]*)")([^}]*\})'
    matches = re.findall(pattern, content, flags=re.DOTALL)
    print(f"Found {len(matches)} func_areaportalwindow entities.")
    
    # Flag to track if any conversion was skipped
    conversion_skipped = False
    for match in matches:
        entity, pre_target, target, target_value, post_target = match
        # Check if BackgroundBModel field exists
        if 'BackgroundBModel' in entity:
            print(f"Skipped a func_areaportalwindow with a BackgroundBModel: {target_value}")
            conversion_skipped = True
            continue
        entity_pattern = r'entity\s*\{[^}]*"targetname" "' + re.escape(target_value) + '".*?(?=entity|cameras)'
        target_entities = re.findall(entity_pattern, content, flags=re.DOTALL)
        for target_entity in target_entities:
            classname_match = re.search(r'"classname" "([^"]*)"', target_entity)
            if classname_match:
                print(f"Found target entity with classname '{classname_match.group(1)}' and targetname '{target_value}'.")
            content = content.replace(target_entity, '')
    
    # Split the modified content back into a list of lines
    content = content.split('\n')

    # Only modify the HRCS checklisk.txt file if no conversion was skipped
    if not conversion_skipped:
        # Open the HRCS checklisk.txt file
        with open('HRCS checklisk.txt', 'r') as file:
            lines = file.readlines()

        # Remove the line "convert all areaportalwindow" from the txt file
        lines = [line for line in lines if line.strip() != "convert all areaportalwindow"]

        # Write the modified lines back to the file
        with open('HRCS checklisk.txt', 'w') as file:
            file.writelines(lines)

    return content
def convert_func_areaportalwindow(input_filename, output_filename):
    lines = read_file(input_filename)
    output_lines = []
    convert = False
    skip = False
    count = 0
    for line in lines:
        stripped = line.strip()
        if stripped == '"classname" "func_areaportalwindow"':
            convert = True
        elif convert and stripped.startswith('"BackgroundBModel"'):
            count += 1
            skip = True
        if convert and not skip:
            if stripped == '"classname" "func_areaportalwindow"':
                output_lines.append('\t"classname" "func_areaportal"')
            elif not (stripped.startswith('"FadeDist"') or stripped.startswith('"FadeStartDist"') or stripped.startswith('"TranslucencyLimit"') or stripped.startswith('"target"')):
                output_lines.append(line)
        else:
            output_lines.append(line)
        if stripped == "}":
            convert = False
            skip = False
    write_file(output_filename, output_lines)
    print(f'Total func_areaportalwindow entities with a BackgroundBModel field: {count}')

def update_vmf_file(filename, output_filename):
	print(f"Opening file: {filename}")
	lines = read_file(filename)
	inside_entity = False
	inside_cubemap = False
	cubemapsize_exists = False
	prop_detail_count = 0
	trigger_changelevel_count = 0
	map_names = []
	farz_values = []
	cubemap_count = 0
	for i, line in enumerate(lines):
		stripped = line.strip()
		line, inside_entity, prop_detail_count = process_prop_detail(line, inside_entity, prop_detail_count)
		if stripped == '"classname" "env_cubemap"':
			inside_entity = True
			inside_cubemap = True
			cubemapsize_exists = False
		line, inside_cubemap, cubemapsize_exists, cubemap_count = process_env_cubemap(line, inside_cubemap, cubemapsize_exists, cubemap_count)
		line, inside_entity, trigger_changelevel_count, map_names = process_trigger_changelevel(line, inside_entity, trigger_changelevel_count, map_names)
		if stripped == '}':
			inside_entity = False
			inside_cubemap = False
		lines[i] = line
	lines, farz_values = process_env_fog_controller(lines, farz_values)
	write_file(output_filename, lines)
	print(f"Converted {prop_detail_count} prop_detail entities into prop_static")
	print(f"Added _hrcs suffix to the map field of {trigger_changelevel_count} trigger_changelevel entities")
	for map_name in map_names:
		print(f"Map field now says: {map_name}")
	if farz_values:
		print(f"Found an env_fog_controller with a farz field set to: {', '.join(farz_values)}")
	print(f"Set cubemapsize to 9 for {cubemap_count} env_cubemaps")

# Usage:
current_folder = os.path.basename(os.getcwd())
filename = os.path.join("mapsrc", current_folder + ".vmf")
update_vmf_file(filename, filename)
convert_func_lod(filename, filename)
removed_func_occluders = remove_func_occluder(filename)
print(f"Removed {removed_func_occluders} func_occluder entities")
convert_func_wall(filename, filename)
content = read_file(filename)
content = find_func_areaportalwindow_and_target(content)
write_file(filename, content)
convert_func_areaportalwindow(filename, filename)
