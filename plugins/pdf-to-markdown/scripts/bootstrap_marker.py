from __future__ import annotations

import argparse
import os
import shlex
import subprocess
import sys
from pathlib import Path
from typing import Iterable, Sequence

PLUGIN_ROOT = Path(__file__).resolve().parents[1]
VENV_DIR = PLUGIN_ROOT / ".venv"
REQUIREMENTS_FILE = PLUGIN_ROOT / "requirements.txt"
MIN_PYTHON = (3, 10)
MAX_PYTHON_EXCLUSIVE = (3, 13)


class BootstrapError(RuntimeError):
    pass


def venv_python() -> Path:
    if os.name == "nt":
        return VENV_DIR / "Scripts" / "python.exe"
    return VENV_DIR / "bin" / "python"


def marker_single_path() -> Path:
    if os.name == "nt":
        return VENV_DIR / "Scripts" / "marker_single.exe"
    return VENV_DIR / "bin" / "marker_single"


def _run(command: Sequence[str], *, check: bool = True) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        list(command),
        cwd=str(PLUGIN_ROOT),
        text=True,
        check=check,
    )


def _capture(command: Sequence[str]) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        list(command),
        cwd=str(PLUGIN_ROOT),
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )


def _python_version(command: Sequence[str]) -> tuple[int, int, int] | None:
    probe = _capture(
        [
            *command,
            "-c",
            "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}')",
        ]
    )
    if probe.returncode != 0:
        return None
    try:
        parts = probe.stdout.strip().split(".")
        return int(parts[0]), int(parts[1]), int(parts[2])
    except (IndexError, ValueError):
        return None


def _supported(version: tuple[int, int, int]) -> bool:
    return MIN_PYTHON <= version[:2] < MAX_PYTHON_EXCLUSIVE


def _candidate_commands() -> Iterable[list[str]]:
    override = os.environ.get("PDF_TO_MARKDOWN_PYTHON")
    if override:
        yield shlex.split(override)

    yield [sys.executable]

    codex_python = (
        Path.home()
        / ".cache"
        / "codex-runtimes"
        / "codex-primary-runtime"
        / "dependencies"
        / "python"
        / "python.exe"
    )
    if codex_python.exists():
        yield [str(codex_python)]

    if os.name == "nt":
        yield ["py", "-3.12"]
        yield ["py", "-3.11"]
        yield ["py", "-3.10"]

    yield ["python3.12"]
    yield ["python3.11"]
    yield ["python3.10"]
    yield ["python3"]
    yield ["python"]


def select_base_python() -> tuple[list[str], tuple[int, int, int]]:
    seen: set[tuple[str, ...]] = set()
    rejected: list[str] = []

    for command in _candidate_commands():
        key = tuple(part.lower() for part in command)
        if key in seen:
            continue
        seen.add(key)

        version = _python_version(command)
        if version is None:
            continue
        label = " ".join(command)
        if _supported(version):
            return command, version
        rejected.append(f"{label} ({version[0]}.{version[1]}.{version[2]})")

    rejected_text = ", ".join(rejected) if rejected else "none found"
    raise BootstrapError(
        "Could not find a supported Python for Marker. "
        "Use Python 3.10, 3.11, or 3.12, or set PDF_TO_MARKDOWN_PYTHON. "
        f"Rejected candidates: {rejected_text}"
    )


def create_venv() -> None:
    base_command, version = select_base_python()
    print(
        "Creating plugin venv with "
        f"{' '.join(base_command)} ({version[0]}.{version[1]}.{version[2]})"
    )
    _run([*base_command, "-m", "venv", str(VENV_DIR)])


def marker_is_ready() -> bool:
    python_path = venv_python()
    marker_path = marker_single_path()
    if not python_path.exists() or not marker_path.exists():
        return False
    probe = _capture([str(python_path), "-c", "import marker"])
    return probe.returncode == 0


def install_requirements(*, upgrade: bool = False) -> None:
    python_path = venv_python()
    if not python_path.exists():
        raise BootstrapError(f"Missing venv Python at {python_path}")
    if not REQUIREMENTS_FILE.exists():
        raise BootstrapError(f"Missing requirements file at {REQUIREMENTS_FILE}")

    command = [str(python_path), "-m", "pip", "install", "-r", str(REQUIREMENTS_FILE)]
    if upgrade:
        command.insert(4, "--upgrade")
    print("Installing Marker dependencies into plugin venv")
    _run(command)


def ensure_environment(*, install: bool = True, upgrade: bool = False) -> Path:
    if not venv_python().exists():
        create_venv()

    if install and (upgrade or not marker_is_ready()):
        install_requirements(upgrade=upgrade)

    marker_path = marker_single_path()
    if install and not marker_path.exists():
        raise BootstrapError(f"Marker CLI was not found after install: {marker_path}")
    if not install and not marker_path.exists():
        raise BootstrapError(f"Marker CLI is not installed in the plugin venv: {marker_path}")
    return marker_path


def main() -> int:
    parser = argparse.ArgumentParser(description="Bootstrap Marker for the PDF to Markdown plugin.")
    parser.add_argument("--check", action="store_true", help="Check whether the local Marker venv is ready.")
    parser.add_argument("--create-venv-only", action="store_true", help="Create the venv without installing Marker.")
    parser.add_argument("--upgrade", action="store_true", help="Upgrade installed requirements.")
    args = parser.parse_args()

    try:
        if args.check:
            if marker_is_ready():
                print(f"Marker is ready: {marker_single_path()}")
                return 0
            print(f"Marker is not ready in {VENV_DIR}", file=sys.stderr)
            return 1

        if args.create_venv_only:
            if not venv_python().exists():
                create_venv()
            print(f"Venv is available: {venv_python()}")
            return 0

        marker_path = ensure_environment(install=True, upgrade=args.upgrade)
        print(f"Marker is ready: {marker_path}")
        return 0
    except (BootstrapError, subprocess.CalledProcessError) as exc:
        print(f"Bootstrap failed: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
