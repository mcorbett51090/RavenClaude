# Never assume English's grammar

English has two plural forms; CLDR defines up to six plural categories (zero/one/two/few/many/other) and Arabic uses all of them. Gender, grammatical case, and word order vary by language. Use ICU MessageFormat `plural`/`select` so the *translator* controls the grammar per the CLDR rules — never a developer's `if (n === 1)`. The moment application code decides the plural form or assumes word order, it is already wrong in some language you don't speak.
