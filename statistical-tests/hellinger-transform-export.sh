#feature table collapse
qiime taxa collapse \
--i-table rarefied-table.qza \
--i-taxonomy gg-taxonomy.qza \
--p-level 2 \
--o-collapsed-table gg-phyla-table.qza

qiime taxa collapse \
--i-table rarefied-table.qza \
--i-taxonomy gg-taxonomy.qza \
--p-level 6 \
--o-collapsed-table gg-genus-table.qza

qiime taxa collapse \
--i-table rarefied-table.qza \
--i-taxonomy gg-taxonomy.qza \
--p-level 5 \
--o-collapsed-table gg-family-table.qza

#relative abundances
qiime feature-table relative-frequency \
  --i-table gg-genus-table.qza \
  --o-relative-frequency-table gg-genera-relative-frequency-table.qza
  
#table exportation
qiime tools export \
  --input-path gg-genera-relative-frequency-table.qza \
  --output-path gg-genera-exported-relative-frequency
  
#biom to tsv
biom convert \
  --input-fp gg-genera-exported-relative-frequency/feature-table.biom \
  --output-fp gg-genera-feature-table.tsv \
  --to-tsv

#phyla
qiime taxa collapse \
--i-table rarefied-table.qza \
--i-taxonomy taxonomy.qza \
--p-level 6 \
--o-collapsed-table genus-table.qza

qiime feature-table relative-frequency \
  --i-table gg-genus-table.qza \
  --o-relative-frequency-table genus-relative-frequency-table.qza
  
qiime tools export \
  --input-path genus-relative-frequency-table.qza \
  --output-path genera-exported-relative-frequency
  
biom convert \
  --input-fp genera-exported-relative-frequency/feature-table.biom \
  --output-fp genera-feature-table.tsv \
  --to-tsv
  
