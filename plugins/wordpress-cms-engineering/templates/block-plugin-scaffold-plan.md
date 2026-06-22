# Block / Plugin Scaffold Plan — <feature>

> Output template for `wordpress-developer`. Plan a custom block or plugin before scaffolding. Fill every section; delete the guidance in italics.

## What it does
- **Feature:** _what the block/plugin provides_
- **Lives in:** _plugin name / mu-plugin / (theme only if presentation)_

## Block (if applicable)
- **Type:** _static (edit/save) / dynamic (render_callback)_
- **`block.json`:** _name, attributes, `supports`_
- **Attributes:** _name → type → source_
- **Assets:** _editor script / front-end script / style — each with a versioned handle_

## Data & queries
- **Reads/writes:** _CPT / meta / options / external API_
- **Query approach:** _WP_Query (bounded) / $wpdb->prepare when unavoidable_

## Hooks
- **Actions/filters used:** _hook → priority → why_

## Security
- **Sanitize-in:** _which inputs, which sanitize_* functions_
- **Escape-out:** _which outputs, which esc_* / wp_kses_
- **Nonce + capability:** _on every mutation_
- **Prepared SQL:** _if $wpdb is used_

## Seams handed off
- _Build approach → wordpress-architect · caching/security ops → wordpress-ops-engineer · decoupled consumer → frontend-engineering_

---
_Plus the ravenclaude-core Structured Output block._
