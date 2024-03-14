def adjust_file(input_file, output_file):
    marker = 'SUBTRACTED'
    with open(input_file, 'r') as f_in:
        lines = f_in.readlines()
        # Check if the marker is in the file
        if any(marker in line for line in lines):
            print(f"The file {input_file} has already been subtracted.")
            return
        # Remove empty lines from anywhere in the file
        lines = [line for line in lines if line.strip() != '']
        with open(output_file, 'w') as f_out:
            for line in lines:
                parts = line.split()
                if len(parts) >= 4 and parts[0] == 'setpos':
                    # Split the third part into number and remaining string
                    number, remaining = parts[3].split(';')
                    # Subtract 64 from the number part
                    number = str(float(number) - 64)
                    # Join them back together
                    parts[3] = ';'.join([number, remaining])
                f_out.write(' '.join(parts) + '\n')
            # Add the marker to the end of the file
            f_out.write(marker + '\n')

# Call the function with your input and output file paths
adjust_file('new 1.txt', 'output.txt')
