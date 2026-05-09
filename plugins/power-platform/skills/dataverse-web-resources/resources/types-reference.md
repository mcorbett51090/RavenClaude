# Web Resource Types Reference

Dataverse supports 12 web resource types, identified by numeric Type IDs.

## Type Catalog

| Type ID | Extension | Name | Description |
|---|---|---|---|
| 1 | `.html` | HTML | Web pages, dashboards, custom UI |
| 2 | `.css` | CSS | Stylesheets for HTML web resources |
| 3 | `.js` | JScript | JavaScript for form events, ribbons, HTML pages |
| 4 | `.xml` | XML | Data files, configuration, XSLT source |
| 5 | `.png` | PNG | Images (icons, logos, status indicators) |
| 6 | `.jpg` | JPG | Images (photos, backgrounds) |
| 7 | `.gif` | GIF | Images (animated indicators) |
| 8 | `.xap` | Silverlight | **DEPRECATED** — Do not use |
| 9 | `.xsl` | XSL | XSLT stylesheets for XML transformation |
| 10 | `.ico` | ICO | Favicon and small icons |
| 11 | `.svg` | SVG | Scalable Vector Graphics (app icons, entity icons) |
| 12 | `.resx` | RESX | Resource strings for localization |

## Common Use Cases by Type

### JavaScript (Type 3) — Most Common
- Form event handlers (OnLoad, OnSave, OnChange)
- Ribbon/command bar button handlers
- Business rule enforcement beyond OOB capabilities
- Field validation and auto-population
- Form section show/hide logic
- Web API calls from forms

### HTML (Type 1)
- Dashboard pages with charts and KPIs
- Custom configuration pages
- Embedded utilities (calculators, viewers)
- Sitemap SubArea pages (`$webresource:` directive)
- Help pages and documentation

### SVG (Type 11)
- Entity icons (32x32 for forms, 16x16 for views)
- App module icons
- Status indicator icons
- Custom button icons for ribbons

### CSS (Type 2)
- Styling for HTML web resources
- Theme customization for embedded pages
- Print stylesheets

### PNG/JPG/GIF (Types 5-7)
- Entity images and icons
- Background images for HTML resources
- Status indicator images for view columns (via `imageproviderwebresource`)

### RESX (Type 12)
- Localized strings for multi-language support
- Label text externalization
- Error message localization

## Naming Conventions

Web resources use a virtual folder structure with the publisher prefix:

```
{prefix}_/                     ← Root virtual folder
  ├── js/
  │   ├── formscript.js        ← Form event handlers
  │   ├── ribboncommands.js    ← Ribbon button handlers
  │   └── utils.js             ← Shared utilities
  ├── html/
  │   ├── dashboard.html       ← Dashboard pages
  │   └── config.html          ← Configuration pages
  ├── css/
  │   └── styles.css           ← Stylesheets
  ├── images/
  │   ├── logo.png             ← Images
  │   └── entity_icon.svg      ← Entity icons
  └── data/
      └── config.xml           ← Configuration data
```

**Full name format:** `cnt_/js/formscript.js`
- The publisher prefix is part of the name
- Forward slashes create virtual folders (not actual filesystem folders)
- Use lowercase, descriptive names
- Group by type (js/, html/, css/, images/)
