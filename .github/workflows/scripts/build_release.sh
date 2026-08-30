#!/usr/bin/env bash
set -euo pipefail

python -m pip install --upgrade pip
python -m pip install -e . pyinstaller
python -m PyInstaller --onefile --name aivcs-cli run_cli.py

os_name="$(uname -s | tr '[:upper:]' '[:lower:]')"
arch_name="$(uname -m)"
output_dir="dist"
mkdir -p "$output_dir"

case "$os_name" in
  linux)
    binary_path="$output_dir/aivcs-cli"
    cp dist/aivcs-cli "$binary_path"
    zip -j "$output_dir/aivcs-cli-linux-${arch_name}.zip" "$binary_path" >/dev/null
    ;;
  darwin)
    binary_path="$output_dir/aivcs-cli"
    cp dist/aivcs-cli "$binary_path"
    zip -j "$output_dir/aivcs-cli-macos-${arch_name}.zip" "$binary_path" >/dev/null
    ;;
  *)
    echo "Unsupported platform: $os_name" >&2
    exit 1
    ;;
esac

echo "Built release artifact for ${os_name}/${arch_name}"
