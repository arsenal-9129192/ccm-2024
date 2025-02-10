qiime dada2 denoise-single \
--i-demultiplexed-seqs single.qza \
--p-trim-left 0 \
--p-trunc-len 0 \
--o-representative-sequences single-rep-seqs.qza \
--o-table single-table.qza \
--o-denoising-stats single-denoising-stats.qza
abc567
qiime dada2 denoise-paired \
  --i-demultiplexed-seqs paired.qza \
  --p-trim-left-f 0 \
  --p-trim-left-r 0 \
  --p-trunc-len-f 0 \
  --p-trunc-len-r 0 \
  --o-representative-sequences paired-rep-seqs.qza \
  --o-table paired-table.qza \
  --o-denoising-stats paired-denoising-stats.qza
  
qiime feature-table summarize \
  --i-table single-table.qza \
  --o-visualization single-table.qzv \
  --m-sample-metadata-file metadata_backup.tsv

qiime feature-table summarize \
  --i-table rarefied-table.qza \
  --o-visualization rarefied-table.qzv \
  --m-sample-metadata-file metadata_backup.tsv
  
qiime feature-table merge \
  --i-tables paired-table.qza \
  --i-tables single-table.qza \
  --o-merged-table merged-table.qza
  
qiime feature-table merge-seqs \
  --i-data paired-rep-seqs.qza \
  --i-data single-rep-seqs.qza \
  --o-merged-data merged-rep-seqs.qza
#merge
qiime feature-table summarize \
  --i-table merged-table.qza \
  --o-visualization merged-table.qzv \
  --m-sample-metadata-file metadata_backup.tsv
