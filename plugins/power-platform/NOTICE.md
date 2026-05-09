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
