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
2. Run the converter script from the plugin root:

```powershell
python .\scripts\convert_pdf.py <path-to-pdf>
```

3. Read the generated Markdown file into context when the user wants to use the PDF content in the current conversation.

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

The script requires either `GOOGLE_API_KEY` or `GEMINI_API_KEY` in the environment. Do not store API keys in repo files, plugin files, Markdown outputs, or command examples.

## Useful Commands

Convert a PDF:

```powershell
python .\scripts\convert_pdf.py C:\path\to\paper.pdf
```

Convert selected pages:

```powershell
python .\scripts\convert_pdf.py C:\path\to\paper.pdf --page-range "0,5-10,20"
```

Force OCR:

```powershell
python .\scripts\convert_pdf.py C:\path\to\paper.pdf --force-ocr
```

Use a different Gemini model:

```powershell
python .\scripts\convert_pdf.py C:\path\to\paper.pdf --model gemini-3.5-flash
```
