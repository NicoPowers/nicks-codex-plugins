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

When Codex is already running and cannot see newly-set shell environment variables, generate commands for storing the key in the installed plugin's gitignored `.env` file:

```powershell
python .\plugins\pdf-to-markdown\scripts\print_commands.py setup
```

The live environment still takes precedence over the plugin-local `.env`.

The first conversion creates `plugins/pdf-to-markdown/.venv` and installs `marker-pdf` there. The venv is ignored by git.

## Terminal Command Generator

The plugin includes a deterministic command generator. It detects the current OS and prints PowerShell commands on Windows or POSIX shell commands on macOS/Linux.

From this repo checkout:

```powershell
python .\plugins\pdf-to-markdown\scripts\print_commands.py setup
python .\plugins\pdf-to-markdown\scripts\print_commands.py convert "C:\path\to\file.pdf"
python .\plugins\pdf-to-markdown\scripts\print_commands.py all "C:\path\to\file.pdf" --page-range "0,5-10,20" --force-ocr
```

To preview another OS target, pass `--os windows` or `--os posix`.

## Terminal Conversion Usage

On Windows, the generated conversion command looks like this:

```powershell
$pluginBase = Join-Path $env:USERPROFILE ".codex\plugins\cache\nicks-codex-plugins\pdf-to-markdown"
$pluginRoot = Get-ChildItem -LiteralPath $pluginBase -Directory |
  Sort-Object LastWriteTime -Descending |
  Select-Object -First 1
python (Join-Path $pluginRoot.FullName "scripts\convert_pdf.py") "C:\path\to\file.pdf"
```

By default, the generated Markdown is written next to the source PDF.
