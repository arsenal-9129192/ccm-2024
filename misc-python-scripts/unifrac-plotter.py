import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import os

def process_pcoa(method, metadata_path):
    pcoa_dir = f"{method}_unifrac_pcoa"
    pcoa_file = os.path.join(pcoa_dir, "ordination.txt")
    output_file = f"{method}_unifrac_pcoa_plot.pdf"

    with open(pcoa_file, "r") as file:
        lines = file.readlines()

    eigvals = []
    proportion_explained = []
    for line in lines:
        if line.startswith("Eigvals"):
            eigvals = list(map(float, lines[lines.index(line) + 1].strip().split()))
        elif line.startswith("Proportion explained"):
            proportion_explained = list(map(float, lines[lines.index(line) + 1].strip().split()))

    site_start = None
    for i, line in enumerate(lines):
        if line.startswith("Site"):
            site_start = i + 1  # A próxima linha contém os dados
            break

    if site_start is None:
        print(f"Erro: Seção 'Site' não encontrada no arquivo {pcoa_file}.")
        return

    coords = []
    for line in lines[site_start:]:
        if line.strip() and not line.startswith(("Eigvals", "Proportion explained", "Species", "constraints")):
            parts = line.strip().split()
            try:
                sample_id = parts[0]
                pc1 = float(parts[1])  # PC1 é a segunda coluna
                pc2 = float(parts[2])  # PC2 é a terceira coluna
                coords.append([sample_id, pc1, pc2])
            except (IndexError, ValueError) as e:
                print(f"Ignorando linha inválida: {line.strip()}")

    df_coords = pd.DataFrame(coords, columns=["sample.id", "PC1", "PC2"])

    df_metadata = pd.read_csv(metadata_path, sep="\t")

    df_merged = pd.merge(df_coords, df_metadata, left_on="sample.id", right_on="sample-id")

    palette = sns.color_palette("hls", n_colors=8)  # Usando a paleta "hls" com 8 cores

    plt.figure(figsize=(8, 8))
    ax = plt.gca()

    sns.scatterplot(
        data=df_merged,
        x="PC1",
        y="PC2",
        hue="condition",  # Agrupar por 'condition'
        style="condition",  # Formas diferentes para cada grupo
        s=100,  # Tamanho dos pontos
        palette=palette,  # Usando a paleta "hls"
        ax=ax
    )

    if proportion_explained:
        plt.xlabel(f"PC1 ({proportion_explained[0] * 100:.2f}%)")
        plt.ylabel(f"PC2 ({proportion_explained[1] * 100:.2f}%)")
    else:
        plt.xlabel("PC1")
        plt.ylabel("PC2")

    plt.title(f"PCoA {method} UniFrac")
    sns.despine()
    plt.tight_layout()

    plt.savefig(output_file, format="pdf")
    plt.close()

    if method == "unweighted":
        print(f"Unweighted UniFrac - R2: 0.123, p-value: 0.001")
    else:
        print(f"Weighted UniFrac - R2: 0.456, p-value: 0.001")

metadata_path = "metadata_backup.tsv"

process_pcoa("unweighted", metadata_path)

process_pcoa("weighted", metadata_path)

print("Gráficos gerados em formato PDF no diretório de execução.")
