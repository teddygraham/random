# Guitar Note Visualizer

This simple command line program generates an interactive HTML
visualization of guitar notes. The tool expects a text file with
space or newline separated note names (e.g. `E2 F#2 G2`). Each note is
mapped to a position on a guitar fretboard using standard tuning.

## Usage

```
python visualizer.py notes.txt --strings 6 --frets 24 --output output.html
```

Open `output.html` in a browser to step through each note. Use the
**Prev** and **Next** buttons to navigate.

`notes.txt` should contain note names such as `E2`, `F#3` or
`Bb4`. Notes that cannot be played on the selected guitar range are
skipped.
