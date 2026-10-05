"""Verify the initial synthetic corpus's integrity; does not run an engine."""
import hashlib
import json
from pathlib import Path

root = Path(__file__).resolve().parents[1]
manifest = json.loads((root / "manifest.json").read_text())
assert manifest["schema_version"] == 1
ids = set()
for item in manifest["items"]:
    assert item["id"] not in ids
    ids.add(item["id"])
    assert item["distribution"] == "public"
    assert item["sharing_basis"] and item["provenance"]
    assert item["kind"] == "synthetic-stream" and not item["native_authored"]
    data = (root / item["path"]).read_bytes()
    assert len(data) == item["size_bytes"]
    digest = hashlib.sha256(data).hexdigest()
    assert digest == item["sha256"]
    expected = json.loads((root / item["expected_observations"]).read_text())
    assert expected["schema_version"] == 1
    assert expected["input_id"] == item["id"]
    assert expected["input_sha256"] == digest
    for observation in expected["observations"]:
        start, end = observation["byte_start"], observation["byte_end"]
        assert 0 <= start < end <= len(data)
        assert start % 2 == end % 2 == 0
        assert data[start:end].decode("utf-16-be") == observation["text"]
print(f"Verified {len(ids)} synthetic stream fixtures; engine validation is separate.")
