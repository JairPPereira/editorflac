import os
import hashlib
from mutagen import File
from pydub import AudioSegment
import simpleaudio as sa

# Caminho base onde estão as músicas
PASTA_MUSICAS = r"D:\Musicas"

# Função para calcular o hash do conteúdo do arquivo
def hash_arquivo(caminho, bloco=65536):
    md5 = hashlib.md5()
    try:
        with open(caminho, 'rb') as f:
            for chunk in iter(lambda: f.read(bloco), b""):
                md5.update(chunk)
        return md5.hexdigest()
    except Exception:
        return None

# Função para obter informações de áudio (bitrate e duração)
def info_audio(caminho):
    try:
        audio = File(caminho)
        if not audio:
            return (0, 0)
        bitrate = int(audio.info.bitrate / 1000) if hasattr(audio.info, 'bitrate') else 0
        duracao = int(audio.info.length) if hasattr(audio.info, 'length') else 0
        return (bitrate, duracao)
    except Exception:
        return (0, 0)

# Função para tocar o áudio
def tocar_musica(caminho):
    try:
        som = AudioSegment.from_file(caminho)
        play_obj = sa.play_buffer(
            som.raw_data,
            num_channels=som.channels,
            bytes_per_sample=som.sample_width,
            sample_rate=som.frame_rate
        )
        input("▶️ Tocando... pressione ENTER para parar.")
        play_obj.stop()
    except Exception as e:
        print(f"Erro ao tocar {caminho}: {e}")

# Busca todas as músicas e calcula hash
musicas = {}
print("🔍 Verificando músicas nas subpastas...\n")

for raiz, _, arquivos in os.walk(PASTA_MUSICAS):
    for arquivo in arquivos:
        if arquivo.lower().endswith((".mp3", ".flac", ".wav", ".m4a", ".ogg")):
            caminho = os.path.join(raiz, arquivo)
            h = hash_arquivo(caminho)
            if not h:
                continue
            bitrate, duracao = info_audio(caminho)
            info = {"caminho": caminho, "bitrate": bitrate, "duracao": duracao}
            musicas.setdefault(h, []).append(info)

# Mostra duplicados
duplicados = {h: v for h, v in musicas.items() if len(v) > 1}

if not duplicados:
    print("✅ Nenhuma música duplicada encontrada.")
else:
    print("\n🎵 Músicas duplicadas encontradas:\n")
    for i, (h, lista) in enumerate(duplicados.items(), 1):
        print(f"\n--- DUPLICADO {i} ---")
        for j, item in enumerate(lista, 1):
            print(f"[{j}] {item['caminho']}")
            print(f"    Bitrate: {item['bitrate']} kbps | Duração: {item['duracao']}s")
        
        while True:
            acao = input("\nDigite o número da música para ESCUTAR, 'd' para excluir uma, ou ENTER para pular: ").strip()
            if acao == "":
                break
            elif acao.isdigit() and 1 <= int(acao) <= len(lista):
                tocar_musica(lista[int(acao) - 1]['caminho'])
            elif acao.lower() == "d":
                num = input("Digite o número da música a excluir: ")
                if num.isdigit() and 1 <= int(num) <= len(lista):
                    caminho_excluir = lista[int(num) - 1]['caminho']
                    os.remove(caminho_excluir)
                    print(f"🗑️ Excluído: {caminho_excluir}")
                    break
            else:
                print("Opção inválida.")
