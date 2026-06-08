# CLDR / Intl is the source of truth for locale data

Plural rules, date/number/currency/list/unit formatting, and collation order are defined by CLDR and exposed through `Intl` (`PluralRules`, `NumberFormat`, `DateTimeFormat`, `Collator`, `ListFormat`) or your i18n library. Read them from there — never hand-roll a date format, a decimal separator, or a sort order. Hardcoded formatting (`MM/DD/YYYY`, `.` as the decimal separator, ASCII sort) is correct in exactly one locale and wrong everywhere else; CLDR already knows the answer for all of them.
