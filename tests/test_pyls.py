# tests/test_pyls.py
import pytest
from pyls.pyls import list_top_level_files


def test_list_files():
    # Assume this is a sample directory structure
    sample_structure = {
        "name": "interpreter",
        "size": 4096,
        "time_modified": 1699957865,
        "permissions": "-rw-r--r--",
        "contents": [
            {"name": "LICENSE", "size": 1071, "time_modified": 1699941437, "permissions": "drwxr-xr-x"},
            {"name": "README.md", "size": 83, "time_modified": 1699941437, "permissions": "drwxr-xr-x"}
        ]
    }
    result = list_top_level_files(sample_structure, show_all=False)
    assert result == ['LICENSE', 'README.md']


def test_hidden_files():
    sample_structure = {
        "name": "interpreter",
        "size": 4096,
        "time_modified": 1699957865,
        "permissions": "-rw-r--r--",
        "contents": [
            {"name": ".gitignore", "size": 8911, "time_modified": 1699941437, "permissions": "drwxr-xr-x"},
            {"name": "LICENSE", "size": 1071, "time_modified": 1699941437, "permissions": "drwxr-xr-x"}
        ]
    }

    result = list_top_level_files(sample_structure, show_all=False)
    assert result == ['LICENSE']

    result_with_hidden = list_top_level_files(sample_structure, show_all=True)
    assert result_with_hidden == ['.gitignore', 'LICENSE']
