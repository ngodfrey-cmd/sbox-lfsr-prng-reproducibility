# S-Box-Controlled Multi-LFSR PRNG: Reproducibility Materials

This repository preserves a deterministic S-box-controlled multi-LFSR pseudorandom-bit-generator experiment and a verified 1,000,000-bit output artifact.

## Verified source/artifact pair

| Source | Generated artifact | SHA-256 |
|---|---|---|
| `src/sbox_lfsr_runs_fix.py` | `data/prng_bits_runs_final.txt` | `012c3b311dcff7669c113472f3c78f34fd96b65cddd0b492f7f7acb8bcc2910b` |

The artifact was reproduced in an isolated temporary directory and compared byte-for-byte with the preserved file.

## Requirements

- Python 3
- No third-party Python packages are required.

## Reproduce the bitstream

From the repository root:

```bash
mkdir -p reproduced
(
  cd reproduced
  python3 ../src/sbox_lfsr_runs_fix.py
)

sha256sum reproduced/prng_bits_runs_final.txt data/prng_bits_runs_final.txt

cmp -s reproduced/prng_bits_runs_final.txt data/prng_bits_runs_final.txt \
  && echo "MATCH: reproduced artifact is identical." \
  || echo "NO MATCH: investigate the execution environment."
```

Expected SHA-256 checksum:

```text
012c3b311dcff7669c113472f3c78f34fd96b65cddd0b492f7f7acb8bcc2910b
```

## Artifact format

`data/prng_bits_runs_final.txt` contains exactly 1,000,000 ASCII characters. Each character is `0` or `1`; the file has no newline terminator.

## Scope and limitations

This repository is a research and reproducibility artifact.

- The generator is deterministic and uses fixed initial states.
- It is not presented as a production cryptographic random-number generator.
- Do not use its output for production encryption keys, passwords, authentication secrets, session tokens, or other security-critical secrets.
- Statistical properties of a finite output sample do not establish suitability for a particular cryptographic deployment.

## Excluded historical materials

The original working directory contained additional source revisions, generated bitstreams, and a compiled `assess` executable. They are intentionally excluded from this minimal release because they are not all independently verified source/artifact pairs, and the executable's source and redistribution provenance were not established.

## Integrity

See `SHA256SUMS.txt` for SHA-256 checksums of the published repository artifacts.
