# Plan is the review artifact; never blind-apply

Every change is reviewed as a `terraform plan` before `apply`. Auto-applying in CI without a human (or policy gate) reading the plan is how infrastructure gets deleted or recreated by surprise. The plan is the diff; review it like code.
