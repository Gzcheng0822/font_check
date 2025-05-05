# Font Check

A Python tool for inspecting `.ttf` font files, counting Unicode range coverage, and visualizing the results. Supports Chinese and English language packs, and comes with a simple Tkinter GUI.

## Features

- Inspect font metadata (name, copyright, version, etc.)
- Count characters in CJK, emoji, Greek, Cyrillic, Arabic, and more
- Visualize coverage in bar charts (with your selected font used for rendering)
- GUI with file picker and language switcher
- Exported as `.exe` with PyInstaller

## Requirements

- Python 3.8+
- matplotlib
- fonttools
- tkinter (usually bundled with Python)

## Quick start

```bash
pip install -r requirements.txt
python gui.py
```

## How to use

1. Download `gui.exe` from [Releases](https://github.com/Zhicheng-Gao/font_check/releases).
2. Run `gui.exe`.
3. Select a font and language.
4. View the results and charts.
