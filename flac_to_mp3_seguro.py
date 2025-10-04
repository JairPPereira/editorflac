import os
import subprocess
import re
import unicodedata
from mutagen.flac import FLAC
from mutagen.id3 import ID3, TIT2, TPE1, TALB

# Pasta com os arquivos FLAC
pasta = r"D:\editorflac"

# Pasta de saída MP3
saida_mp3 = os.path.join(pasta, "MP3")
os.makedirs(saida_mp3, exist_ok=True)

# Função para tornar o nome seguro para Windows
def nome_seguro(nome):
    # Remove acentos
    nome = unicodedata.normalize('NFKD', nome).encode('ASCII', 'ignore').decode('ASCII')
    # Substitui caracteres inválidos por underscore
    nome = re.sub(r'[<>:"/\\|?*]', '_', nome)
    # Remove parênteses extras
    nome = nome.replace("(", "").replace(")", "")
    # Remove múltiplos espaços
    nome = re.sub(r'\s+', ' ', nome).strip()
    return nome

# Processa todos os arquivos FLAC na pasta
for arquivo in os.listdir(pasta):
    if arquivo.endswith(".flac"):
        flac_path = os.path.join(pasta, arquivo)
        
        # Lê tags do FLAC
        audio_flac = FLAC(flac_path)
        titulo = audio_flac.get("title", [""])[0]
        artista = audio_flac.get("artist", [""])[0]
        album = audio_flac.get("album", [""])[0]

        # Nome do MP3 seguro
        nome_base = f"{titulo}"
        nome_mp3 = nome_seguro(nome_base) + ".mp3"
        mp3_path = os.path.join(saida_mp3, nome_mp3)

        # Converte usando FFmpeg para MP3 320 kbps
        subprocess.run([
            "ffmpeg", "-y", "-i", flac_path,
            "-codec:a", "libmp3lame", "-b:a", "320k",
            mp3_path
        ], check=True)

        # Aplica tags ID3 no MP3
        audio_mp3 = ID3(mp3_path)
        audio_mp3.add(TIT2(encoding=3, text=titulo))
        audio_mp3.add(TPE1(encoding=3, text=artista))
        audio_mp3.add(TALB(encoding=3, text=album))
        audio_mp3.save()

        print(f"{arquivo} → convertido para MP3 320 kbps com tags, nome seguro: {nome_mp3}")

print("Conversão concluída! Todos os MP3s estão renomeados de forma segura.")
