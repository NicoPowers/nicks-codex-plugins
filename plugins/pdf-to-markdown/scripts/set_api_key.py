from __future__ import annotations

import argparse
import getpass
import os
import stat
import sys
from pathlib import Path

PLUGIN_ROOT = Path(__file__).resolve().parents[1]
ENV_FILE = PLUGIN_ROOT / ".env"
KEY_NAMES = ("GOOGLE_API_KEY", "GEMINI_API_KEY")


def parse_env_file() -> tuple[list[str], dict[str, str]]:
    lines: list[str] = []
    values: dict[str, str] = {}
    if not ENV_FILE.exists():
        return lines, values

    lines = ENV_FILE.read_text(encoding="utf-8").splitlines()
    for line in lines:
        stripped = line.strip()
        if not stripped or stripped.startswith("#") or "=" not in stripped:
            continue
        key, value = stripped.split("=", 1)
        key = key.strip()
        if key in KEY_NAMES:
            values[key] = value.strip().strip('"').strip("'")
    return lines, values


def write_key(api_key: str, *, key_name: str = "GOOGLE_API_KEY") -> None:
    if not api_key.strip():
        raise ValueError("API key cannot be empty.")

    lines, _ = parse_env_file()
    output: list[str] = []
    wrote = False

    for line in lines:
        stripped = line.strip()
        if "=" in stripped and stripped.split("=", 1)[0].strip() in KEY_NAMES:
            if not wrote:
                output.append(f"{key_name}={api_key.strip()}")
                wrote = True
            continue
        output.append(line)

    if not wrote:
        if output and output[-1].strip():
            output.append("")
        output.append("# Local PDF-to-Markdown plugin secrets. Do not commit this file.")
        output.append(f"{key_name}={api_key.strip()}")

    ENV_FILE.write_text("\n".join(output) + "\n", encoding="utf-8")
    if os.name != "nt":
        ENV_FILE.chmod(stat.S_IRUSR | stat.S_IWUSR)


def clear_key() -> bool:
    if not ENV_FILE.exists():
        return False

    lines, _ = parse_env_file()
    output = [
        line
        for line in lines
        if not ("=" in line.strip() and line.strip().split("=", 1)[0].strip() in KEY_NAMES)
    ]
    if any(line.strip() for line in output):
        ENV_FILE.write_text("\n".join(output).rstrip() + "\n", encoding="utf-8")
    else:
        ENV_FILE.unlink()
    return True


def masked(value: str) -> str:
    if len(value) <= 8:
        return "*" * len(value)
    return f"{value[:4]}...{value[-4:]}"


def show_key() -> int:
    _, values = parse_env_file()
    for key_name in KEY_NAMES:
        if values.get(key_name):
            print(f"{key_name} is set in {ENV_FILE}: {masked(values[key_name])}")
            return 0
    print(f"No plugin-local API key is set in {ENV_FILE}")
    return 1


def main() -> int:
    parser = argparse.ArgumentParser(description="Manage the plugin-local Gemini API key.")
    subparsers = parser.add_subparsers(dest="command", required=True)

    set_parser = subparsers.add_parser("set", help="Store an API key in the plugin-local .env file.")
    set_parser.add_argument("--api-key", help="API key to store. Omit to enter it in a hidden prompt.")
    set_parser.add_argument(
        "--key-name",
        choices=KEY_NAMES,
        default="GOOGLE_API_KEY",
        help="Environment key name to write. Default: GOOGLE_API_KEY.",
    )

    subparsers.add_parser("show", help="Show whether a plugin-local key is configured.")
    subparsers.add_parser("clear", help="Remove plugin-local API keys.")

    args = parser.parse_args()

    try:
        if args.command == "set":
            api_key = args.api_key
            if api_key is None:
                api_key = getpass.getpass("Gemini API key: ")
            write_key(api_key, key_name=args.key_name)
            print(f"Stored {args.key_name} in {ENV_FILE}")
            return 0

        if args.command == "show":
            return show_key()

        if args.command == "clear":
            if clear_key():
                print(f"Removed plugin-local API key from {ENV_FILE}")
            else:
                print(f"No plugin-local .env file exists at {ENV_FILE}")
            return 0
    except Exception as exc:
        print(f"Failed to update plugin-local API key: {exc}", file=sys.stderr)
        return 1

    parser.error(f"Unknown command: {args.command}")
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
