#SPARCC
qiime taxa collapse \
--i-table rarefied-table.qza \
--i-taxonomy gg-taxonomy.qza \
--p-level 2 \
--o-collapsed-table gg-phyla-table.qza

#correl
qiime SCNIC calculate-correlations \
  --i-table gg-phyla-table.qza \
  --p-method sparcc \
  --o-correlation-table gg-sparcc-phyla-correlation-table.qza

# network
qiime SCNIC build-correlation-network-r \
  --i-correlation-table gg-sparcc-phyla-correlation-table.qza \
  --p-min-val 0.5 \
  --o-correlation-network gg-sparcc-phyla-correlation-network.qza

# export network
qiime tools export \
  --input-path gg-sparcc-phyla-correlation-network.qza \
  --output-path gg-sparcc-phyla-exported-network
