# MIDI Visualizer (MVP)

A tiny Python/Tkinter app that loads a MIDI file and renders abstract, colorful visuals in real time.

## Features
- Load a `.mid` file and **Play** it visually (no audio).
- Note events trigger glowing **pulses** (circles) whose size/brightness depend on velocity.
- Channel-based color bands + pitch-based color blending.
- Simple, portable code with **Tkinter** and **mido**.

## Install

```bash
python -m venv .venv
.venv\Scripts\pip install -r requirements.txt   # Windows
# or
source .venv/bin/activate && pip install -r requirements.txt  # macOS/Linux
```

> Tkinter ships with Python on Windows/macOS. On some Linux distros you may need: `sudo apt install python3-tk`.

## Run

```bash
python main.py
```

Click **Load MIDI...**, select a file, then **Play**.

## Notes
- This MVP doesn’t synthesize or play audio. It only visualizes MIDI notes.
- It’s structured so we can later:
  - Add **USB live input** (via `python-rtmidi`)  
  - Add more styles (bars, particles)  
  - Package as a Windows `.exe` with PyInstaller
