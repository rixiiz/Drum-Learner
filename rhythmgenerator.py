#uses drumrnn ai to generate drum rhythms
#Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
#.\drumenv\Scripts\Activate.ps1
#Remove-Item -Recurse -Force "C:\path\to\tempfolder"

print("Running:", __file__)
import tkinter as tk
from tkinter import messagebox
import subprocess
import tempfile
import os
import random
import magenta.music as mm
from magenta.models.drums_rnn import drums_rnn_sequence_generator
from magenta.models.shared import sequence_generator_bundle
from note_seq.protobuf import generator_pb2, music_pb2
from PIL import Image, ImageTk

# Constants
TOTAL_STEPS = 64
TEMPO = 120
BUNDLE_PATH = "drum_kit_rnn.mag"  # Make sure this is in your working directory

class DrumGenerator:
    def __init__(self):
        bundle = sequence_generator_bundle.read_bundle_file(BUNDLE_PATH)
        self.generator = drums_rnn_sequence_generator.get_generator_map()['drum_kit'](checkpoint=None, bundle=bundle)
        self.generator.initialize()

    def generate(self, pattern_type='drill'):
        primer = music_pb2.NoteSequence()
        if pattern_type == 'drill':
            for i in range(4):
                primer.notes.add(pitch=38, start_time=0.5 * i, end_time=0.5 * i + 0.1, velocity=80, is_drum=True)
        else:
            # basic 1 bar rhythm primer
            times = [0.0, 0.5, 1.0, 1.5]
            drums = [36, 38, 42, 38]
            for i in range(4):
                primer.notes.add(pitch=drums[i % len(drums)],
                                 start_time=times[i],
                                 end_time=times[i] + 0.1,
                                 velocity=80,
                                 is_drum=True)

        primer.tempos.add(qpm=TEMPO)
        generator_options = generator_pb2.GeneratorOptions()
        generator_options.generate_sections.add(start_time=2, end_time=6)
        return self.generator.generate(primer, generator_options)

def sequence_to_lilypond(sequence):
    parts = []
    hand_labels = ['R', 'L']
    hand_index = 0

    for note in sequence.notes:
        if note.is_drum:
            dur = "16"
            pitch = note.pitch
            drum_map = {
                36: "bd",   # bass drum
                38: "sn",   # snare
                42: "hh",   # closed hi-hat
                44: "hp"    # pedal hi-hat
            }
            label = drum_map.get(pitch, "sn")
            hand = hand_labels[hand_index]
            if label == "sn":
                hand_index = (hand_index + 1) % 2  # Alternate hands
                parts.append(f"\\drummode {{ {label}{dur}^\"{hand}\" }}")
            else:
                parts.append(f"\\drummode {{ {label}{dur} }}")

    return "\\version \"2.24.2\"\n\\new DrumStaff <<\n" + "\n".join(parts) + "\n>>"

def render_lilypond_to_image(ly_text):
    with tempfile.TemporaryDirectory() as tmpdir:
        ly_path = os.path.join(tmpdir, "score.ly")
        with open(ly_path, "w") as f:
            f.write(ly_text)

        subprocess.run(["lilypond", "-dbackend=eps", "-dno-gs-load-fonts",
                        "-dinclude-eps-fonts", "--png", ly_path],
                        cwd=tmpdir, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

        # Output PNG will be named score.png
        png_path = os.path.join(tmpdir, "score.png")
        if os.path.exists(png_path):
            return Image.open(png_path)
        else:
            raise RuntimeError("Failed to generate LilyPond image")

class DrumGUI(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("DrumRNN Rhythm Generator (LilyPond View)")
        self.geometry("800x600")
        self.generator = DrumGenerator()

        self.mode = tk.StringVar(value="drill")
        self.rhythm_image = None
        self.canvas = None

        control_frame = tk.Frame(self)
        control_frame.pack(pady=10)

        tk.Radiobutton(control_frame, text="Drill (Snare L/R)", variable=self.mode, value="drill").pack(side=tk.LEFT)
        tk.Radiobutton(control_frame, text="Beat (Kick, Snare, Hi-Hat)", variable=self.mode, value="beat").pack(side=tk.LEFT)
        tk.Button(control_frame, text="Generate Rhythm", command=self.generate_rhythm).pack(side=tk.LEFT, padx=20)

        self.image_label = tk.Label(self)
        self.image_label.pack(pady=10)

    def generate_rhythm(self):
        try:
            seq = self.generator.generate(self.mode.get())
            ly_text = sequence_to_lilypond(seq)
            img = render_lilypond_to_image(ly_text)
            self.display_image(img)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to generate rhythm:\n{e}")

    def display_image(self, img):
        img = img.resize((760, 120), Image.ANTIALIAS)
        self.rhythm_image = ImageTk.PhotoImage(img)
        self.image_label.configure(image=self.rhythm_image)

if __name__ == "__main__":
    app = DrumGUI()
    app.mainloop()