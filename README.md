# Nick's Codex Plugins

Personal Codex plugin monorepo.

## Plugins

- `pdf-to-markdown`: Converts PDFs to Markdown with `datalab-to/marker`, using LLM mode by default with Gemini 3.1 Flash-Lite and image descriptions instead of extracted image files.

## Install In Codex

As a Git marketplace, add this GitHub repo with explicit sparse paths:

```powershell
codex plugin marketplace add git@github.com:NicoPowers/nicks-codex-plugins.git --sparse .agents/plugins/marketplace.json --sparse plugins/pdf-to-markdown
codex plugin add pdf-to-markdown@nicks-codex-plugins
```

Codex marketplace imports look for `.agents/plugins/marketplace.json`. The default Git sparse checkout may not include that hidden path, so the explicit `--sparse` arguments are required for this repo.

For a local filesystem install from this checkout:

```powershell
codex plugin marketplace add C:\Users\nicol\Documents\nicks-codex-plugins
codex plugin add pdf-to-markdown@nicks-codex-plugins
```

Start a new Codex thread after installing or updating the plugin so Codex can load the skill.

## PDF To Markdown Setup

Set one Gemini API key environment variable before running conversions:

```powershell
$env:GOOGLE_API_KEY = "your-api-key"
```

`GEMINI_API_KEY` is also accepted. If only `GEMINI_API_KEY` is set, the script forwards it to Marker as `GOOGLE_API_KEY`.

The first conversion creates `plugins/pdf-to-markdown/.venv` and installs `marker-pdf` there. The venv is ignored by git.

## Direct Script Usage

```powershell
python .\plugins\pdf-to-markdown\scripts\convert_pdf.py C:\path\to\file.pdf
```

By default, the generated Markdown is written next to the source PDF.
