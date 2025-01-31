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
                    phyla_match = re.search(r'p__([^;]+)', label)
                    domain_match = re.search(r'd__([^;]+)', label)

                    phyla = phyla_match.group(1) if phyla_match else ""
                    domain = domain_match.group(1) if domain_match else ""

                    new_block = []
                    for node_line in node_block:
                        if "label" in node_line:
                            new_block.append(f'    label "{phyla}"\n')
                            new_block.append(f'    domain "{domain}"\n')
                        else:
                            new_block.append(node_line)

                    outfile.writelines(new_block)
                else:
                    outfile.writelines(node_block)
            elif in_node:
                node_block.append(line)
            else:
                outfile.write(line)

input_file = 'gg-sparcc-phyla-exported-network/network.gml'
output_file = 'gg-sparcc-phyla-exported-network/gg-sparcc-phyla-modified_network.gml'
modify_gml(input_file, output_file)
