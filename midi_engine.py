from __future__ import annotations
from typing import Tuple
import mido

DEFAULT_TEMPO = 500000  # 120bpm

def parse_midi(path: str) -> Tuple[list, dict]:
    mid = mido.MidiFile(path)
    ticks_per_beat = mid.ticks_per_beat
    merged = mido.merge_tracks(mid.tracks)

    tempo = DEFAULT_TEMPO
    abs_time_sec = 0.0
    events = []
    pitch_min, pitch_max = None, None

    for msg in merged:
        if msg.time:
            abs_time_sec += mido.tick2second(msg.time, ticks_per_beat, tempo)

        if msg.type == "set_tempo":
            tempo = msg.tempo
            continue

        if msg.type == "note_on":
            ch = getattr(msg, "channel", 0)
            vel = getattr(msg, "velocity", 0)
            pitch = getattr(msg, "note", 60)
            if vel == 0:
                events.append({"time": abs_time_sec, "type": "note_off", "pitch": pitch, "velocity": 0, "channel": ch})
            else:
                events.append({"time": abs_time_sec, "type": "note_on", "pitch": pitch, "velocity": vel, "channel": ch})
                pitch_min = pitch if pitch_min is None else min(pitch_min, pitch)
                pitch_max = pitch if pitch_max is None else max(pitch_max, pitch)

        elif msg.type == "note_off":
            ch = getattr(msg, "channel", 0)
            pitch = getattr(msg, "note", 60)
            events.append({"time": abs_time_sec, "type": "note_off", "pitch": pitch, "velocity": 0, "channel": ch})

    meta = {
        "total_time": abs_time_sec,
        "ticks_per_beat": ticks_per_beat,
        "pitch_min": pitch_min,
        "pitch_max": pitch_max,
    }
    return events, meta
