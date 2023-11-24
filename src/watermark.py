import subprocess
import os

def add_watermark(input_file):
    print("...Adding watermark...")
    watermark = "@peakyclips"
    output_file = input_file.split(".")[0] + "_watermark.mp4"
    font_path = "./font/moon_get-Heavy.ttf"  
    ffmpeg_cmd = [
        "ffmpeg",
        "-i", input_file,
        "-vf", f"drawtext=text='{watermark}':fontfile={font_path}:fontcolor=white:fontsize=18:x=50:y=100",
        "-codec:a", "copy",
        output_file
    ]
        # Aggiunta di subprocess.PIPE per gestire l'output e l'errore
    completed_process = subprocess.run(
        ffmpeg_cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE
    )

    # Verifica se ci sono errori
    if completed_process.returncode != 0:
        print("Si è verificato un errore:", completed_process.stderr.decode('utf-8'))
    else:
        print("Conversione completata con successo!")
    os.remove(input_file)
    os.rename(output_file, input_file)