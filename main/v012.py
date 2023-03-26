import tkinter as tk
from tkinter import filedialog
import tkinter.messagebox as messagebox
from youtube_transcript_api import YouTubeTranscriptApi, NoTranscriptFound
import yt_dlp
import tempfile
import os
import shutil


def progress_hook(status):
    if status['status'] == 'downloading':
        percentage = status['_percent_str'].strip()
        status_label.config(text=f"Downloading audio: {percentage}")
    elif status['status'] == 'finished':
        status_label.config(text="Download complete. Saving audio...")



def download_audio():
    url = url_entry.get()
    video_id = extract_video_id(url)

    if video_id:
        try:
            ydl_opts = {
                'format': 'bestaudio/best',
                'postprocessors': [{
                    'key': 'FFmpegExtractAudio',
                    'preferredcodec': 'm4a',
                    'preferredquality': '192',
                }],
                'outtmpl': os.path.join(os.getcwd(), '%(title)s.%(ext)s'),
                'progress_hooks': [progress_hook],
            }
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download([url])
            status_label.config(text="Audio saved successfully.")
        except Exception as e:
            messagebox.showerror("Error", f"Error: {e}")
            status_label.config(text=f"Error: {e}")
    else:
        status_label.config(text="Invalid URL")

        

def extract_video_id(url):
    if 'watch?v=' in url:
        return url.split('watch?v=')[-1]
    return None

def save_transcript_to_txt(transcript, filename):
    transcript_text = ""
    for entry in transcript:
        transcript_text += entry['text'] + '\n'
    
    with open(filename, 'w', encoding='utf-8') as f:
        f.write(transcript_text)
    
    return transcript_text

def process_url():
    url = url_entry.get()
    video_id = extract_video_id(url)
    selected_language = language_var.get()

    if video_id:
        try:
            transcript = YouTubeTranscriptApi.get_transcript(video_id, languages=[selected_language])
            save_file_path = filedialog.asksaveasfilename(defaultextension=".txt")
            if save_file_path:
                captions_text = save_transcript_to_txt(transcript, save_file_path)
                captions_textbox.delete(1.0, tk.END)
                captions_textbox.insert(tk.END, captions_text)
                status_label.config(text="Captions saved successfully.")
            else:
                status_label.config(text="Saving was cancelled.")
        except NoTranscriptFound:
            status_label.config(text="No captions found for the selected language. Please choose another language.")
        except Exception as e:
            messagebox.showerror("Error", f"Error: {e}")
            status_label.config(text=f"Error: {e}")
    else:
        status_label.config(text="Invalid URL")

def paste_url():
    url_entry.insert(tk.END, app.clipboard_get())

app = tk.Tk()
app.title("YouTube Extractor")
app.geometry("900x500")


url_frame = tk.Frame(app)
url_frame.pack(pady=10)

url_label = tk.Label(url_frame, text="YouTube URL:")
url_label.pack(side=tk.LEFT)

url_entry = tk.Entry(url_frame, width=50)
url_entry.pack(side=tk.LEFT)

paste_button = tk.Button(url_frame, text="Paste", command=paste_url)
paste_button.pack(side=tk.LEFT, padx=(0, 5))

language_label = tk.Label(app, text="Select language:")
language_label.pack(pady=5)

available_languages = ['en', 'es', 'de', 'fr', 'it', 'ja', 'ko', 'pt', 'ru', 'zh-Hans', 'zh-Hant']
language_var = tk.StringVar(app)
language_var.set(available_languages[0])

language_menu = tk.OptionMenu(app, language_var, *available_languages)
language_menu.pack(pady=5)

button_frame = tk.Frame(app)
button_frame.pack(pady=10)

process_button = tk.Button(button_frame, text="Extract Captions", command=process_url)
process_button.pack(side=tk.LEFT, padx=(0, 10))

download_audio_button = tk.Button(button_frame, text="Extract Audio", command=download_audio)
download_audio_button.pack(side=tk.LEFT, padx=(0, 5))

status_label = tk.Label(button_frame, text="")
status_label.pack(side=tk.LEFT, padx=(5, 0))

captions_textbox = tk.Text(app, wrap=tk.WORD, width=80, height=10, font=("Arial", 15), padx=10, pady=10)
captions_textbox.pack(pady=10)

scrollbar = tk.Scrollbar(app, command=captions_textbox.yview)
scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

captions_textbox.config(yscrollcommand=scrollbar.set)

app.mainloop()
