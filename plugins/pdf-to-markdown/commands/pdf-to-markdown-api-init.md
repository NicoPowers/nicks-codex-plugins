---
description: Store the Gemini API key for the PDF-to-Markdown plugin without requiring Codex to restart.
---

# PDF To Markdown API Init

Store the Gemini API key in the installed PDF-to-Markdown plugin's gitignored `.env` file.

## Preflight

- Treat `$ARGUMENTS` as the API key.
- Never print, quote, summarize, or expose the API key value.
- If `$ARGUMENTS` is empty, ask the user to rerun `/pdf-to-markdown-api-init <API_KEY>`.
- Use the newest installed `pdf-to-markdown` plugin version under the local Codex plugin cache.

## Plan

1. Resolve the installed plugin root.
2. Pass the API key to `scripts/set_api_key.py set`.
3. Verify with `scripts/set_api_key.py show`, which prints only a masked key.

## Commands

Run this PowerShell snippet without echoing the API key:

```powershell
$apiKey = @'
$ARGUMENTS
'@.Trim()
if (-not $apiKey) {
  throw "Missing API key. Run /pdf-to-markdown-api-init <API_KEY>."
}

$pluginBase = Join-Path $env:USERPROFILE ".codex\plugins\cache\nicks-codex-plugins\pdf-to-markdown"
if (-not (Test-Path -LiteralPath $pluginBase)) {
  throw "The pdf-to-markdown plugin is not installed. Install it, start a new thread, then rerun this command."
}

$pluginRoot = Get-ChildItem -LiteralPath $pluginBase -Directory |
  Sort-Object LastWriteTime -Descending |
  Select-Object -First 1
if (-not $pluginRoot) {
  throw "No installed pdf-to-markdown plugin version was found under $pluginBase."
}

python (Join-Path $pluginRoot.FullName "scripts\set_api_key.py") set --api-key $apiKey
python (Join-Path $pluginRoot.FullName "scripts\set_api_key.py") show
```

## Verification

- Confirm the `show` command reports `GOOGLE_API_KEY is set`.
- Confirm the displayed key is masked.
- Do not reveal the actual key.

## Summary

Report only:

```text
PDF-to-Markdown API key stored for the installed plugin.
```

Do not include the key value.

## Next Steps

The current Codex process does not need to be reopened. Future PDF conversions can read the plugin-local `.env`.
