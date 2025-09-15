from __future__ import annotations
import time
from utils.config import FPS
import pygame.midi


class Controller:
    def __init__(self, canvas, visual):
        self.canvas = canvas
        self.visual = visual
        self.events = []
        self.meta = {}
        self._start_wall = None
        self._playhead = 0.0
        self._running = False
        self._idx = 0

        # Init pygame.midi and open default output device
        pygame.midi.init()
        try:
            self.midi_out = pygame.midi.Output(0)  # 0 = default device
        except Exception:
            self.midi_out = None
            print("Warning: No MIDI output device found. Notes will be silent.")

    def load_events(self, events: list, meta: dict):
        self.stop()
        self.events = events
        self.meta = meta
        self.visual.set_pitch_range(meta.get("pitch_min"), meta.get("pitch_max"))
        self._playhead = 0.0
        self._idx = 0

    def play(self):
        if not self.events:
            return
        if not self._running:
            self._running = True
            self._start_wall = time.perf_counter() - self._playhead

    def stop(self):
        if self._running:
            self._running = False
        self._playhead = 0.0
        self._idx = 0
        self.visual.clear()

        # Turn off all possible notes to avoid "stuck notes"
        if self.midi_out:
            for ch in range(16):
                for pitch in range(128):
                    self.midi_out.note_off(pitch, 0, ch)

    def pause(self):
        if self._running:
            self._running = False
            self._playhead = time.perf_counter() - self._start_wall

    def tick(self, schedule_next_cb):
        if self._running:
            now_wall = time.perf_counter()
            self._playhead = now_wall - self._start_wall

            # dispatch events up to current playhead
            while self._idx < len(self.events) and self.events[self._idx]["time"] <= self._playhead:
                evt = self.events[self._idx]
                self._idx += 1
                if evt["type"] == "note_on":
                    # Use playhead time (not wall-clock)
                    self.visual.spawn_from_note(evt["pitch"], evt["velocity"], evt["channel"], self._playhead)
                    if self.midi_out:
                        self.midi_out.note_on(evt["pitch"], evt["velocity"], evt["channel"])
                elif evt["type"] == "note_off":
                    if self.midi_out:
                        self.midi_out.note_off(evt["pitch"], 0, evt["channel"])

            # update visuals with playhead time
            self.visual.update_and_draw(self._playhead)

            # stop automatically at the end (with a short tail)
            total = self.meta.get("total_time", 0.0)
            if self._playhead > total + 2.0 and not self.visual.particles:
                self._running = False

        # schedule next frame
        delay_ms = int(1000 / FPS)
        schedule_next_cb(delay_ms)

    def close(self):
        """Call this on app exit to release MIDI device."""
        if self.midi_out:
            self.midi_out.close()
        pygame.midi.quit()
