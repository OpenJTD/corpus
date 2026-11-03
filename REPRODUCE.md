# Reproducing the initial trial

The manifest gives the literal-byte recipe for each synthetic input. Both are
logical stream fragments, not CFB containers or native JTD files. Byte spans are
zero-based and half-open. All their content is self-authored synthetic text.

Run `python3 tools/verify.py` from this repository to check the bytes against
their hashes, sizes, and expected text spans. This uses the Python standard
library and does not verify an engine.

For rjtd, feed each `.bin` file directly to
`rjtd_core::document_text::extract_document_text` and
`rjtd_core::document_text::map_document_text`. Compare plain text and each
entry's kind, `byte_start`, `byte_end`, and text to `expected/*.json`.
The full-document CLI expects a CFB document and is not the adapter for these
logical streams. The corresponding existing rjtd tests are:

```sh
cd rjtd
cargo test -p rjtd-core --locked extracts_utf16be_runs_after_text_marker
cargo test -p rjtd-core --locked excludes_style_tail_text_markers_after_the_declared_content
```

The first test uses different self-authored text but exercises the same marker
path; the second matches the style-tail bytes. Record engine/version and
executed/skipped cases for every comparison. Tika JTD+ results remain pending;
do not count a missing adapter as successful differential testing.

<!-- native-documents: begin -->
# Native documents: ruby on/off (rb15-fit-plain, rb15-half, rb15-over)

These three are complete JTD files saved by Ichitaro 2026, not stream
fragments. The experiment changes one variable: `rb15-fit-plain` has no
ruby; `rb15-half` and `rb15-over` add one ruby annotation (a reading of 5
and of 7 characters) to the same two characters of the same 81-character
body. The files differ in other streams too, as every save does (summary
streams, `/RelatedDocuments`, layout records). Each manifest item names
the generator, its version and commit, the Sample Catalog with its SHA-256,
and the catalog sample the generator executed.

Each native item also has a `reference_pdf`: Ichitaro's own PDF of the
document, saved as PDF from the saved JTD by the generator. `verify.py`
checks only its PDF header, path, size and hash, and no layout value of the
PDF is asserted in the expected files. The PDFs embed a glyph subset of
YuMincho-Regular (Version 1.92, a Microsoft supplied font, © 2019 JIYUKOBO
Ltd.) under its editable embedding permission (fsType 0x0008); that subset
stays under its provider's terms, Apache-2.0 does not extend to it, and no
complete or installable font is distributed. The PDFs' document information
holds `/Author` `user`, `/Producer` 一太郎 (the product name) and timestamps.

`tools/verify.py` reads `/DocumentText` from each file with a minimal
compound-file reader (standard library only), checks its hash against
`surface_sha256`, and checks every expected span against those stream bytes.
The kinds are rjtd's names: `text` (a run after a `0x001F` marker),
`control` (a control code; `raw` is its bytes), `inline` and
`skipped-inline` (a `0x001D ... 0x001E` segment that rjtd's plain text keeps
or drops; the span includes both delimiters and `text` is the bytes between
them). `selector`, `raw`, `surface_stream` and `surface_sha256` are added to
the observation format for these files.

To compare an engine, read `/DocumentText` from the JTD (for rjtd:
`rjtd dump-stream <file> /DocumentText`, `rjtd text-map <file>`,
`rjtd text-tokens <file>`) and compare kind, `byte_start`, `byte_end`,
selector and text with `expected/<id>.json`. The expected files were produced
by rjtd at the commit in `producer.version`; they record rjtd's behaviour,
not an independent agreement.

Regeneration: the generator is [openjtd-specimens](https://github.com/SH1R4S4G1/openjtd-specimens)
(Apache-2.0). `samples/native/rb15.catalog.json` holds these three samples
with the same `id`, `feature`, `expected` and `document` as the 18-sample
catalog whose id and SHA-256 the manifest items record (the other 15 samples
are not published; `title` and `purpose` are rewritten, so the file's SHA-256,
recorded as `catalog_file_sha256`, differs from the recorded catalog's).
It validates against releases 0.22.1 and 0.22.4 (tags `v0.22.1`, `v0.22.4`): from the generator's
checkout, `node bin/ichitaro.mjs validate <path to rb15.catalog.json>`
(Node.js 22 or later; checked on macOS; no Ichitaro needed). `verify.py`
checks that each manifest item's `recipe.document` is the published sample. Making the documents needs Windows and a licensed Ichitaro
2026: `node bin/ichitaro-request.mjs <path to rb15.catalog.json>
<new-dir> runs --pdf` validates the Catalog, compiles each sample to an
Ichitaro macro and runs it (it opens a new document, writes the body, applies
the ruby operation, saves, reads the settings back and saves the PDF); the
generator's README describes the steps and the per-sample records. These
three files were made by a pre-release build (0.15.1) that is not in the
public repository. This set is offered as `observed`, not `reproduced`: a
rerun by the contributor would not be an independent reproduction, and no
rerun with the public release has been made, so whether the public release writes the
same `/DocumentText` as the pre-release build is not shown here. A
regenerated JTD would not be byte-identical in any case: the summary streams
hold the save time and the generator's working path; compare `/DocumentText`
(and other streams) rather than the files. In one earlier run with the same body and ruby
operation but explicit document settings, `/DocumentText` was byte-identical
to these files'; that run is not included.

What these files show and do not show:

The annotation is Ichitaro's ruby (UI term: ふりがな), set by the generator
with its defaults (no size, alignment, position or distance given).

- Observed (two documents, readings of 5 and 7 characters): the two body
  characters at bytes 106..110 of the control's `/DocumentText` are wrapped.
  Before them the annotated files insert
  `001C 0000 000C 0000 0005 0000 0205 0200 000C 0000 0000 001F 001C 0001 0007 0000 0000 0003 001D`;
  after them
  `001E 0005 0000 0001 001F 001C 0001 0007 0000 0001 0082 001D <the requested reading> 001E 0005 0000 0001 001F`.
  The two segments match the selector-3 and `0x0082` patterns of the
  [current RFC 0003, "Inline Segment Observation"](https://github.com/OpenJTD/spec/blob/050a24a8d96f18c8cff17928c28704ea8fcb3284/rfc/0003-document-text.md#inline-segment-observation)
  and of "Inline regions" in the RFC 0002 proposed in
  [OpenJTD/spec#2](https://github.com/OpenJTD/spec/pull/2) (at
  `b999db7c86b2b4ec2fcbf083f0699635bcfafe05`). `verify.py` checks the
  `0x001C` codes and the two inline spans, not the other bytes quoted here.
  The meaning of the first record, of the words after each segment and of
  the selector values is not decoded by these files.
- Observed (same two documents), header words in the terms of the proposed
  RFC 0002: header word 9 (bytes 18..20, counting 16-bit words from 0; the
  word before `TextV.01`) is `0001` in the control and `0002` in both
  annotated files; the BE-u32 content length at byte 28 is 81 in the
  control and 122 and 124 in the annotated files, which is 81 plus the
  number of code units inserted (41 and 43). Within the declared content,
  each annotated body is the control's body with exactly the two insertions
  above. No meaning of header word 9 is claimed. Other bytes of
  `/DocumentText` (for example at byte 198 of the control, after the body)
  and other streams change too.
- Not shown: other ruby positions or placements (other selectors), ruby
  formatting, or any layout value of the PDFs (included only as references).
<!-- native-documents: end -->
