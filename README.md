# Microbial communities diversity analysis in microbial fuel cells

## Overview
Study analyzing 227 samples from 30 MFC experiments using 16S rRNA amplicon sequencing to understand microbial community composition, functional pathways, and performance in wastewater treatment and bioenergy generation.

## Key findings
- Dominant phyla: _Pseudomonadota_ (13.45%), _Bacteroidota_ (9.88%);
- Key electroactive genera: _Geobacter_ (1.10%), _Proteiniphilum_ (0.84%);
- Exclusive specialized metabolic pathways in different effluent conditions;
- Complex microbial interactions in bioelectrochemical systems.

## Limitations
- Fluctuations in sequencing depths among samples, leading to significant differences in feature coverage;
- Rarefaction removed large amounts of data but retained the maximum possible features for as many samples as possible;
- The analysis lacks sufficient sensitivity to correlate specific microbial communities with many operational conditions.

## Data processing
- Tools: QIIME2, PICRUSt2, SCNIC, BIOM, matplotlib, seaborn, re, pandas, numpy, font_manager, mpol_toolkits.mplot3d, random, sklearn, tidyverse
- Taxonomic classification:
  * Initial: Silva classifier
  * Final: Greengenes2 2024.09 classifier

## Repository Access
https://github.com/jvtarss/ccm-2024
