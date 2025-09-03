# ReadToMe

![Status: Prototype](https://img.shields.io/badge/status-prototype-yellow)
![Python](https://img.shields.io/pypi/pyversions/fastapi)

ReadToMe converts web articles into speech using Kokoro TTS. Post a URL to the `/tts` endpoint and get back an `audio/wav` file you can play in the browser or save locally.

---

## Demo
_(Add an animated GIF or short screencast here showing `curl` -> save -> play audio)_

---

## Table of contents
- [Quick start](#quick-start)
- [API](#api)
- [Installation](#installation)
- [Usage examples](#usage-examples)
- [Configuration & environment](#configuration--environment)
- [Development & testing](#development--testing)
- [Roadmap](#roadmap)
- [Contributing](#contributing)
- [License](#license)

---

## Quick start

Run locally (recommended use for development):

```bash
pip install -r requirements.txt
uvicorn main:app --reload --port 8000
