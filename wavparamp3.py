import os
import subprocess

# Arquivo CUE que você exportou
arquivo_cue = "Reginaldo Rossi - Reginaldo Rossi - 20 Super Sucessos.cue"

# Ler o arquivo corretamente com encoding flexível
with open(arquivo_cue, "r", encoding="latin-1") as f:
    linhas = f.readlines()

# Procurar performer (artista) e title (álbum)
artista = "Desconhecido"
album = "Album Desconhecido"

for l in linhas:
    if l.strip().startswith("PERFORMER") and artista == "Desconhecido":
        artista = l.split('"', 1)[1].rsplit('"', 1)[0]
    if l.strip().startswith("TITLE") and album == "Album Desconhecido":
        album = l.split('"', 1)[1].rsplit('"', 1)[0]

# Listar os arquivos WAV existentes
arquivos = [a for a in os.listdir() if a.lower().endswith(".wav")]

# Converter WAV para MP3 (320kbps)
mp3_files = []
for arquivo in arquivos:
    mp3_file = os.path.splitext(arquivo)[0] + ".mp3"
    cmd = [
        "ffmpeg",
        "-y",  # sobrescreve se já existir
        "-i", arquivo,
        "-codec:a", "libmp3lame",
        "-b:a", "320k",
        mp3_file,
    ]
    subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    mp3_files.append(mp3_file)

# Criar lista M3U com MP3
with open("playlist.m3u", "w", encoding="utf-8") as m3u:
    m3u.write("#EXTM3U\n")
    for mp3_file in sorted(mp3_files):
        titulo = os.path.splitext(os.path.basename(mp3_file))[0]
        m3u.write(f"#EXTINF:-1,{artista} - {titulo}\n")
        m3u.write(f"{mp3_file}\n")

print("✅ Conversão concluída e playlist.m3u gerada com sucesso!")
print(f"Artista detectado: {artista}")
print(f"Álbum detectado: {album}")
