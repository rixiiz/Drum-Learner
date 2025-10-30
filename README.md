# Drum-Learner
Generate playable drum parts from scratch — or from any song — using Magenta's DrumRNN for practice and coordination, and visualize the result as real drum sheet music.

## Features
- AI Groove Generation (Magenta DrumRNN)
  - Generates 4-bar drum grooves (kick, snare, hats, cymbals, toms) using a pretrained model
  - Can also generate split sticking variations (left hand / right hand)
- Song Drum Transcription
  - User inputs a song and the model will generate the drum partition for the song
- Interactive Notation GUI
  - Outputs like a real drum partition
 
## How It Works
1. Input
    - Select option A (generate rhythms) or B (generate from song)
    - If A is selected then the user has to choose between grooves or split sticking variations
2. Sequence generation
    - Use DrumRNN to produce a drum sequence
3. Notation rendering
    - Converts DrumRNN's output into a real drum partition using LilyPond and displays it onto a GUI

## Setup
- Create a Python environment `pythono3 -m env env` `source venv/bin/activate`
- Install `requirements.txt` with `pip install requirements.txt`

## Progress Tracker
- Done with the rhythm generator
- Currently working on the GUI
