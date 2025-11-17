import subprocess
import sys
from pathlib import Path

def test_cli_help():
    res = subprocess.run([sys.executable, "main.py"], capture_output=True, text=True, input="5\n")
    assert res.returncode == 0
    assert "OCR & Image Enhancement Tool" in res.stdout


def test_enhance_writes_output(tmp_path: Path):
    # create a small image using Pillow
    from PIL import Image
    src_dir = tmp_path / "images"
    out_dir = tmp_path / "enh"
    src_dir.mkdir()
    out_dir.mkdir()

    img = Image.new("RGB", (10, 10), color=(255, 255, 255))
    img_path = src_dir / "tiny.jpg"
    img.save(img_path)

    # Choose option 1, then provide input and output directories
    user_input = f"1\n{src_dir}\n{out_dir}\n5\n"
    res = subprocess.run([sys.executable, "main.py"], capture_output=True, text=True, input=user_input)
    assert res.returncode == 0

    # expect an enhanced PNG file with suffix _enhanced.PNG
    files = list(out_dir.glob("*_enhanced.PNG"))
    assert len(files) == 1
