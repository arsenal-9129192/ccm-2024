import csv

metadata_file = "metadata_backup.tsv"

single_manifest = "single_manifest.tsv"
paired_manifest = "paired_manifest.tsv"

with open(single_manifest, 'w', newline='') as single_out, open(paired_manifest, 'w', newline='') as paired_out:
    single_writer = csv.writer(single_out, delimiter='\t')
    paired_writer = csv.writer(paired_out, delimiter='\t')
    
    single_writer.writerow(['sample-id', 'absolute-filepath'])
    paired_writer.writerow(['sample-id', 'forward-absolute-filepath', 'reverse-absolute-filepath'])
    
    with open(metadata_file, 'r', encoding='utf-8') as file:
        reader = csv.DictReader(file, delimiter='\t')
        for row in reader:
            if row['type'] == 'single-end':
                single_writer.writerow([row['sample-id'], row['absolute-filepath']])
            elif row['type'] == 'paired-end':
                paired_writer.writerow([row['sample-id'], row['forward-absolute-filepath'], row['reverse-absolute-filepath']])

print("Manifestos gerados com sucesso!")
