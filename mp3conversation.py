# -*- coding: utf-8 -*-
"""
MP3Conversation — generates an MP3 with free AI voices from a dialogue script.

Script format (one line per utterance):
    CHARACTER: spoken text
Blank lines and lines starting with # are ignored.
Lines without "CHARACTER:" are treated as narration (character "Narrator").

Voices come from the free Microsoft Edge read-aloud service
(edge-tts library). An internet connection is required during generation.
"""

import asyncio
import os
import re
import sys
import threading
import tkinter as tk
from tkinter import filedialog, messagebox, ttk

try:
    import edge_tts
except ImportError:
    print("The edge-tts library is not installed. Run: pip install edge-tts")
    sys.exit(1)

VOICES = [
    # United States
    "en-US-JennyNeural (female, US)",
    "en-US-GuyNeural (male, US)",
    "en-US-AriaNeural (female, US)",
    "en-US-AndrewNeural (male, US)",
    "en-US-AvaNeural (female, US)",
    "en-US-BrianNeural (male, US)",
    "en-US-EmmaNeural (female, US)",
    "en-US-ChristopherNeural (male, US)",
    "en-US-MichelleNeural (female, US)",
    "en-US-EricNeural (male, US)",
    "en-US-AnaNeural (female child, US)",
    "en-US-RogerNeural (male, US)",
    "en-US-SteffanNeural (male, US)",
    "en-US-AndrewMultilingualNeural (male, US)",
    "en-US-AvaMultilingualNeural (female, US)",
    "en-US-BrianMultilingualNeural (male, US)",
    "en-US-EmmaMultilingualNeural (female, US)",
    # United Kingdom
    "en-GB-SoniaNeural (female, UK)",
    "en-GB-RyanNeural (male, UK)",
    "en-GB-LibbyNeural (female, UK)",
    "en-GB-ThomasNeural (male, UK)",
    "en-GB-MaisieNeural (female child, UK)",
    # Australia
    "en-AU-NatashaNeural (female, Australia)",
    "en-AU-WilliamMultilingualNeural (male, Australia)",
    # Canada
    "en-CA-ClaraNeural (female, Canada)",
    "en-CA-LiamNeural (male, Canada)",
    # Ireland
    "en-IE-EmilyNeural (female, Ireland)",
    "en-IE-ConnorNeural (male, Ireland)",
    # India
    "en-IN-NeerjaNeural (female, India)",
    "en-IN-NeerjaExpressiveNeural (female, India)",
    "en-IN-PrabhatNeural (male, India)",
    # New Zealand
    "en-NZ-MollyNeural (female, New Zealand)",
    "en-NZ-MitchellNeural (male, New Zealand)",
    # Hong Kong
    "en-HK-YanNeural (female, Hong Kong)",
    "en-HK-SamNeural (male, Hong Kong)",
    # Singapore
    "en-SG-LunaNeural (female, Singapore)",
    "en-SG-WayneNeural (male, Singapore)",
    # Philippines
    "en-PH-RosaNeural (female, Philippines)",
    "en-PH-JamesNeural (male, Philippines)",
    # South Africa
    "en-ZA-LeahNeural (female, South Africa)",
    "en-ZA-LukeNeural (male, South Africa)",
    # Kenya
    "en-KE-AsiliaNeural (female, Kenya)",
    "en-KE-ChilembaNeural (male, Kenya)",
    # Nigeria
    "en-NG-EzinneNeural (female, Nigeria)",
    "en-NG-AbeoNeural (male, Nigeria)",
    # Tanzania
    "en-TZ-ImaniNeural (female, Tanzania)",
    "en-TZ-ElimuNeural (male, Tanzania)",
]

NARRATOR = "Narrator"
DIALOGUE_LINE = re.compile(r"^([^:]{1,40}):\s*(.+)$")


def extract_voice(combo_item: str) -> str:
    return combo_item.split(" ")[0]


def parse_script(text: str):
    """Returns a list of (character, line)."""
    lines = []
    for raw_line in text.splitlines():
        raw_line = raw_line.strip()
        if not raw_line or raw_line.startswith("#"):
            continue
        m = DIALOGUE_LINE.match(raw_line)
        if m:
            lines.append((m.group(1).strip(), m.group(2).strip()))
        else:
            lines.append((NARRATOR, raw_line))
    return lines


async def generate_mp3(lines, voice_map, output_path, progress):
    with open(output_path, "wb") as output:
        for i, (character, line) in enumerate(lines, start=1):
            voice = voice_map[character]
            progress(i, len(lines), character)
            tts = edge_tts.Communicate(line, voice)
            async for chunk in tts.stream():
                if chunk["type"] == "audio":
                    output.write(chunk["data"])


class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("MP3Conversation — dialogue to MP3 with AI voices")
        self.geometry("1080x620")
        self.minsize(860, 520)
        self.combos = {}
        self.generating = False
        self._build_ui()

    def _build_ui(self):
        top = ttk.Frame(self, padding=8)
        top.pack(fill="x")
        ttk.Button(top, text="Open script…", command=self.open_file).pack(side="left")
        ttk.Button(top, text="Detect characters", command=self.detect).pack(side="left", padx=6)
        self.generate_btn = ttk.Button(top, text="▶ Generate MP3", command=self.generate)
        self.generate_btn.pack(side="right")

        middle = ttk.PanedWindow(self, orient="horizontal")
        middle.pack(fill="both", expand=True, padx=8, pady=4)

        script_frame = ttk.LabelFrame(middle, text="Dialogue script  (format:  CHARACTER: line)")
        self.text = tk.Text(script_frame, wrap="word", font=("Segoe UI", 11), undo=True, width=48)
        scrollbar = ttk.Scrollbar(script_frame, command=self.text.yview)
        self.text.configure(yscrollcommand=scrollbar.set)
        self.text.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        middle.add(script_frame, weight=3)

        self.voices_frame = ttk.LabelFrame(middle, text="Voices per character")
        middle.add(self.voices_frame, weight=2)

        footer = ttk.Frame(self, padding=(6, 4))
        footer.pack(fill="x", side="bottom")
        self.status = ttk.Label(footer, text="Paste your script, click “Detect characters”, then “Generate MP3”.")
        self.status.pack(fill="x")
        self.progress_bar = ttk.Progressbar(footer, mode="determinate")
        # the bar is only shown during generation (see generate/_generation_done)

        self.text.insert("1.0",
            "# Example — delete this and paste your own script\n"
            "Sarah: Hi! I'm looking for a jacket for the winter. Can you help me?\n"
            "Clerk: Of course! Are you thinking of something casual or more formal?\n"
            "Sarah: Something casual, but that I could also wear to work.\n"
            "Clerk: We have this navy blue one on sale. Would you like to try it on?\n"
            "Sarah: It fits perfectly! How much is it?\n"
            "Clerk: It's forty dollars with the discount.\n"
            "Sarah: Great, I'll take it. Can I pay by card?\n"
            "Clerk: Sure! I'll meet you at the register.\n")
        self.detect()

    def open_file(self):
        path = filedialog.askopenfilename(filetypes=[("Text files", "*.txt"), ("All files", "*.*")])
        if not path:
            return
        with open(path, "r", encoding="utf-8-sig") as f:
            content = f.read()
        self.text.delete("1.0", "end")
        self.text.insert("1.0", content)
        self.detect()

    def detect(self):
        lines = parse_script(self.text.get("1.0", "end"))
        characters = []
        for c, _ in lines:
            if c not in characters:
                characters.append(c)

        previous = {c: combo.get() for c, combo in self.combos.items()}
        for child in self.voices_frame.winfo_children():
            child.destroy()
        self.combos = {}

        for i, c in enumerate(characters):
            ttk.Label(self.voices_frame, text=c, font=("Segoe UI", 10, "bold")).grid(
                row=i, column=0, sticky="w", padx=8, pady=6)
            width = max(len(v) for v in VOICES) + 2
            combo = ttk.Combobox(self.voices_frame, values=VOICES, state="readonly", width=width)
            combo.set(previous.get(c, VOICES[i % len(VOICES)]))
            combo.grid(row=i, column=1, sticky="ew", padx=8, pady=6)
            self.combos[c] = combo
        self.voices_frame.columnconfigure(1, weight=1)
        self.status.config(text=f"{len(characters)} character(s) and {len(lines)} line(s) detected.")

    def generate(self):
        if self.generating:
            return
        lines = parse_script(self.text.get("1.0", "end"))
        if not lines:
            messagebox.showwarning("Empty script", "Write or open a script first.")
            return
        characters = {c for c, _ in lines}
        if characters - set(self.combos):
            self.detect()
        voice_map = {c: extract_voice(self.combos[c].get()) for c in characters}

        path = filedialog.asksaveasfilename(
            defaultextension=".mp3", filetypes=[("MP3 audio", "*.mp3")],
            initialfile="dialogue.mp3")
        if not path:
            return

        self.generating = True
        self.generate_btn.config(state="disabled", text="⏳ Generating…")
        self.progress_bar.config(maximum=len(lines), value=0)
        self.progress_bar.pack(fill="x", pady=(4, 0))

        def progress(current, total, character):
            def update():
                self.status.config(text=f"Generating line {current}/{total} — {character}…")
                self.progress_bar.config(value=current - 1)
            self.after(0, update)

        def work():
            try:
                asyncio.run(generate_mp3(lines, voice_map, path, progress))
                self.after(0, lambda: self._finish_ok(path))
            except Exception as error:
                self.after(0, lambda error=error: self._finish_error(error))

        threading.Thread(target=work, daemon=True).start()

    def _generation_done(self):
        self.generating = False
        self.generate_btn.config(state="normal", text="▶ Generate MP3")
        self.progress_bar.pack_forget()

    def _finish_ok(self, path):
        self._generation_done()
        self.status.config(text=f"Done! MP3 saved to: {path}")
        if messagebox.askyesno("Finished", f"MP3 generated successfully!\n\n{path}\n\nOpen the file's folder?"):
            os.startfile(os.path.dirname(path))

    def _finish_error(self, error):
        self._generation_done()
        self.status.config(text=f"Error: {error}")
        messagebox.showerror(
            "Generation error",
            f"Could not generate the audio.\n\n{error}\n\n"
            "Check your internet connection and try again.")


if __name__ == "__main__":
    App().mainloop()
