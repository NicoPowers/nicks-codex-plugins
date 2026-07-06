from __future__ import annotations

import argparse
import platform
import shlex
from pathlib import PurePosixPath, PureWindowsPath


PLUGIN_MARKETPLACE = "nicks-codex-plugins"
PLUGIN_NAME = "pdf-to-markdown"


def detect_os() -> str:
    if platform.system().lower().startswith("win"):
        return "windows"
    return "posix"


def quote_powershell(value: str) -> str:
    return "'" + value.replace("'", "''") + "'"


def quote_posix(value: str) -> str:
    return shlex.quote(value)


def windows_preamble() -> list[str]:
    cache_path = rf".codex\plugins\cache\{PLUGIN_MARKETPLACE}\{PLUGIN_NAME}"
    return [
        rf"$pluginBase = Join-Path $env:USERPROFILE {quote_powershell(cache_path)}",
        "$pluginRoot = Get-ChildItem -LiteralPath $pluginBase -Directory |",
        "  Sort-Object LastWriteTime -Descending |",
        "  Select-Object -First 1",
        "if (-not $pluginRoot) { throw \"The pdf-to-markdown plugin is not installed.\" }",
    ]


def posix_preamble() -> list[str]:
    cache_path = f".codex/plugins/cache/{PLUGIN_MARKETPLACE}/{PLUGIN_NAME}"
    return [
        f"plugin_base=\"$HOME/{cache_path}\"",
        "plugin_root=$(find \"$plugin_base\" -mindepth 1 -maxdepth 1 -type d -print0 | xargs -0 ls -td | head -n 1)",
        "test -n \"$plugin_root\" || { echo \"The pdf-to-markdown plugin is not installed.\" >&2; exit 1; }",
    ]


def windows_python_script(script_name: str) -> str:
    script_path = "scripts\\" + script_name
    return f"python (Join-Path $pluginRoot.FullName {quote_powershell(script_path)})"


def posix_python_script(script_name: str) -> str:
    return f"python3 \"$plugin_root/scripts/{script_name}\""


def convert_args(args: argparse.Namespace, os_name: str) -> list[str]:
    quote = quote_powershell if os_name == "windows" else quote_posix
    parts = [quote(args.input_pdf)]
    if args.output_dir:
        parts.extend(["--output-dir", quote(args.output_dir)])
    if args.page_range:
        parts.extend(["--page-range", quote(args.page_range)])
    if args.force_ocr:
        parts.append("--force-ocr")
    if args.overwrite:
        parts.append("--overwrite")
    if args.model:
        parts.extend(["--model", quote(args.model)])
    return parts


def setup_commands(os_name: str) -> tuple[str, list[str]]:
    if os_name == "windows":
        lines = windows_preamble()
        lines.append(windows_python_script("set_api_key.py") + " set")
        lines.append(windows_python_script("set_api_key.py") + " show")
        return "powershell", lines

    lines = posix_preamble()
    lines.append(posix_python_script("set_api_key.py") + " set")
    lines.append(posix_python_script("set_api_key.py") + " show")
    return "bash", lines


def convert_commands(args: argparse.Namespace, os_name: str) -> tuple[str, list[str]]:
    if not args.input_pdf:
        raise ValueError("convert commands require input_pdf.")

    if os_name == "windows":
        lines = windows_preamble()
        command = windows_python_script("convert_pdf.py")
    else:
        lines = posix_preamble()
        command = posix_python_script("convert_pdf.py")

    command += " " + " ".join(convert_args(args, os_name))
    lines.append(command)
    return ("powershell" if os_name == "windows" else "bash"), lines


def print_block(shell: str, title: str, lines: list[str]) -> None:
    print(title)
    print()
    print(f"```{shell}")
    for line in lines:
        print(line)
    print("```")


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Print OS-specific terminal commands for the PDF-to-Markdown plugin.",
    )
    parser.add_argument(
        "action",
        choices=("setup", "convert", "all"),
        help="Which command block to print.",
    )
    parser.add_argument("input_pdf", nargs="?", help="PDF path for convert/all command output.")
    parser.add_argument("--output-dir", help="Directory for generated Markdown.")
    parser.add_argument("--page-range", help='Marker page range, for example "0,5-10,20".')
    parser.add_argument("--force-ocr", action="store_true", help="Include --force-ocr in conversion commands.")
    parser.add_argument("--overwrite", action="store_true", help="Include --overwrite in conversion commands.")
    parser.add_argument("--model", help="Include an explicit Gemini model override.")
    parser.add_argument(
        "--os",
        choices=("auto", "windows", "posix"),
        default="auto",
        help="Target shell OS. Defaults to auto-detecting the current OS.",
    )
    args = parser.parse_args()

    os_name = detect_os() if args.os == "auto" else args.os

    if args.action in {"setup", "all"}:
        shell, lines = setup_commands(os_name)
        print_block(shell, "API key setup command:", lines)

    if args.action in {"convert", "all"}:
        try:
            shell, lines = convert_commands(args, os_name)
        except ValueError as exc:
            parser.error(str(exc))
        if args.action == "all":
            print()
        print_block(shell, "PDF conversion command:", lines)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
