---
name: pdf-to-markdown
description: Convert uploaded or repo-local PDFs to Markdown for Codex context using Marker with Gemini LLM cleanup and image descriptions.
---

# PDF To Markdown

Use this skill when the user asks to convert, extract, parse, summarize from, or make context from a PDF, especially when they mention Markdown, Marker, or using a PDF as Codex context.

## Workflow

1. Identify the PDF path.
   - If the user points to a repo file, use that path.
   - If the user uploaded a PDF and Codex exposes a local attachment path, use that path.
   - If no filesystem path is available, ask the user for the local PDF path.
2. Prefer a user-terminal workflow for conversion jobs.
   - Generate copy-paste terminal commands with the plugin's `scripts/print_commands.py` helper.
   - The helper detects the user's OS and prints PowerShell on Windows or POSIX shell commands on macOS/Linux.
   - Do not run long conversions inside the Codex turn unless the user explicitly asks Codex to run it.
   - Tell the user that first-time dependency installation and large PDFs may take 10+ minutes.
3. After the terminal command finishes, ask the user for the generated Markdown path or read the path printed by the script if it is available in context.
4. Read the generated Markdown file into context when the user wants to use the PDF content in the current conversation.

## Command Generation

When the user needs terminal commands, run the command generator from the installed plugin root or from this skill's plugin root. From this `SKILL.md` directory, the script is at `../../scripts/print_commands.py`.

Print API key setup commands:

```bash
python ../../scripts/print_commands.py setup
```

Print conversion commands for a PDF:

```bash
python ../../scripts/print_commands.py convert "C:\path\to\paper.pdf"
```

Print both setup and conversion commands:

```bash
python ../../scripts/print_commands.py all "C:\path\to\paper.pdf"
```

Pass conversion flags through the generator as needed:

```bash
python ../../scripts/print_commands.py convert "C:\path\to\paper.pdf" --page-range "0,5-10,20" --force-ocr
```

Paste the generated command block to the user. Do not hand-write OS-specific install or conversion snippets unless the generator is unavailable.

## Defaults

The converter defaults to:

- Marker LLM mode enabled.
- Gemini model `gemini-3.1-flash-lite`.
- `marker.services.gemini.GoogleGeminiService`.
- Markdown output.
- Image extraction disabled, so Marker replaces images with descriptions when LLM mode is active.
- Output next to the source PDF.
- No overwrite of an existing expected Markdown output unless `--overwrite` is passed.

## Credentials

The script uses `GOOGLE_API_KEY` or `GEMINI_API_KEY` from the live environment first. If neither is set, it reads the plugin-local `.env` file, which is ignored by git.

For Codex GUI usage, prefer having the user run the terminal setup command above. It avoids Codex process environment issues and keeps long-running conversions in the user's terminal.

From the plugin root, this is the underlying setup command:

```powershell
python .\scripts\set_api_key.py set
```

Do not store API keys in tracked repo files, plugin manifests, Markdown outputs, or command examples.
