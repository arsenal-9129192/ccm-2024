
import qiime2
import pandas as pd
import os

def convert_to_stamp(rarefied_table, metadata_file, output_dir):
    """
    Converte tabela rarefeita do QIIME2 para formato STAMP
    
    Parâmetros:
    rarefied_table: arquivo .qza com tabela rarefeita
    metadata_file: arquivo de metadados com grupos
    output_dir: diretório para salvar outputs
    """
    
    os.makedirs(output_dir, exist_ok=True)
    
    table_artifact = qiime2.Artifact.load(rarefied_table)
    table_df = table_artifact.view(pd.DataFrame)
    
    metadata = pd.read_csv(metadata_file, sep='\t', index_col='sample-id')
    
    metadata_subset = metadata[['condition']]
    
    table_df.index.name = 'Sample'
    
    table_with_groups = table_df.merge(metadata_subset, 
                                     left_index=True, 
                                     right_index=True, 
                                     how='inner')
    
    if table_with_groups['condition'].duplicated().any():
        print("Aviso: Há amostras associadas a múltiplos grupos. Serão mantidos apenas os primeiros grupos encontrados.")
        table_with_groups = table_with_groups[~table_with_groups.index.duplicated(keep='first')]
    
    cols = table_with_groups.columns.tolist()
    cols.remove('condition')
    cols = ['condition'] + cols
    table_with_groups = table_with_groups[cols]
    
    table_with_groups.reset_index(inplace=True)
    
    table_with_groups = table_with_groups.rename(columns={'condition': 'Group'})
    
    output_file = os.path.join(output_dir, 'stamp_input.tsv')
    table_with_groups.to_csv(output_file, sep='\t', index=False)
    
    return output_file

def main():
    base_dir = os.getcwd()
    output_dir = os.path.join(base_dir, "stamp_analysis")
    
    rarefied_table = "rarefied-table.qza"
    metadata_file = "metadata_backup.tsv"
    
    stamp_file = convert_to_stamp(rarefied_table, 
                                metadata_file, 
                                output_dir)
    
    print(f"\nArquivo para análise STAMP criado: {stamp_file}")
    print("\nFormato do arquivo:")
    print("- Primeira coluna: Sample (nomes das amostras)")
    print("- Segunda coluna: Group (grupos do metadata)")
    print("- Demais colunas: Features com contagens rarefeitas")

if __name__ == "__main__":
    main()
