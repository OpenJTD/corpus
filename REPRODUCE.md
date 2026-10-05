# Reproducing the initial trial

The manifest gives the literal-byte recipe for each input. Both are logical
stream fragments, not CFB containers or native JTD files. Byte spans are
zero-based and half-open. All content is self-authored synthetic text.

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
