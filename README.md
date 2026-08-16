# MP3Conversation

A Windows app that turns a **text dialogue script** into an **MP3 file with free AI voices** in English.

The voices come from the Microsoft Edge read-aloud service ([edge-tts](https://github.com/rany2/edge-tts) library) — high-quality neural voices, **free of charge and with no practical usage limit**. An internet connection is required during generation.

## How to use

1. Double-click **`MP3Conversation.bat`** (or run `python mp3conversation.py`).
2. Paste your script into the text area, or click **Open script…** to load a `.txt` file (see `example_dialogue.txt`).
3. Click **Detect characters** — each character appears on the right with a suggested voice, which you can change.
4. Click **▶ Generate MP3** and choose where to save. While generating, the button is disabled and a **progress bar** shows the progress line by line; when it finishes, the button is enabled again.

Listen to `example_dialogue.mp3` to hear the result of the example script (a conversation about buying clothes).

## Script format

```
# Comment (ignored)
A line without a colon becomes narration, read by the "Narrator" voice.
Sarah: Line spoken by Sarah.
Clerk: Line spoken by the clerk.
```

## Available voices

The app includes **all 47 English neural voices** from the service, organized by region:

| Region | Voices |
|---|---|
| United States | Jenny, Guy, Aria, Andrew, Ava, Brian, Emma, Christopher, Michelle, Eric, Ana (child), Roger, Steffan + multilingual variants |
| United Kingdom | Sonia, Ryan, Libby, Thomas, Maisie (child) |
| Australia | Natasha, William |
| Canada | Clara, Liam |
| Ireland | Emily, Connor |
| India | Neerja, Neerja Expressive, Prabhat |
| New Zealand | Molly, Mitchell |
| Hong Kong | Yan, Sam |
| Singapore | Luna, Wayne |
| Philippines | Rosa, James |
| South Africa | Leah, Luke |
| Kenya | Asilia, Chilemba |
| Nigeria | Ezinne, Abeo |
| Tanzania | Imani, Elimu |

To see the service's full voice list (hundreds, in many languages):
`python -m edge_tts --list-voices`

## Requirements

- Windows with **Python 3.12** (installed at `%LOCALAPPDATA%\Programs\Python\Python312`)
- **edge-tts** library: `python -m pip install edge-tts`
- Internet connection during generation
