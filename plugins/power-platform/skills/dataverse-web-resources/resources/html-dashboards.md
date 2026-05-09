# HTML Dashboard Web Resources

Build rich, interactive dashboard pages with charts, KPIs, and data visualizations
as HTML web resources embedded in model-driven apps.

## Architecture

```
Model-Driven App
  └── Sitemap SubArea ($webresource:cnt_/html/dashboard.html)
       └── HTML Web Resource (iframe)
            ├── Chart Library (Chart.js, D3.js)
            ├── CSS Stylesheet
            └── Data Access (parent.Xrm.WebApi)
```

## Accessing Dataverse Data

From within an HTML web resource loaded in a model-driven app, access the parent
window's Xrm object:

```javascript
// Get the Xrm context from the parent MDA frame
var Xrm = parent.Xrm;

// Fetch records
async function loadProjects() {
    try {
        var result = await Xrm.WebApi.retrieveMultipleRecords(
            "cnt_project",
            "?$select=cnt_projectname,cnt_budget,cnt_status" +
            "&$filter=statecode eq 0" +
            "&$orderby=cnt_budget desc" +
            "&$top=50"
        );
        return result.entities;
    } catch (error) {
        console.error("Failed to load projects:", error.message);
        return [];
    }
}

// Aggregate data
async function getKPIs() {
    var projects = await loadProjects();
    return {
        totalProjects: projects.length,
        totalBudget: projects.reduce((sum, p) => sum + (p.cnt_budget || 0), 0),
        avgBudget: projects.length > 0
            ? projects.reduce((sum, p) => sum + (p.cnt_budget || 0), 0) / projects.length
            : 0
    };
}
```

## Dashboard Page Template

```html
<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8" />
    <title>Project Dashboard</title>
    <script src="../../cnt_/lib/chart.min.js"></script>
    <link rel="stylesheet" href="../../cnt_/css/dashboard.css" />
    <style>
        body { font-family: 'Segoe UI', sans-serif; margin: 20px; background: #f5f5f5; }
        .kpi-row { display: flex; gap: 20px; margin-bottom: 20px; }
        .kpi-card {
            background: white; border-radius: 8px; padding: 20px;
            flex: 1; box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }
        .kpi-value { font-size: 2em; font-weight: bold; color: #0078d4; }
        .kpi-label { color: #666; margin-top: 4px; }
        .chart-container { background: white; border-radius: 8px; padding: 20px; }
    </style>
</head>
<body>
    <h1>Project Dashboard</h1>
    <div class="kpi-row">
        <div class="kpi-card">
            <div class="kpi-value" id="totalProjects">-</div>
            <div class="kpi-label">Total Projects</div>
        </div>
        <div class="kpi-card">
            <div class="kpi-value" id="totalBudget">-</div>
            <div class="kpi-label">Total Budget</div>
        </div>
        <div class="kpi-card">
            <div class="kpi-value" id="avgBudget">-</div>
            <div class="kpi-label">Avg Budget</div>
        </div>
    </div>
    <div class="chart-container">
        <canvas id="budgetChart" height="300"></canvas>
    </div>

    <script>
        var Xrm = parent.Xrm;

        async function init() {
            var projects = await loadData();
            renderKPIs(projects);
            renderChart(projects);
        }

        async function loadData() {
            try {
                var result = await Xrm.WebApi.retrieveMultipleRecords(
                    "cnt_project",
                    "?$select=cnt_projectname,cnt_budget,cnt_status&$filter=statecode eq 0&$top=20"
                );
                return result.entities;
            } catch (e) {
                console.error("Data load failed:", e);
                return [];
            }
        }

        function renderKPIs(projects) {
            var total = projects.reduce((s, p) => s + (p.cnt_budget || 0), 0);
            document.getElementById("totalProjects").textContent = projects.length;
            document.getElementById("totalBudget").textContent = "$" + total.toLocaleString();
            document.getElementById("avgBudget").textContent = "$" +
                (projects.length ? Math.round(total / projects.length).toLocaleString() : "0");
        }

        function renderChart(projects) {
            var ctx = document.getElementById("budgetChart").getContext("2d");
            new Chart(ctx, {
                type: "bar",
                data: {
                    labels: projects.map(p => p.cnt_projectname),
                    datasets: [{
                        label: "Budget",
                        data: projects.map(p => p.cnt_budget || 0),
                        backgroundColor: "#0078d4"
                    }]
                },
                options: {
                    responsive: true,
                    plugins: { legend: { display: false } }
                }
            });
        }

        init();
    </script>
</body>
</html>
```

## Sitemap Integration

Add the dashboard as a navigation item using the `$webresource:` directive:

```xml
<Area Id="Dashboard" Title="Dashboard" ShowGroups="true">
    <Group Id="Overview" Title="Overview">
        <SubArea Id="projectDashboard"
                 Url="$webresource:cnt_/html/dashboard.html"
                 Title="Project Dashboard" />
    </Group>
</Area>
```

## Referencing Other Web Resources

From within an HTML web resource, reference other web resources using relative paths:

```html
<!-- Two levels up from the HTML resource to the web resource root -->
<script src="../../cnt_/lib/chart.min.js"></script>
<link rel="stylesheet" href="../../cnt_/css/dashboard.css" />
<img src="../../cnt_/images/logo.png" />
```

The path structure: `../../{prefix}_/{folder}/{filename}`

## Responsive Design Patterns

```css
/* Adapt to the container size */
body { margin: 0; padding: 16px; box-sizing: border-box; }

.dashboard-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
    gap: 16px;
}

/* Handle narrow containers (e.g., embedded in a form section) */
@media (max-width: 600px) {
    .kpi-row { flex-direction: column; }
}
```

## Best Practices

1. **Load data asynchronously** — don't block page rendering while fetching
2. **Handle errors gracefully** — show "No data" states instead of blank pages
3. **Use `parent.Xrm`** — don't try to authenticate separately
4. **Minify JS/CSS** — web resources have a 5MB limit
5. **Cache-friendly** — Dataverse caches web resources; version filenames for updates
6. **Responsive layout** — the iframe size varies by screen and MDA layout
7. **No sensitive data in HTML** — web resource content is accessible to all app users
8. **Test in the actual MDA context** — `parent.Xrm` is only available when loaded inside MDA
