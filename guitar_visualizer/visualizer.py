# Program to visualize guitar notes from a simple text file.
# The program reads a list of note names and generates an interactive
# HTML file that shows each note on a guitar fretboard sequentially.

from __future__ import annotations

import json
import os
from typing import List, Tuple

NOTE_ORDER = ["C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B"]
FLAT_TO_SHARP = {"Db": "C#", "Eb": "D#", "Gb": "F#", "Ab": "G#", "Bb": "A#"}

STANDARD_TUNING = ["E2", "A2", "D3", "G3", "B3", "E4"]


def note_to_midi(note: str) -> int:
    """Convert note name like 'C4' or 'F#3' to MIDI number."""
    note = note.strip()
    if len(note) < 2:
        raise ValueError(f"Invalid note: {note}")
    pitch = note[0]
    rest = note[1:]
    accidental = ""
    if rest and rest[0] in {"#", "b"}:
        accidental = rest[0]
        rest = rest[1:]
    octave = int(rest)
    if accidental == "b":
        pitch = FLAT_TO_SHARP.get(pitch + "b", pitch)
    elif accidental == "#":
        pitch = pitch + "#"
    idx = NOTE_ORDER.index(pitch)
    return 12 * (octave + 1) + idx


def parse_notes(text: str) -> List[str]:
    """Return a list of note strings from given text."""
    return [n for n in text.replace(",", " ").split() if n]


def find_position(
    midi: int, tuning: List[str], frets: int
) -> Tuple[int, int] | None:
    """Return (string_index, fret) for the note or None if out of range."""
    tuning_midis = [note_to_midi(n) for n in tuning]
    for s, open_midi in enumerate(tuning_midis):
        fret = midi - open_midi
        if 0 <= fret <= frets:
            return s, fret
    return None


def build_positions(
    notes: List[str], tuning: List[str], frets: int
) -> List[dict]:
    positions = []
    for n in notes:
        try:
            midi = note_to_midi(n)
        except (ValueError, IndexError):
            continue
        pos = find_position(midi, tuning, frets)
        if pos:
            s, f = pos
            positions.append({"note": n, "string": s, "fret": f})
    return positions


HTML_TEMPLATE = """<!DOCTYPE html>
<html>
<head>
<meta charset='UTF-8'>
<title>Guitar Visualization</title>
<style>
#fretboard svg {{ border:1px solid #ccc; }}
</style>
</head>
<body>
<h2>Guitar Note Visualization</h2>
<div id='fretboard'></div>
<button onclick='prev()'>Prev</button>
<button onclick='next()'>Next</button>
<p id='label'></p>
<script>
const positions = {positions_json};
let index = 0;
const strings = {num_strings};
const frets = {num_frets};

function draw(pos) {{
  const width = 800;
  const height = 120;
  const sSpace = height/(strings+1);
  const fSpace = width/frets;
  let svg = `<svg width='${{width}}' height='${{height}}' xmlns='http://www.w3.org/2000/svg'>`;
  for (let s=1; s<=strings; s++) {{
    let y = sSpace*s;
    svg += `<line x1='0' y1='${{y}}' x2='${{width}}' y2='${{y}}' stroke='black'/>`;
  }}
  for (let f=0; f<=frets; f++) {{
    let x = fSpace*f;
    svg += `<line x1='${{x}}' y1='${{sSpace}}' x2='${{x}}' y2='${{sSpace*strings}}' stroke='gray'/>`;
  }}
  if (pos) {{
    const cx = fSpace*(pos.fret+0.5);
    const cy = sSpace*(pos.string+1);
    svg += `<circle cx='${{cx}}' cy='${{cy}}' r='${{sSpace*0.3}}' fill='red'/>`;
  }}
  svg += '</svg>';
  document.getElementById('fretboard').innerHTML = svg;
  document.getElementById('label').innerText = pos? pos.note : '';
}}
function next() {{ if (index<positions.length-1) index++; draw(positions[index]); }}
function prev() {{ if (index>0) index--; draw(positions[index]); }}
window.onload = function() {{ draw(positions[0]); }};
</script>
</body>
</html>
"""


def generate_html(
    positions: List[dict], num_strings: int, num_frets: int, out_file: str
) -> None:
    html = HTML_TEMPLATE.format(
        positions_json=json.dumps(positions),
        num_strings=num_strings,
        num_frets=num_frets,
    )
    with open(out_file, "w", encoding="utf-8") as f:
        f.write(html)
    print(f"Visualization written to {out_file}")


def main() -> None:
    import argparse

    parser = argparse.ArgumentParser(
        description="Generate guitar visualization"
    )
    parser.add_argument("notes_file", help="Text file containing note names")
    parser.add_argument(
        "--strings", type=int, default=6, help="Number of strings"
    )
    parser.add_argument(
        "--frets", type=int, default=24, help="Number of frets"
    )
    parser.add_argument(
        "--output", default="visualization.html", help="Output HTML file"
    )
    args = parser.parse_args()

    if not os.path.isfile(args.notes_file):
        raise SystemExit(f"File not found: {args.notes_file}")

    with open(args.notes_file, "r", encoding="utf-8") as f:
        text = f.read()
    notes = parse_notes(text)
    positions = build_positions(
        notes, STANDARD_TUNING[: args.strings], args.frets
    )
    if not positions:
        raise SystemExit("No valid notes found in file")
    generate_html(positions, args.strings, args.frets, args.output)


if __name__ == "__main__":
    main()
