import os
import sys
import pytest
from modules.persistence import persist_multicopy, remove_persist, get_system_paths

def test_persist_multicopy_creates_files():
    paths = persist_multicopy()
    created = [p for p in paths if os.path.exists(p)]
    assert len(created) > 0

def test_remove_persist_deletes_files():
    persist_multicopy()
    remove_persist()
    for p in get_system_paths():
        assert not os.path.exists(p)
