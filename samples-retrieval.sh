#!/bin/bash

mkdir -p logs

echo "Iniciando downloads..."

# tsv metadata header 
echo -e "sample-id\tstudy-id\tauthor\tsample-name\tcondition1\tcondition2\tcondition3\tmix1\tmix2\ttype\tabsolute-filepath\tforward-absolute-filepath\treverse-absolute-filepath" > metadata.tsv
head -n 1 biogas-metadata.csv > failed_runs.csv

while IFS=';' read -r run_id study author sample cond1 cond2 cond3 mix1 mix2 type abs fwd rev || [ -n "$run_id" ]; do
    if [[ $run_id == "sample-id" ]]; then
        continue
    fi
    
    echo -e "\n=== processing $run_id (author: $author) ==="
    
    mkdir -p "$author"
    cd "$author"
    
    echo "Executando fastq-dump para $run_id..."
    if ! fastq-dump --split-files --gzip "$run_id" 2>/dev/null; then
        echo "ERROR: failed $run_id"
        cd ..
        echo "$run_id;$study;$author;$sample;$cond1;$cond2;$cond3;$mix1;$mix2;$type;$abs;$fwd;$rev" >> failed_runs.csv
        continue
    fi
    
    # _1 and _2 (paired-end) check
    if [ -f "${run_id}_1.fastq.gz" ] && [ -f "${run_id}_2.fastq.gz" ]; then
        echo "finished download: paired-end"
        abs_path=""
        fwd_path="$(pwd)/${run_id}_1.fastq.gz"
        rev_path="$(pwd)/${run_id}_2.fastq.gz"
        run_type="PAIRED-END"
    
    # _1 (single-end) check
    elif [ -f "${run_id}_1.fastq.gz" ] && [ ! -f "${run_id}_2.fastq.gz" ]; then
        echo "finished download: single-end _1"
        abs_path="$(pwd)/${run_id}_1.fastq.gz"
        fwd_path=""
        rev_path=""
        run_type="SINGLE-END"
    
    # single-end no suffix check
    elif [ -f "${run_id}.fastq.gz" ]; then
        echo "finished download: single-end no suffix"
        abs_path="$(pwd)/${run_id}.fastq.gz"
        fwd_path=""
        rev_path=""
        run_type="SINGLE-END"
    
    else
        echo "no downloadable file"
        cd ..
        echo "$run_id;$study;$author;$sample;$cond1;$cond2;$cond3;$mix1;$mix2;$type;$abs;$fwd;$rev" >> failed_runs.csv
        continue
    fi
    
    cd ..
    
    echo -e "${run_id}\t${study}\t${author}\t${sample}\t${cond1}\t${cond2}\t${cond3}\t${mix1}\t${mix2}\t${run_type}\t${abs_path}\t${fwd_path}\t${rev_path}" >> metadata.tsv
    
    echo "sample $run_id processed"
    
done < biogas-metadata.csv

echo -e "\nfinished!"
echo "failed_runs.csv generayed"
echo "update metadata metadata.tsv"
