# Vendored Python dependencies

These packages ship **inside the plugin** so hooks and scripts need nothing beyond a stock
`python3`. They are a **fallback only**: each consuming script _appends_ this directory to
`sys.path`, so an installed copy of the same package always wins.

| Package          | Version | Source                                                          | sha256 of the sdist                                                | License                              |
| ---------------- | ------- | --------------------------------------------------------------- | ------------------------------------------------------------------ | ------------------------------------ |
| `yaml/` (PyYAML) | 6.0.3   | `lib/yaml/` from `pyyaml-6.0.3.tar.gz` on PyPI, copied verbatim | `d76623373421df22fb4cf8817020cbb7ef15c725b9d5e45f17e189bfc384190f` | MIT — [`yaml/LICENSE`](yaml/LICENSE) |

## Why PyYAML is vendored

A stock macOS `python3` (Xcode Command Line Tools, or Homebrew) has **no PyYAML**. Before this
directory existed, the command-review tribunal (`hooks/thing-orchestrator.sh` →
`scripts/thing-decision.py`) could not parse `.ravenclaude/comfort-posture.yaml` or the concern
catalog. It failed closed and **denied every Bash command, including `ls`**, with a misleading
"would tamper with the Thing" reason. That is correct fail-closed behaviour, but the missing module
was the only cause.

Installing PyYAML automatically was rejected because:

- Homebrew Python is PEP 668 "externally managed", so `pip install` is refused.
- A guardrail plugin that runs `pip` from a hook is making network and supply-chain changes the
  user never approved.

A hand-written YAML-subset parser was also rejected. The concern catalog is a 1,200-line block of
security regexes, and a parser that reads a quoted regex differently from PyYAML would silently
weaken a security gate. The vendored copy is byte-identical upstream code, so it parses exactly
the same way.

Only the pure-Python modules are included. `cyaml.py` needs the compiled `_yaml` extension, and
`yaml/__init__.py` already falls back cleanly when that extension is missing.

## Updating

```shell
curl -sSLO https://files.pythonhosted.org/packages/source/p/pyyaml/pyyaml-<ver>.tar.gz
sha256sum pyyaml-<ver>.tar.gz          # compare against the digest PyPI publishes
tar -xzf pyyaml-<ver>.tar.gz
rm -rf yaml && cp -r pyyaml-<ver>/lib/yaml yaml && cp pyyaml-<ver>/LICENSE yaml/LICENSE
```

Then update the table above. Do not edit the vendored files by hand. Ruff and prettier skip this
directory.
