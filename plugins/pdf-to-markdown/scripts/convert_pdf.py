from __future__ import annotations

import argparse
import os
import subprocess
import sys
import time
from pathlib import Path

from bootstrap_marker import BootstrapError, PLUGIN_ROOT, ensure_environment

DEFAULT_MODEL = "gemini-3.1-flash-lite"
LLM_SERVICE = "marker.services.gemini.GoogleGeminiService"
LOCAL_ENV_FILE = PLUGIN_ROOT / ".env"


def expected_outputs(pdf_path: Path, output_dir: Path) -> list[Path]:
    stem = pdf_path.stem
    return [
        output_dir / f"{stem}.md",
        output_dir / stem / f"{stem}.md",
    ]


def find_recent_markdown(output_dir: Path, started_at: float) -> list[Path]:
    if not output_dir.exists():
        return []
    matches = [
        path
        for path in output_dir.rglob("*.md")
        if path.is_file() and path.stat().st_mtime >= started_at - 1
    ]
    return sorted(matches, key=lambda path: path.stat().st_mtime, reverse=True)


def get_api_key() -> str | None:
    return (
        os.environ.get("GOOGLE_API_KEY")
        or os.environ.get("GEMINI_API_KEY")
        or read_local_env_key()
    )


def read_local_env_key() -> str | None:
    if not LOCAL_ENV_FILE.exists():
        return None

    for raw_line in LOCAL_ENV_FILE.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        if key.strip() not in {"GOOGLE_API_KEY", "GEMINI_API_KEY"}:
            continue
        value = value.strip().strip('"').strip("'")
        if value:
            return value
    return None


def build_marker_command(
    marker_path: Path,
    pdf_path: Path,
    output_dir: Path,
    *,
    model: str,
    page_range: str | None,
    force_ocr: bool,
) -> list[str]:
    command = [
        str(marker_path),
        str(pdf_path),
        "--output_format",
        "markdown",
        "--use_llm",
        "--llm_service",
        LLM_SERVICE,
        "--gemini_model_name",
        model,
        "--disable_image_extraction",
        "--output_dir",
        str(output_dir),
    ]

    if page_range:
        command.extend(["--page_range", page_range])
    if force_ocr:
        command.append("--force_ocr")

    return command


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Convert a PDF to Markdown with Marker using Gemini LLM cleanup.",
    )
    parser.add_argument("input_pdf", help="Path to the PDF to convert.")
    parser.add_argument("--output-dir", help="Directory for generated Markdown. Defaults to the PDF directory.")
    parser.add_argument("--page-range", help='Marker page range, for example "0,5-10,20".')
    parser.add_argument("--force-ocr", action="store_true", help="Force OCR processing in Marker.")
    parser.add_argument("--overwrite", action="store_true", help="Allow overwriting an existing expected Markdown file.")
    parser.add_argument("--model", default=DEFAULT_MODEL, help=f"Gemini model name. Default: {DEFAULT_MODEL}.")
    parser.add_argument("--upgrade-deps", action="store_true", help="Upgrade plugin dependencies before conversion.")
    parser.add_argument("--no-bootstrap", action="store_true", help="Use the existing plugin venv without installing dependencies.")
    args = parser.parse_args()

    pdf_path = Path(args.input_pdf).expanduser().resolve()
    if not pdf_path.exists():
        print(f"PDF does not exist: {pdf_path}", file=sys.stderr)
        return 2
    if not pdf_path.is_file() or pdf_path.suffix.lower() != ".pdf":
        print(f"Input must be a PDF file: {pdf_path}", file=sys.stderr)
        return 2

    api_key = get_api_key()
    if not api_key:
        print(
            "Set GOOGLE_API_KEY or GEMINI_API_KEY, or run scripts/set_api_key.py to store one in the plugin-local .env.",
            file=sys.stderr,
        )
        return 2

    output_dir = Path(args.output_dir).expanduser().resolve() if args.output_dir else pdf_path.parent
    output_dir.mkdir(parents=True, exist_ok=True)

    existing = [path for path in expected_outputs(pdf_path, output_dir) if path.exists()]
    if existing and not args.overwrite:
        paths = "\n".join(f"  {path}" for path in existing)
        print("Refusing to overwrite existing Markdown output. Pass --overwrite to replace:\n" + paths, file=sys.stderr)
        return 3

    try:
        marker_path = ensure_environment(install=not args.no_bootstrap, upgrade=args.upgrade_deps)
    except (BootstrapError, subprocess.CalledProcessError) as exc:
        print(f"Could not prepare Marker: {exc}", file=sys.stderr)
        return 1

    env = os.environ.copy()
    env["GOOGLE_API_KEY"] = api_key

    command = build_marker_command(
        marker_path,
        pdf_path,
        output_dir,
        model=args.model,
        page_range=args.page_range,
        force_ocr=args.force_ocr,
    )

    started_at = time.time()
    result = subprocess.run(command, cwd=str(pdf_path.parent), env=env, text=True, check=False)
    if result.returncode != 0:
        return result.returncode

    expected = [path for path in expected_outputs(pdf_path, output_dir) if path.exists()]
    outputs = expected or find_recent_markdown(output_dir, started_at)
    if outputs:
        print("Markdown output:")
        for path in outputs:
            print(path)
    else:
        print(f"Marker completed, but no Markdown file was found under {output_dir}", file=sys.stderr)
        return 4

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
