import re

def modify_gml(input_file, output_file):
    with open(input_file, 'r') as infile, open(output_file, 'w') as outfile:
        node_block = []
        in_node = False

        for line in infile:
            stripped_line = line.strip()
            
            if stripped_line.startswith("node ["):
                in_node = True
                node_block = [line]
            elif stripped_line.startswith("]") and in_node:
                in_node = False
                node_block.append(line)

                node_content = "".join(node_block)
                match_label = re.search(r'label "(.*?)"', node_content)
                if match_label:
                    label = match_label.group(1)
                    genus_match = re.search(r'g__([^;]+)', label)
                    phyla_match = re.search(r'p__([^;]+)', label)
                    family_match = re.search(r'f__([^;]+)', label)

                    genus = genus_match.group(1) if genus_match else ""
                    phyla = phyla_match.group(1) if phyla_match else ""
                    family = family_match.group(1) if family_match else ""

                    new_block = []
                    for node_line in node_block:
                        if "label" in node_line:
                            new_block.append(f'    label "{genus}"\n')
                            new_block.append(f'    phyla "{phyla}"\n')
                            new_block.append(f'    family "{family}"\n')
                        else:
                            new_block.append(node_line)

                    outfile.writelines(new_block)
                else:
                    outfile.writelines(node_block)
            elif in_node:
                node_block.append(line)
            else:
                outfile.write(line)

input_file = 'genus-exported-network/network.gml'
output_file = 'genus-exported-network/modified_network.gml'
modify_gml(input_file, output_file)
