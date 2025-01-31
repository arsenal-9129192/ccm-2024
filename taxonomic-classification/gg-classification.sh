qiime feature-classifier classify-sklearn \
--i-classifier silva-138-99-nb-classifier.qza \
--i-reads merged-rep-seqs.qza \
--o-classification taxonomy.qza

qiime metadata tabulate \
  --m-input-file taxonomy.qza \
  --o-visualization taxonomy.qzv
  
  #Greengenes
  qiime feature-classifier classify-sklearn \
  --i-classifier 2024.09.backbone.full-length.nb.sklearn-1.4.2.qza \
  --i-reads merged-rep-seqs.qza \
  --o-classification gg-taxonomy.qza \
  --p-confidence 0.8
