# Show, don't tell — with the hard examples

When a model can't infer format or behavior from an instruction, *show* it: one
well-chosen example teaches what a paragraph of description can't. But the examples
must earn their tokens.

**Do:** pick few-shot examples that cover the **hard and edge cases**, format them
identically to the desired output, order them deliberately, and stop at the
diminishing-returns point.

**Don't:** pad the prompt with easy, obvious examples — they teach nothing, cost
tokens, and can overfit the model to a rigid format.

**Flag:** a growing example list added "just in case" with no evidence each one
moves the eval. Every example should pay for its tokens on the regression set.
