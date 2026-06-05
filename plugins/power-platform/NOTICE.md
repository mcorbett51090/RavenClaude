# Third-party content notice — `power-platform` plugin

The `skills/` directory of this plugin contains skill definitions (SKILL.md files and `resources/` reference content) imported from:

**Source:** [`DanielKerridge/claude-code-power-platform-skills`](https://github.com/DanielKerridge/claude-code-power-platform-skills)
**Author:** Daniel Kerridge
**License:** MIT

The following skill folders are imported substantially as-is (with only minor structural adjustments to fit the RavenClaude plugin layout):

- `skills/code-review/`
- `skills/dataverse-plugins/`
- `skills/dataverse-web-api/`
- `skills/dataverse-web-resources/`
- `skills/pcf-controls/`
- `skills/plan-with-team/`
- `skills/power-apps-code-apps/`
- `skills/record-screen/`
- `skills/visual-qa/`

The `agents/` directory and `CLAUDE.md` constitution in this plugin are original work by Matt Corbett and are also released under MIT.

## MIT License (covers both the imported skills and original additions)

```
MIT License

Copyright (c) 2024–2026 Daniel Kerridge (skills imported from claude-code-power-platform-skills)
Copyright (c) 2026 Matt Corbett (RavenClaude additions and modifications)

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
```

## Excluded from import

The original `record-screen/scripts/node_modules` tree was excluded — consumers should run `npm install` from `skills/record-screen/scripts/` if they want to use the recorder. The `package-lock.json` was also excluded; it will be regenerated on first `npm install`.

---

## Bundled MCP servers

This plugin's `plugin.json` declares the following Model Context Protocol (MCP) server, which Claude Code starts automatically when the plugin is installed:

### `powerbi-editor` — community pbix-mcp

**Source:** [`d0nk3yhm/pbix-mcp`](https://github.com/d0nk3yhm/pbix-mcp)
**PyPI package:** [`pbix-mcp`](https://pypi.org/project/pbix-mcp/)
**License:** MIT
**What it does:** Read, write, and DAX-evaluate Power BI `.pbix` and `.pbit` files without requiring Power BI Desktop. Exposes ~101 tools covering multi-table creation with relationships, CSV/SQL/Excel/JSON sources, DirectQuery, DAX measure evaluation (~156 functions), RLS, custom visuals, and themes.

**Consumer prerequisite — must run once on the machine.** Pin the version (an unpinned install lets a breaking/compromised upstream release reach you silently):

```bash
pip install 'pbix-mcp==<tested-version>'   # [verify-at-use] — record the tested version
```

The plugin only declares the MCP wiring; the underlying Python binary (`pbix-mcp-server`) must exist on the consumer's PATH. If the binary isn't on PATH but Python is, override the declaration in your own `.claude/settings.json` with the console script by absolute path (the entry point that definitely exists), or with the `python -m` module form — **confirm the exact module path with `pip show -f pbix-mcp`** (it varies by package version; don't assume `pbix_mcp.cli` vs `pbix_mcp.server`):

```json
{
  "mcpServers": {
    "powerbi-editor": {
      "command": "/absolute/path/to/pbix-mcp-server"
    }
  }
}
```

Consumers who hit PATH issues can apply this override in their own `.claude/settings.json` without modifying this plugin. Keep this fallback identical to the one in [`CLAUDE.md`](CLAUDE.md) §9.

**MIT License attribution for pbix-mcp** — full text per the upstream LICENSE file at [`d0nk3yhm/pbix-mcp`](https://github.com/d0nk3yhm/pbix-mcp). Reproduced summary:

```
MIT License — Copyright (c) d0nk3yhm (pbix-mcp authors)

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction…
```

(See the upstream repo for the canonical, year-stamped license text.)
