import os

class Node:
    def __init__(self, name):
        self.name = name
        self.properties = {}
        self.children = []

def parse_vmf(vmf_string):
    lines = vmf_string.split('\n')
    root = Node('root')
    stack = [root]

    for line in lines:
        line = line.strip()
        if line.startswith('{'):
            continue
        elif line.startswith('}'):
            stack.pop()
        elif '"' in line:
            key, value = line.replace('"', '').split(' ', 1)
            stack[-1].properties[key] = value
        else:
            new_node = Node(line)
            stack[-1].children.append(new_node)
            stack.append(new_node)

    return root

def move_solids_to_world(root):
    world_node = None
    for child in root.children:
        if child.name == 'world':
            world_node = child
            break

    if world_node is None:
        return

    for child in root.children:
        if child.name == 'entity' and child.properties.get('vrad_brush_cast_shadows') == '1':
            solids = [grandchild for grandchild in child.children if grandchild.name == 'solid']
            world_node.children.extend(solids)

def write_node_to_vmf(node, f, indent=0):
    if node is not None:
        f.write('\t' * indent + node.name + '\n')
        f.write('\t' * indent + '{\n')
        for key, value in node.properties.items():
            f.write('\t' * (indent + 1) + f'"{key}" "{value}"\n')
        for child in node.children:
            write_node_to_vmf(child, f, indent + 1)
        f.write('\t' * indent + '}\n')

def filter_nodes(node, materials):
    if node.name == 'entity':
        # Keep only 'solid' children of the entity that have at least one 'side' with a material in the list
        # or if the entity has "classname" "func_detail"
        node.children = [child for child in node.children if child.name == 'solid' and any(grandchild.name == 'side' and grandchild.properties.get('material') in materials for grandchild in child.children)]
    new_node = Node(node.name)
    new_node.properties = node.properties.copy()
    for child in node.children:
        new_child = filter_nodes(child, materials)
        if new_child is not None:
            new_node.children.append(new_child)
    return new_node

def validate_and_clean_world_node(node, materials):
    valid_solids = []
    for child in node.children:
        if child.name == 'solid' and any(grandchild.name == 'side' and grandchild.properties.get('material') in materials for grandchild in child.children):
            valid_solids.append(child)
    node.children = valid_solids

def convert_func_detail_to_world(root):
    world_node = None
    for child in root.children:
        if child.name == 'world':
            world_node = child
        elif child.name == 'entity' and child.properties.get('classname') == 'func_detail':
            world_node.children.extend([grandchild for grandchild in child.children if grandchild.name == 'solid'])
            child.children = [grandchild for grandchild in child.children if grandchild.name != 'solid']
    return world_node  # Return the world_node

# Get the current folder name
folder_name = os.path.basename(os.getcwd())

# Construct the input and output file paths
input_file_path = os.path.join('mapsrc', f'{folder_name}.vmf')
output_file_path = os.path.join('mapsrc', f'{folder_name}_model.vmf')

# Usage
# Read from the input file
with open(input_file_path, 'r') as f:
    content = f.read()

with open('E:\\freesw\\bin\\transparent_vmts.txt', 'r') as f:
    materials = [line.strip() for line in f]

root = parse_vmf(content)

# Convert func_detail brush entity solids into world solids and get the world_node
world_node = convert_func_detail_to_world(root)

# Move solids to world and filter nodes based on the materials
move_solids_to_world(root)
filtered_root = filter_nodes(world_node, materials)

# Validate and clean the world node
validate_and_clean_world_node(filtered_root, materials)

# Write only the world node to the VMF file
with open(output_file_path, 'w') as f:
    if filtered_root is not None:
        write_node_to_vmf(filtered_root, f, 0)
