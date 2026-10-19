"""Cho phép `import src...` khi chạy pytest từ thư mục gốc repo."""
import pathlib
import sys

GOC = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(GOC))
