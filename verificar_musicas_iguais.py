import os
import hashlib
from mutagen import File
import tkinter as tk
from tkinter import ttk
import threading

# Caminho base das músicas
PASTA_MUSICAS = r"D:\Musicas"  # Altere para sua pasta

# --- FUNÇÕES ---
def hash_arquivo(caminho, bloco=65536):
    md5 = hashlib.md5()
    try:
        with open(caminho, 'rb') as f:
            for chunk in iter(lambda: f.read(bloco), b""):
                md5.update(chunk)
        return md5.hexdigest()
    except Exception:
        return None

def info_audio(caminho):
    try:
        audio = File(caminho)
        if not audio:
            return (0, 0, os.path.basename(caminho), "Desconhecido", "Desconhecido")
        bitrate = int(audio.info.bitrate / 1000) if hasattr(audio.info, 'bitrate') else 0
        duracao = int(audio.info.length) if hasattr(audio.info, 'length') else 0
        titulo = getattr(audio.tags.get("TIT2"), "text", [os.path.basename(caminho)])[0] if audio.tags and "TIT2" in audio else os.path.basename(caminho)
        artista = getattr(audio.tags.get("TPE1"), "text", ["Desconhecido"])[0] if audio.tags and "TPE1" in audio else "Desconhecido"
        album = getattr(audio.tags.get("TALB"), "text", ["Desconhecido"])[0] if audio.tags and "TALB" in audio else "Desconhecido"
        return (bitrate, duracao, titulo, artista, album)
    except Exception:
        return (0, 0, os.path.basename(caminho), "Desconhecido", "Desconhecido")

# --- VARREDURA DE DUPLICADOS ---
def processar_musicas(frame, progresso_var, barra_progresso):
    musicas = {}
    arquivos_totais = []
    
    # Contar todos os arquivos primeiro
    for raiz, _, arquivos in os.walk(PASTA_MUSICAS):
        for arquivo in arquivos:
            if arquivo.lower().endswith((".mp3", ".flac", ".wav", ".m4a", ".ogg")):
                arquivos_totais.append(os.path.join(raiz, arquivo))
    
    total = len(arquivos_totais)
    barra_progresso['maximum'] = total

    for idx, caminho in enumerate(arquivos_totais, 1):
        h = hash_arquivo(caminho)
        if not h:
            continue
        bitrate, duracao, titulo, artista, album = info_audio(caminho)
        info = {
            "caminho": caminho,
            "bitrate": bitrate,
            "duracao": duracao,
            "titulo": titulo,
            "artista": artista,
            "album": album
        }
        musicas.setdefault(h, []).append(info)

        # Atualizar barra de progresso
        progresso_var.set(idx)
        frame.update_idletasks()

    duplicados = {h: v for h, v in musicas.items() if len(v) > 1}

    # Limpar frame e barra
    for widget in frame.winfo_children():
        widget.destroy()

    if not duplicados:
        tk.Label(frame, text="✅ Nenhuma música duplicada encontrada.", font=("Arial", 14)).pack(pady=10)
    else:
        for i, (h, lista) in enumerate(duplicados.items(), 1):
            dup_frame = tk.LabelFrame(frame, text=f"DUPLICADO {i}", padx=10, pady=10, font=("Arial", 12, "bold"))
            dup_frame.pack(fill="x", pady=5, padx=5)

            for item in lista:
                caminho = item['caminho']
                bitrate = item['bitrate']
                duracao = item['duracao']
                titulo = item['titulo']
                artista = item['artista']
                album = item['album']

                info_label = tk.Label(
                    dup_frame,
                    text=f"{titulo} — {artista} — {album} | {bitrate} kbps | {duracao}s\n{caminho}",
                    anchor="w",
                    justify="left",
                    wraplength=900
                )
                info_label.pack(fill="x", padx=5, pady=2)

# --- INTERFACE TKINTER ---
root = tk.Tk()
root.title("Duplicadas de Música")
root.geometry("950x700")

canvas = tk.Canvas(root)
scrollbar = tk.Scrollbar(root, orient="vertical", command=canvas.yview)
scrollable_frame = tk.Frame(canvas)
scrollable_frame.bind(
    "<Configure>",
    lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
)
canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
canvas.configure(yscrollcommand=scrollbar.set)
canvas.pack(side="left", fill="both", expand=True)
scrollbar.pack(side="right", fill="y")

# Mensagem e barra de progresso inicial
tk.Label(scrollable_frame, text="🔍 Verificando músicas nas subpastas...", font=("Arial", 14)).pack(pady=20)
progresso_var = tk.IntVar()
barra_progresso = ttk.Progressbar(scrollable_frame, orient="horizontal", length=600, mode="determinate", variable=progresso_var)
barra_progresso.pack(pady=10)

# Rodar a varredura em thread
threading.Thread(target=processar_musicas, args=(scrollable_frame, progresso_var, barra_progresso), daemon=True).start()

root.mainloop()
