import os
import subprocess
from mutagen.flac import FLAC

# Caminho da pasta onde estão os arquivos
pasta = r"D:\editorflac"

# Nomes dos arquivos
arquivo_cue = "KC And The Sunshine Band - Do You Wanna Go Party.cue"
arquivo_flac = "KC And The Sunshine Band - Do You Wanna Go Party.flac"
shntool_exe = "shntool.exe"

# Função para ler faixas do CUE
def ler_cue(cue_path):
    faixas = []
    track = None
    dentro_track = False

    with open(cue_path, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line.startswith("TRACK"):
                if track:
                    faixas.append(track)
                track = {"TITLE": "", "PERFORMER": ""}
                dentro_track = True
            elif dentro_track and line.startswith("TITLE"):
                track["TITLE"] = line.split('"')[1]
            elif dentro_track and line.startswith("PERFORMER"):
                track["PERFORMER"] = line.split('"')[1]

    if track:
        faixas.append(track)
    return faixas

# 1️⃣ Dividir o FLAC usando shntool
print("Dividindo o arquivo FLAC em faixas...")
subprocess.run([
    os.path.join(pasta, shntool_exe),
    "split",
    "-f", os.path.join(pasta, arquivo_cue),
    "-t", "%n - %t",
    "-o", "flac",
    os.path.join(pasta, arquivo_flac)
], check=True)

# 2️⃣ Ler faixas do cue
faixas = ler_cue(os.path.join(pasta, arquivo_cue))

# 3️⃣ Aplicar tags
print("Aplicando tags nas faixas...")
for i, faixa in enumerate(faixas, start=1):
    numero = f"{i:02d}"  # 01, 02, 03...
    # Procura arquivo que comece com número correspondente
    nome_arquivo = [f for f in os.listdir(pasta) if f.startswith(numero) and f.endswith(".flac")]
    if nome_arquivo:
        flac_path = os.path.join(pasta, nome_arquivo[0])
        audio = FLAC(flac_path)
        audio["title"] = faixa["TITLE"]
        audio["artist"] = faixa["PERFORMER"] if faixa["PERFORMER"] else "Julio Iglesias"
        audio["album"] = "Do You Wanna Go Party"
        audio.save()
        print(f"Tags aplicadas: {nome_arquivo[0]} → {faixa['TITLE']}")
    else:
        print(f"Arquivo não encontrado para a faixa {numero}")

print("✅ Concluído! Todas as faixas foram criadas e etiquetadas.")
