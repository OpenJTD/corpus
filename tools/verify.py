"""Verify the corpus's integrity; does not run an engine.

Synthetic items are logical stream fragments: byte spans index the file itself.
Native items are complete CFB (OLE2) JTD files: byte spans index the stream
named by the expected file's `surface_stream` (for example `/DocumentText`),
read with the minimal compound-file reader below (standard library only).
A `reference_pdf` of an item is checked for its PDF header, size and hash only.
"""
import hashlib
import json
import struct
from pathlib import Path

FREE, END_OF_CHAIN = 0xFFFFFFFF, 0xFFFFFFFE


def cfb_stream(data, path):
    """The bytes of the stream at `path` ("/Name" or "/Storage/Name") in a CFB file."""
    assert data[:8] == bytes.fromhex("d0cf11e0a1b11ae1"), "not a compound file"
    sector_shift, mini_shift = struct.unpack_from("<HH", data, 30)
    sector, mini = 1 << sector_shift, 1 << mini_shift
    n_fat, first_dir, _, cutoff, first_minifat, n_minifat, first_difat, n_difat = struct.unpack_from(
        "<IIIIIIII", data, 44)

    def at(index):
        return (index + 1) * sector

    difat = list(struct.unpack_from("<109I", data, 76))
    next_difat = first_difat
    for _ in range(n_difat):
        block = struct.unpack_from(f"<{sector // 4}I", data, at(next_difat))
        difat += block[:-1]
        next_difat = block[-1]
    fat = []
    for index in difat[:n_fat]:
        fat += struct.unpack_from(f"<{sector // 4}I", data, at(index))

    def chain(start, table):
        out, seen = [], set()
        while start not in (FREE, END_OF_CHAIN):
            assert start not in seen and start < len(table), "broken sector chain"
            seen.add(start)
            out.append(start)
            start = table[start]
        return out

    def read(start):
        return b"".join(data[at(i):at(i) + sector] for i in chain(start, fat))

    directory = read(first_dir)
    entries = []
    for offset in range(0, len(directory), 128):
        raw = directory[offset:offset + 128]
        name_len = struct.unpack_from("<H", raw, 64)[0]
        name = raw[:max(name_len - 2, 0)].decode("utf-16-le")
        kind = raw[66]
        left, right, child, start = struct.unpack_from("<IIII", raw, 68)[:3] + struct.unpack_from("<I", raw, 116)
        size = struct.unpack_from("<Q", raw, 120)[0]
        entries.append((name, kind, left, right, child, start, size))
    root = entries[0]
    minifat = []
    for index in chain(first_minifat, fat) if n_minifat else []:
        minifat += struct.unpack_from(f"<{sector // 4}I", data, at(index))
    ministream = read(root[5]) if root[5] != END_OF_CHAIN else b""

    def children(entry):
        found, stack = {}, [entry[4]]
        while stack:
            index = stack.pop()
            if index == FREE or index >= len(entries):
                continue
            e = entries[index]
            found[e[0].upper()] = e
            stack += [e[2], e[3]]
        return found

    entry = root
    for part in [p for p in path.split("/") if p]:
        entry = children(entry).get(part.upper())
        assert entry is not None, f"no stream {path}"
    assert entry[1] == 2, f"{path} is not a stream"
    if entry[6] < cutoff:
        raw = b"".join(ministream[i * mini:(i + 1) * mini] for i in chain(entry[5], minifat))
    else:
        raw = read(entry[5])
    return raw[:entry[6]]


root = Path(__file__).resolve().parents[1]
manifest = json.loads((root / "manifest.json").read_text(encoding="utf-8"))
assert manifest["schema_version"] == 1
ids = set()
counts = {"synthetic": 0, "native": 0, "pdf": 0}
for item in manifest["items"]:
    assert item["id"] not in ids
    ids.add(item["id"])
    assert item["distribution"] == "public"
    assert item["sharing_basis"] and item["provenance"]
    data = (root / item["path"]).read_bytes()
    assert len(data) == item["size_bytes"]
    digest = hashlib.sha256(data).hexdigest()
    assert digest == item["sha256"]
    expected = json.loads((root / item["expected_observations"]).read_text(encoding="utf-8"))
    assert expected["schema_version"] == 1
    assert expected["input_id"] == item["id"]
    assert expected["input_sha256"] == digest
    if "reference_pdf" in item:
        pdf = item["reference_pdf"]
        assert pdf["path"] == f"samples/native/{item['id']}.pdf"
        pdf_data = (root / pdf["path"]).read_bytes()
        assert pdf_data.startswith(b"%PDF-")
        assert len(pdf_data) == pdf["size_bytes"]
        assert hashlib.sha256(pdf_data).hexdigest() == pdf["sha256"]
        counts["pdf"] += 1
    if item["kind"] == "synthetic-stream":
        assert not item["native_authored"]
        surface = data
        counts["synthetic"] += 1
    else:
        assert item["kind"] == "native-document" and item["native_authored"]
        surface = cfb_stream(data, expected["surface_stream"])
        assert hashlib.sha256(surface).hexdigest() == expected["surface_sha256"]
        recipe = item["provenance"]["recipe"]
        if "catalog_file" in recipe:
            # the published Sample Catalog holds the same sample the generator executed
            catalog_bytes = (root / recipe["catalog_file"]).read_bytes()
            assert hashlib.sha256(catalog_bytes).hexdigest() == recipe["catalog_file_sha256"]
            catalog = json.loads(catalog_bytes.decode("utf-8"))
            assert catalog["id"] == recipe["catalog_id"]
            (sample,) = [s for s in catalog["samples"] if s["id"] == recipe["sample_id"]]
            assert sample["document"] == recipe["document"]
        counts["native"] += 1
    for observation in expected["observations"]:
        start, end = observation["byte_start"], observation["byte_end"]
        assert 0 <= start < end <= len(surface)
        assert start % 2 == end % 2 == 0
        assert "text" in observation or "raw" in observation
        if "raw" in observation:
            assert surface[start:end].hex() == observation["raw"]
        if observation["kind"] in ("inline", "skipped-inline"):
            # the span includes the 0x001D/0x001E delimiters; the text is between them
            assert surface[start:start + 2] == b"\x00\x1d" and surface[end - 2:end] == b"\x00\x1e"
            assert surface[start + 2:end - 2].decode("utf-16-be") == observation["text"]
        elif "text" in observation:
            assert surface[start:end].decode("utf-16-be") == observation["text"]
print(f"Verified {counts['synthetic']} synthetic stream fixtures, {counts['native']} native documents "
      f"and {counts['pdf']} reference PDFs; "
      "engine validation is separate.")
