# -*- coding: utf-8 -*-
"""Local OCR fallback: extract text from images without any cloud API.

Tries Windows.Media.Ocr (built into Windows 10+) or Tesseract CLI.
Returns a plain-text string, or None if no backend is available.
This module is pure stdlib -- no pip dependencies.
"""
import json
import os
import shutil
import subprocess
import sys


def _windows_ocr(image_path):
    """Use Windows.Media.Ocr via PowerShell. Returns text or None."""
    if os.name != "nt":
        return None
    # PowerShell script: load the image, run OCR, output JSON.
    # We inline it rather than using a separate .ps1 file.
    ps_script = r'''
$ErrorActionPreference = "Stop"
Add-Type -AssemblyName System.Runtime.WindowsRuntime
$asTask = ([System.WindowsRuntimeSystemExtensions].GetMethods() | ? {
    $_.Name -eq 'AsTask' -and $_.GetParameters().Count -eq 1 -and
    $_.GetParameters()[0].ParameterType.Name -eq 'IAsyncOperation`1'
})[0]
function Await($op, $t) {
    $netTask = $asTask.MakeGenericMethod($t).Invoke($null, @($op))
    $netTask.Wait(-1) | Out-Null
    $netTask.Result
}
try {
    [Windows.Media.Ocr.OcrEngine, Windows.Media.Ocr, ContentType=WindowsRuntime] | Out-Null
    [Windows.Graphics.Imaging.BitmapDecoder, Windows.Graphics.Imaging, ContentType=WindowsRuntime] | Out-Null
    $stream = [System.IO.File]::OpenRead($args[0])
    $bmp = Await ([Windows.Graphics.Imaging.BitmapDecoder]::CreateAsync(
        [Windows.Storage.Streams.RandomAccessStream]::CreateAsync($stream).GetResults())) ([Windows.Graphics.Imaging.BitmapDecoder])
    $fmt = Await ($bmp.GetSoftwareBitmapAsync()) ([Windows.Graphics.Imaging.SoftwareBitmap])
    $engine = [Windows.Media.Ocr.OcrEngine]::TryCreateFromUserProfileLanguages()
    $result = Await ($engine.RecognizeAsync($fmt)) ([Windows.Media.Ocr.OcrResult])
    $stream.Close()
    $result.Text
} catch {
    Write-Error $_.Exception.Message
    exit 1
}
'''
    try:
        result = subprocess.run(
            ["powershell", "-NoProfile", "-NonInteractive",
             "-Command", ps_script, "-", image_path],
            capture_output=True, text=True, timeout=30)
        if result.returncode == 0 and result.stdout.strip():
            return result.stdout.strip()
    except (subprocess.TimeoutExpired, FileNotFoundError, OSError):
        pass
    return None


def _tesseract_ocr(image_path):
    """Use Tesseract CLI. Returns text or None."""
    tesseract = shutil.which("tesseract")
    if not tesseract:
        return None
    try:
        result = subprocess.run(
            [tesseract, image_path, "stdout", "-l", "eng"],
            capture_output=True, text=True, timeout=30)
        if result.returncode == 0 and result.stdout.strip():
            return result.stdout.strip()
    except (subprocess.TimeoutExpired, OSError):
        pass
    return None


def local_ocr(image_path):
    """Try all local OCR backends in order. Returns text or None.

    Chain: Windows OCR -> Tesseract.
    """
    for backend_name, backend_fn in [
        ("windows_ocr", _windows_ocr),
        ("tesseract", _tesseract_ocr),
    ]:
        text = backend_fn(image_path)
        if text:
            print("[ocr] text extracted via {}".format(backend_name),
                  file=sys.stderr)
            return text
    return None


def local_ocr_available():
    """Check if any local OCR backend is available."""
    if os.name == "nt":
        powershell = shutil.which("powershell")
        if powershell:
            return True
    if shutil.which("tesseract"):
        return True
    return False


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Local OCR text extraction.")
    parser.add_argument("image", help="Path to image file")
    args = parser.parse_args()
    text = local_ocr(args.image)
    if text:
        print(text)
    else:
        print("No local OCR backend available.", file=sys.stderr)
        sys.exit(1)
