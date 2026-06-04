# Compose components; don't configure mega-components

Build small components with clear, narrow props and compose them, lifting shared logic into custom hooks. A single component accreting boolean flags and conditional branches becomes untestable and fragile, and prop-drilling through many layers signals a missing composition or context boundary. Composition keeps each piece simple, testable, and replaceable.
