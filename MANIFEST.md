# Corpus manifest format

Status: draft for joint review

`manifest.json` has `schema_version: 1` and an `items` array. Each item records:

| Field | Meaning |
| --- | --- |
| `id`, `filename`, `sha256`, `size_bytes` | Stable identity and exact bytes; use null for bytes not acquired |
| `path`, `source_url` | Repository-relative path or an external acquisition source |
| `creator`, `rights_holder`, `license` | Authorship and applicable original terms |
| `provenance` | How, when, and by whom the input was acquired or generated |
| `sharing_basis` | Concrete grant or authorship basis permitting this audience to access it |
| `distribution` | `public`, `collaborators-only`, or `metadata-only` |
| `allowed_collaborators` | Named permitted audience for a private item |
| `derived_output_permission` | Whether and under which terms derived output may be shared |
| `kind`, `native_authored`, `features` | Native/synthetic/imported distinction and observed features |
| `expected_observations` | Optional relative path to permitted expected results |

Record permission evidence and its scope rather than treating a source URL as
a redistribution grant. For an external metadata-only entry, omit local bytes
and use only metadata the original terms allow publishing. Private storage is
not itself a sharing basis. Remove personal/confidential data only where
permitted and retain the distinction between an original and a derived input.
