# Never concatenate translatable fragments

"You have " + count + " items" is untranslatable: word order, agreement, and placement of the number differ per language, and a translator handed the fragments can't reorder them. Always emit one message with named interpolation placeholders (`"You have {count, plural, ...}"`) so the translator controls the whole sentence. Sentence-building from translated pieces produces grammatically broken output in most non-English locales and silently can't be fixed in translation.
