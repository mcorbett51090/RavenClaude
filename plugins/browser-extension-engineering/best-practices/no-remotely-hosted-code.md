# No remotely-hosted code

**Rule.** All executable JS ships inside the package. Fetch data/config if needed,
but never fetch and run code — no `eval` of a remote payload, no injected remote
`<script>`, no remote module import.

**Why.** MV3 forbids remotely-hosted code, and it is a hard store-rejection cause
(and a serious security risk).

**Smell.** A loosened CSP to allow a remote script; `import()` of a remote URL;
`eval` of a fetched string.

**Cite:** plugin §4.6; `knowledge/manifest-v3-architecture.md`.
