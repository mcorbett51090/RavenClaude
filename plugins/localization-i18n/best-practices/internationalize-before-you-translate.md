# Internationalize before you translate

The expensive localization mistakes — hardcoded strings, concatenated sentences, 2-form plural logic, physical CSS that breaks in RTL — are baked into the code before a single word is translated. Design the i18n seam (the library, the keys, the message format, the RTL approach) up front. Retrofitting internationalization onto a hardcoded codebase is a rewrite, not a feature, and translation spent on a non-internationalized app produces strings the product can't render correctly.
