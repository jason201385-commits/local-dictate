# local-dictate

**English** · [繁體中文](README.md)

Click, speak, and the text appears wherever your cursor is. No word limit, no subscription.

**Your voice is turned into text entirely on your own machine and is never uploaded.** The only thing that ever leaves is the optional "cleanup" pass — and that sends the *already-transcribed text*, never the audio. One click on the panel turns it off.

Windows + Python, running [faster-whisper](https://github.com/SYSTRAN/faster-whisper). Tuned for **Traditional Chinese**, but the engine handles any language Whisper supports.

---

## Quick start (30 seconds)

<img src="docs/panel-guide.svg" alt="How the panel works" width="100%">

```mermaid
flowchart LR
    A["1. Click where you<br/>want to type"] --> B["2. Click the panel<br/>or press Ctrl+Alt+Z"]
    B --> C["3. Speak<br/>watch the level meter"]
    C --> D["4. Click / press again"]
    D --> E["5. Text lands where<br/>you clicked in step 1"]
    style A fill:#1f4e6b,stroke:#4a90b8,color:#fff
    style C fill:#8b1e1e,stroke:#c14b4b,color:#fff
    style E fill:#1e5f2e,stroke:#3fa057,color:#fff
```

> It's a **toggle, not push-to-talk**. Click once to start, speak, click again to stop.

---

## Why this exists

Cloud dictation services upload your audio, cap your word count, and charge monthly. The built-in voice input in some AI desktop apps doesn't support Traditional Chinese at all — speak Chinese, get English back.

And an MCP connector can't solve this: **a connector only runs after you submit a message**, so it can never reach the input box you haven't submitted yet. The input layer has to live at the OS level.

So this is a local one.

---

## Features

- **Audio stays on your machine.** Recording and transcription both run locally. Works with no internet.
- **Model stays in memory.** Loaded once at startup — every dictation after that is instant.
- **No hotkey to memorise.** A small panel sits in the corner of your screen. Click to start, click to stop.
- **Traditional Chinese first.** Forced zh-TW prompt plus OpenCC conversion as a safety net.
- **Custom vocabulary.** Put your brand names, project codenames and jargon in `vocab.txt` — recognition improves immediately, and casing gets normalised automatically.
- **Optional cleanup pass.** Strips filler words, adds punctuation, and keeps only your final wording when you correct yourself mid-sentence.
- **You can see where the text will go.** While recording, the panel shows the target window and a live input-level meter. Right-click cancels.

---

## Install

```bash
git clone https://github.com/jason201385-commits/local-dictate.git
cd local-dictate
pip install -r requirements.txt
cp vocab.example.txt vocab.txt
```

Then **run the doctor before starting anything**:

```bash
python doctor.py
```

It checks your OS, Python version, every dependency, tkinter, GPU and CUDA, **Windows microphone permission**, your input device (with a real half-second test recording), the model cache, free disk space, API key and folder write access — and tells you exactly how to fix whatever is missing.

### Let it pick your settings

```bash
python tune.py            # profile the machine, recommend settings (instant)
python tune.py --bench    # actually benchmark on your machine
python tune.py --apply    # write the result into config.json
```

`--bench` synthesises a short speech sample with your OS's built-in TTS, runs the candidate models, and picks **the largest model your machine can transcribe in under 2.5 seconds**. No spec-sheet guesswork.

Start it with `啟動口述.bat`. `建立快捷鍵.bat` adds a `Ctrl+Alt+V` global shortcut to launch/recall it, plus run-at-logon.

---

## Requirements

| Requirement | Hard? | If missing |
|---|---|---|
| **Windows** | 🔴 yes | Won't run. The whole OS-integration layer is Win32. See [docs/macos.md](docs/macos.md) for a porting map |
| **Python 3.10+** | 🔴 yes | — |
| **Microphone + Windows mic permission** | 🔴 yes | Silent failure — the permission one is easy to miss |
| **~3 GB disk + internet for first download** | 🔴 yes | Model download fails |
| NVIDIA GPU | 🟡 optional | Falls back to CPU, roughly 5× slower |

---

## Measured numbers

Same **11-second Chinese clip**. Your machine will differ — these are here so you can calibrate.

**With an NVIDIA GPU** (RTX 4050 Laptop, 6 GB):

| Setting | Time |
|---|---|
| `medium` + beam 5 | **1.2 s** (default) |
| `medium` + beam 1 | 0.99 s — ⚠️ mangles English brand names, not worth it |
| `large-v3` + beam 5 | 1.95 s |
| `large-v3` + beam 1 | 1.61 s |

**CPU only** (22 logical cores — fewer cores will be slower):

| Model | Time | Quality |
|---|---|---|
| `medium` | 6.7 s | Good, but you feel the wait |
| `small` | **3.3 s** | Sentences fine, English proper nouns drift → **pick this without a GPU** |
| `base` | 1.2 s | Noticeably worse |

---

## Privacy

| Data | Where it goes |
|---|---|
| **Your voice** | **Never leaves the machine.** No exceptions |
| Screen contents / which app you're in | **Never sent anywhere.** Some commercial dictation tools send this as context — this one does not |
| Transcribed text | Local by default. **Only** when the cleanup pass is on does that text go to the cleanup model |
| `dictate.log` | Local only. Records the first 40 characters of each result plus window titles |

**To stay fully offline**, set `polish.enabled` to `false` in `config.json`, or click the `✨` toggle on the panel until it goes grey. Nothing else changes.

---

## Use it as a Claude Code skill

One repo, two uses. Clone it into your skills directory and Claude can install, tune and debug it for you:

```bash
git clone https://github.com/jason201385-commits/local-dictate.git ~/.claude/skills/local-dictate
```

`SKILL.md` is deliberately short (it loads into context every time) and routes to `references/` on demand.

---

## The pitfalls doc is worth reading even if you never use this

[`references/pitfalls.md`](references/pitfalls.md) documents 11 problems that took a full day to track down. **Most are not specific to this project** — they apply to any Windows desktop automation, or any feature that pipes user content through an LLM:

- Global hotkeys registered via low-level hooks **leak characters into the target app** (`Ctrl+Alt` is AltGr on Windows; Qt apps type it as text). Changing the letter doesn't help.
- Reopening an audio stream repeatedly yields a stream that **opens fine but records pure silence** — and Whisper hallucinates confident sentences from silence.
- An LLM cleanup pass will **execute instructions found inside the user's content**. 18 seconds of dictation came back as a 1,998-character spec document that replaced the original. Prompting alone doesn't hold; you need a hard length ceiling in code.
- `SetForegroundWindow` is blocked by the foreground lock and **fails silently**.
- `.gitignore` doesn't support trailing comments — the rule silently stops matching.

The umbrella lesson: **"it works sometimes" is usually not one bug.** Before asking "why doesn't it work", ask "when does it work and when doesn't it".

---

## Contributing

The most useful thing you can send right now is **real numbers from your machine**: run `python tune.py` and open an issue with the output. The hardware table above only has one machine in it, and [docs/macos.md](docs/macos.md) has none.

macOS port: the transcription core is already cross-platform. What's missing is the OS-integration layer — the map is in [docs/macos.md](docs/macos.md).

---

## License

MIT. Take it, change it, sell it.
