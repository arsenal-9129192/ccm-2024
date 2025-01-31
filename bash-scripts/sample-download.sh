#!/bin/bash

study_ids=(
    "SRP384575"
    "SRP235164"
    "SRP151359"
    "SRP150263"
    "SRP058179"
    "SRP119389"
    "SRP468627"
    "SRP397764"
    "SRP126731"
    "SRP126921"
    "SRP390541"
    "SRP431342"
)

#sra download
for study_id in "${study_ids[@]}"; do
    prefetch "$study_id"
    #fastq conversion
    fastq-dump --split-files --gzip --outdir ./fastq_files "$study_id"
done

find . -name "*.sra" | while read sra_file; do
    base_name=$(basename "$sra_file" .sra)
    
    fastq-dump --split-files --gzip "$sra_file"
    
    mv "${base_name}_1.fastq.gz" .
    mv "${base_name}_2.fastq.gz" .
done
