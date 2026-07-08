# Every eval needs a frozen golden set with provenance

**Rule.** Version the eval set, record where each example came from and how it was labeled, and never
let a model's output leak back in as an input. A set that quietly changes between runs makes every
comparison a lie.

**Why.** If the denominator moves, a score delta could be the change *or* the set — you can't tell.
Provenance lets you defend a label; a no-leakage rule stops the eval from grading the model on its own
answers.

**Anti-pattern it kills.** "The score jumped 8 points" — because three easy examples were quietly added,
not because the model improved.

**In practice.** Golden set under version control with a schema `{id, input, expected/label, source,
labeled_by, version}`; changes are deliberate, recorded promotions.
