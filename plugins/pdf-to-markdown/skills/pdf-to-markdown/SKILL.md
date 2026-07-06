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
   - Give the user copy-paste PowerShell commands that locate the installed plugin, store the API key if needed, and run the converter.
   - Do not run long conversions inside the Codex turn unless the user explicitly asks Codex to run it.
   - Tell the user that first-time dependency installation and large PDFs may take 10+ minutes.
3. After the terminal command finishes, ask the user for the generated Markdown path or read the path printed by the script if it is available in context.
4. Read the generated Markdown file into context when the user wants to use the PDF content in the current conversation.

## Terminal Commands

Give this setup command when the user needs to configure their Gemini API key:

```powershell
$pluginBase = Join-Path $env:USERPROFILE ".codex\plugins\cache\nicks-codex-plugins\pdf-to-markdown"
$pluginRoot = Get-ChildItem -LiteralPath $pluginBase -Directory |
  Sort-Object LastWriteTime -Descending |
  Select-Object -First 1
python (Join-Path $pluginRoot.FullName "scripts\set_api_key.py") set
```

Give this conversion command, replacing the PDF path:

```powershell
$pluginBase = Join-Path $env:USERPROFILE ".codex\plugins\cache\nicks-codex-plugins\pdf-to-markdown"
$pluginRoot = Get-ChildItem -LiteralPath $pluginBase -Directory |
  Sort-Object LastWriteTime -Descending |
  Select-Object -First 1
python (Join-Path $pluginRoot.FullName "scripts\convert_pdf.py") "C:\path\to\paper.pdf"
```

For selected pages:

```powershell
python (Join-Path $pluginRoot.FullName "scripts\convert_pdf.py") "C:\path\to\paper.pdf" --page-range "0,5-10,20"
```

For OCR-heavy PDFs:

```powershell
python (Join-Path $pluginRoot.FullName "scripts\convert_pdf.py") "C:\path\to\paper.pdf" --force-ocr
```

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
