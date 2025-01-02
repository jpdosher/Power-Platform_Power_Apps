#made by @jean-paul-dosher
#visit: https://medium.com/@jean.dosher

import re
from collections import defaultdict
from Control_prefixes import control_prefixes

def refactor_yaml(yaml_content):
    screen_name = get_screen_name(yaml_content)
    if screen_name is None:
        print("Unable to refactor: Screen name not found")
        return yaml_content  

    lines = yaml_content.split('\n')
    refactored_lines = []
    control_counters = defaultdict(int)  # for control name generation (if needed)
    control_name_map = {}  # to store old to new control name mapping

    for i, line in enumerate(lines):
        if re.search(r'\w+_\d+ As \w+(\.\w+)?:', line):
            indentation = len(line) - len(line.lstrip())
            control_name, control_type = line.strip().split(" As ")  # Extract control name and type
            control_type = control_type.strip().rstrip(':')  # Remove trailing whitespace and colon
            

            # Only refactor if the control name ends with _\d+ or '_Unknown'
            if re.search(r'_\d+$', control_name) or '_Unknown' in control_name:
                # Get the container name without any suffixes
                container_name = get_container_name(indentation, lines, i)
                # Ensure we only keep the relevant part of the container name
                container_name = container_name.split('_')[0]  # Keep only the first part

                # Get control properties
                control_props = {}
                j = i + 1
                while j < len(lines) and lines[j].startswith(' ' * (indentation + 4)):
                    stripped_line = lines[j].strip()
                    if ': ' in stripped_line:
                        prop, value = stripped_line.split(": ", 1)
                        control_props[prop] = value
                    j += 1

                context_purpose = get_context_purpose(control_props)

                # Use the extracted control type to get the prefix
                control_type_prefix = control_prefixes.get(control_type.lower(), control_type.lower()[:3])  # Use the dictionary to get the prefix
                context = re.sub(r'[^a-zA-Z0-9]', '', context_purpose)[:10]

                # Generate the new name without the counter initially
                new_name = f"{control_type_prefix}_{context}_{container_name}_{screen_name}"
                
                # Check if the new name already exists in the control_name_map
                if new_name in control_name_map.values():
                    control_counters[control_type] += 1  # Increment the counter if the name exists
                    new_name = f"{new_name}_{control_counters[control_type]}"  # Append the counter

                control_name_map[control_name] = new_name
                refactored_lines.append(line.replace(control_name, new_name))
            else:
                refactored_lines.append(line)
        else:
            # Check for references to other controls in properties
            for old_name, new_name in control_name_map.items():
                if old_name in line:
                    line = re.sub(r'\b' + re.escape(old_name) + r'\b', new_name, line)
            refactored_lines.append(line)

    refactored_content = '\n'.join(refactored_lines)

 
    return refactored_content

# Updated get_screen_name function
def get_screen_name(yaml_content):
    pattern = r"(?:['\"](.*?)['\"]\s+As\s+screen|(\w+)\s+As\s+screen)" #Updated pattern to ensure quotes are included in the screen name---PLEASE CHANGE THIS
    match = re.search(pattern, yaml_content)
    if match:
        # The screen name will be in either group 1 or group 2
        screen_name = match.group(1) or match.group(2)
        # Ensure the screen name is returned with quotes
        if match.group(1):
            screen_name = f"'{screen_name}'"  # Add quotes if it was found in group 1
        print(f"Screen name found: {screen_name}")
        return screen_name
    else:
        print("Screen name not found in YAML content")
        return None

def get_container_name(indentation, lines, current_index):
    for i in range(current_index - 1, -1, -1):
        line = lines[i].strip()
        if " As " in line and any(container_type in line for container_type in ["group", "groupContainer", "container"]):
            # Extract the container name and remove the prefix (e.g., "grp_")
            full_container_name = line.split(" As ")[0]
            # Return only the part after the first underscore
            return full_container_name.split('_', 1)[-1]  # Keep only the part after the first underscore
    return "Unknown"

def get_context_purpose(control_props):
    return control_props.get("Icon", control_props.get("Text", control_props.get("Tooltip", "Unknown")))

def refactor_control_name(old_name, control_type, context_purpose, container_name, screen_name, control_counters):
    control_type_prefix = control_prefixes.get(control_type.lower(), control_type.lower()[:3])  # Use the dictionary to get the prefix
    context = re.sub(r'[^a-zA-Z0-9]', '', context_purpose)[:10]
    control_counters[control_type] += 1
    return f"{control_type_prefix}_{context}_{container_name}_{screen_name}_{control_counters[control_type]}" #New name

# Main execution
if __name__ == "__main__":
    # Ask the user for the input filename
    input_filename = input("Enter the name of the YAML file to refactor: ")

    # Read the YAML file
    try:
        with open(input_filename, 'r', encoding='utf-8') as file:
            yaml_content = file.read()
    except FileNotFoundError:
        print(f"Error: The file '{input_filename}' was not found.")
        exit(1)
    except IOError:
        print(f"Error: Unable to read the file '{input_filename}'.")
        exit(1)

    # Refactor the YAML content

    refactored_yaml = refactor_yaml(yaml_content)

    # Write the refactored YAML to a new file
    output_filename = f"refactored_{input_filename}"
    with open(output_filename, 'w', encoding='utf-8') as file:
        file.write(refactored_yaml)

    print(f"Refactoring complete. Check '{output_filename}' for the result.")

    # Close confirmation
    input("Press Enter to close the program...")
