from __future__ import annotations
from dataclasses import dataclass
from typing import List, Tuple, Optional
import random, math

from utils.config import (
    BACKGROUND, PARTICLE_BASE_LIFETIME, PARTICLE_MAX_LIFETIME,
    PARTICLE_MIN_RADIUS, PARTICLE_MAX_RADIUS, MAX_PARTICLES
)
from utils import color_maps

@dataclass
class Particle:
    x: float
    y: float
    radius: float
    color_rgb: Tuple[int,int,int]
    birth_time: float      # in playhead seconds, not wall time
    lifetime: float
    velocity: float
    channel: int
    pitch: int

class VisualEngine:
    def __init__(self, canvas, width: int, height: int):
        self.canvas = canvas
        self.width = width
        self.height = height
        self.particles: List[Particle] = []
        self.pitch_min = 21
        self.pitch_max = 108
        self._rng = random.Random(1234)

    def set_pitch_range(self, pmin: Optional[int], pmax: Optional[int]):
        if pmin is not None and pmax is not None and pmin < pmax:
            self.pitch_min, self.pitch_max = pmin, pmax

    def clear(self):
        self.particles.clear()
        self.canvas.delete("all")
        self.canvas.configure(background=BACKGROUND)

    def _hex_to_rgb(self, hexstr: str) -> Tuple[int,int,int]:
        hexstr = hexstr.lstrip("#")
        return tuple(int(hexstr[i:i+2], 16) for i in (0,2,4))

    def spawn_from_note(self, pitch: int, velocity: int, channel: int, playhead_time: float):
        """Spawn a new particle, using playhead_time as the reference clock."""
        x = self._map_pitch_to_x(pitch)
        band_h = self.height / 8.0
        band = channel % 8
        y = (band + 0.5) * band_h + self._rng.uniform(-0.25, 0.25) * band_h

        base_radius = PARTICLE_MIN_RADIUS + (velocity / 127.0) * (PARTICLE_MAX_RADIUS - PARTICLE_MIN_RADIUS)

        ch_hex = color_maps.channel_color(channel)
        pt_hex = color_maps.pitch_to_color_hex(pitch, self.pitch_min, self.pitch_max)
        cr, cg, cb = self._hex_to_rgb(ch_hex)
        pr, pg, pb = self._hex_to_rgb(pt_hex)
        r = int(0.6 * cr + 0.4 * pr)
        g = int(0.6 * cg + 0.4 * pg)
        b = int(0.6 * cb + 0.4 * pb)

        life = PARTICLE_BASE_LIFETIME + (velocity / 127.0) * (PARTICLE_MAX_LIFETIME - PARTICLE_BASE_LIFETIME)

        p = Particle(x=x, y=y, radius=base_radius, color_rgb=(r,g,b),
                     birth_time=playhead_time, lifetime=life,
                     velocity=velocity, channel=channel, pitch=pitch)
        self.particles.append(p)

        if len(self.particles) > MAX_PARTICLES:
            drop = max(1, len(self.particles)//10)
            self.particles = self.particles[drop:]

    def _map_pitch_to_x(self, pitch: int) -> float:
        pmin, pmax = self.pitch_min, self.pitch_max
        if pmax <= pmin:
            return self.width * 0.5
        t = (pitch - pmin) / float(pmax - pmin)
        t = max(0.0, min(1.0, t))
        margin = 60.0
        return margin + t * (self.width - 2*margin)

    def update_and_draw(self, playhead_time: float):
        """Update/draw based on playhead time, so pause works properly."""
        self.canvas.delete("all")
        self.canvas.configure(background=BACKGROUND)

        alive = []
        for p in self.particles:
            age = playhead_time - p.birth_time
            if age < 0:
                continue  # not yet started
            if age >= p.lifetime:
                continue
            t = age / p.lifetime
            rad = p.radius * (1.0 + 0.8 * (1.0 - math.cos(t * math.pi)))
            fade = max(0.0, (1.0 - t)) ** 1.3
            r = int(p.color_rgb[0] * fade)
            g = int(p.color_rgb[1] * fade)
            b = int(p.color_rgb[2] * fade)
            hexcol = f"#{r:02X}{g:02X}{b:02X}"
            x0, y0 = p.x - rad, p.y - rad
            x1, y1 = p.x + rad, p.y + rad
            outline_w = max(1, int(1 + (p.velocity / 127.0) * 5))
            self.canvas.create_oval(x0, y0, x1, y1, outline=hexcol, width=outline_w)
            alive.append(p)
        self.particles = alive
