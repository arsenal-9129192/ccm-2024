#rooted/unrooted trees
qiime phylogeny align-to-tree-mafft-fasttree \
  --i-sequences merged-rep-seqs.qza \
  --o-alignment aligned-rep-seqs.qza \
  --o-masked-alignment masked-aligned-rep-seqs.qza \
  --o-tree unrooted-tree.qza \
  --o-rooted-tree rooted-tree.qza
  
#bar plot
qiime taxa barplot \
  --i-table rarefied-table.qza \
  --i-taxonomy taxonomy.qza \
  --m-metadata-file metadata_backup.tsv \
  --o-visualization taxa-bar-plots.qzv

#diversity analysis
qiime diversity core-metrics-phylogenetic \
  --i-phylogeny rooted-tree.qza \
  --i-table paired-table.qza \
  --p-sampling-depth 2849 \
  --m-metadata-file metadata_backup.tsv \
  --o-rarefied-table rarefied-table.qza \
  --o-faith-pd-vector faith-pd.qza \
  --o-unweighted-unifrac-distance-matrix unweighted-unifrac.qza \
  --o-weighted-unifrac-distance-matrix weighted-unifrac.qza
  
  qiime diversity pcoa \
  --i-distance-matrix weighted-unifrac.qza \
  --o-pcoa pcoa-weighted-unifrac.qza

qiime emperor plot \
  --i-pcoa pcoa-weighted-unifrac.qza \
  --m-metadata-file metadata_backup.tsv \
  --o-visualization emperor-weighted-unifrac.qzv

#alpha diversity
qiime diversity alpha \
  --i-table rarefied-table.qza \
  --p-metric shannon \
  --o-alpha-diversity shannon-diversity.qza

qiime metadata tabulate \
  --m-input-file shannon-diversity.qza \
  --o-visualization shannon-diversity.qzv

#alpha comparison
qiime diversity alpha-group-significance \
  --i-alpha-diversity shannon-diversity.qza \
  --m-metadata-file metadata_backup.tsv \
  --o-visualization alpha-group-significance.qzv
  
qiime diversity alpha \
  --i-table rarefied-table.qza \
  --p-metric observed_features \
  --o-alpha-diversity observed-features.qza

#beta bray curtis diversity
qiime diversity beta \
  --i-table rarefied-table.qza \
  --p-metric braycurtis \
  --o-distance-matrix beta-diversity-braycurtis.qza

#pcoa beta
qiime diversity pcoa \
  --i-distance-matrix beta-diversity-braycurtis.qza \
  --o-pcoa pcoa-braycurtis.qza

qiime emperor plot \
  --i-pcoa pcoa-braycurtis.qza \
  --m-metadata-file metadata_backup.tsv \
  --o-visualization emperor-braycurtis.qzv

# weighted unifrac
qiime diversity beta-phylogenetic \
  --i-table rarefied-table.qza \
  --i-phylogeny rooted-tree.qza \
  --p-metric weighted_unifrac \
  --o-distance-matrix weighted_unifrac_distance.qza

# unweighted unifrac
qiime diversity beta-phylogenetic \
  --i-table rarefied-table.qza \
  --i-phylogeny rooted-tree.qza \
  --p-metric unweighted_unifrac \
  --o-distance-matrix unweighted_unifrac_distance.qza
  
  # weighted unifrac pcoa
qiime diversity pcoa \
  --i-distance-matrix weighted_unifrac_distance.qza \
  --o-pcoa weighted_unifrac_pcoa.qza

# unweighted unifrac pcoa
qiime diversity pcoa \
  --i-distance-matrix unweighted_unifrac_distance.qza \
  --o-pcoa unweighted_unifrac_pcoa.qza
  
  # weighted unifrac pcoa view
qiime emperor plot \
  --i-pcoa weighted_unifrac_pcoa.qza \
  --m-metadata-file metadata_backup.tsv \
  --o-visualization weighted_unifrac_emperor.qzv

# unweighted unifrac pcoa view
qiime emperor plot \
  --i-pcoa unweighted_unifrac_pcoa.qza \
  --m-metadata-file metadata_backup.tsv \
  --o-visualization unweighted_unifrac_emperor.qzv
  
  # permanova unifrac weighted
qiime diversity beta-group-significance \
  --i-distance-matrix weighted_unifrac_distance.qza \
  --m-metadata-file metadata_backup.tsv \
  --m-metadata-column condition \
  --p-method permanova \
  --o-visualization weighted_unifrac_permanova.qzv

# permanova unifrac unweighted
qiime diversity beta-group-significance \
  --i-distance-matrix unweighted_unifrac_distance.qza \
  --m-metadata-file metadata_backup.tsv \
  --m-metadata-column condition \
  --p-method permanova \
  --o-visualization unweighted_unifrac_permanova.qzv
  
 
#genera filtering
qiime taxa collapse \
  --i-table rarefied-table.qza \
  --i-taxonomy taxonomy.qza \
  --p-level 6 \
  --o-collapsed-table genus-table.qza
  
  qiime feature-table group \
  --i-table genus-hellinger-table.qza \
  --p-axis sample \
  --m-metadata-file metadata_backup.tsv \
  --m-metadata-column condition \
  --p-mode mean-ceiling \
  --o-grouped-table grouped-genus-hellinger-table.qza
