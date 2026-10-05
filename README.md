# OpenJTD corpus

Public validation inputs, Markdown indexes, and manifests for external
documents. Include files only when redistribution is permitted and recorded.
External documents retain their original terms; inclusion does not relicense
them under Apache-2.0.

The initial [manifest](manifest.json) contains two self-generated synthetic
DocumentText stream fragments with expected low-level text observations. They
are not complete JTD files, not native-authored documents, and not evidence of
independent reproduction with Tika JTD+. No local real-world sample is included.
Our authored fixtures, expected results, and documentation use Apache-2.0.

See the draft [manifest format](MANIFEST.md), [reproduction procedure](REPRODUCE.md),
and [shared research policy](https://github.com/OpenJTD/spec/blob/main/RESEARCH-POLICY.md).
Run `python3 tools/verify.py` to verify hashes, sizes, and byte-span expectations.
That check verifies corpus integrity, not an engine's parser behavior.
