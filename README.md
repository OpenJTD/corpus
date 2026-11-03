# OpenJTD corpus

Public validation inputs, Markdown indexes, and manifests for external
documents. Include files only when redistribution is permitted and recorded.
External documents retain their original terms; inclusion does not relicense
them under Apache-2.0.

The initial [manifest](manifest.json) contains two self-generated synthetic
DocumentText stream fragments with expected low-level text observations. These two
are not complete JTD files, not native-authored documents, and not evidence of
independent reproduction with Tika JTD+. No local real-world sample is included.
Our authored fixtures, expected results, and documentation use Apache-2.0.

See the draft [manifest format](MANIFEST.md), [reproduction procedure](REPRODUCE.md),
and [shared research policy](https://github.com/OpenJTD/spec/blob/main/RESEARCH-POLICY.md).
Run `python3 tools/verify.py` to verify hashes, sizes, and byte-span expectations.
That check verifies corpus integrity, not an engine's parser behavior.

<!-- native-documents: begin -->
The manifest also contains three native JTD documents saved by Ichitaro 2026
(`samples/native/`), each with Ichitaro's own PDF of it: a controlled set in
which the experiment changes one variable (no ruby, or one ruby annotation
with a reading of 5 or 7 characters). They were generated from a Sample
Catalog (the three samples are published as `samples/native/rb15.catalog.json`)
by the contributor's macro-driven sample generator,
[openjtd-specimens](https://github.com/SH1R4S4G1/openjtd-specimens), with self-authored body text. The documents, the Catalog, the expected
observations and the PDFs are published under Apache-2.0, except the font
subset embedded in the PDFs, which stays under its provider's terms. Their
expected observations are rjtd text-map spans of `/DocumentText`; see
[REPRODUCE.md](REPRODUCE.md).
<!-- native-documents: end -->
