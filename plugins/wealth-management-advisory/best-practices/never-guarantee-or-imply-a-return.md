# Never guarantee or imply a return

**Status:** Absolute rule
**Domain:** Advisory compliance, RIA practice
**Applies to:** `wealth-management-advisory`

---

## Why this exists

Guaranteeing or implying an investment return is a misrepresentation under Section 206 of the
Investment Advisers Act and a violation of FINRA Rule 2210 for registered representatives.
Beyond the regulatory exposure, it sets an expectation the advisor cannot meet — and when
markets underperform that implication, it destroys the client relationship and exposes the firm
to complaints, arbitration, and regulatory sanction.

Return guarantees are not always explicit. Soft-form violations are common: "this strategy has
historically returned 8%," "this is about as safe as it gets," "you really can't lose here," or
"this is a low-risk investment" applied to a product with significant risk. All of these can
create a guarantee impression in a retail client's mind and will be read that way in a complaint.

The hook in this plugin flags the most mechanically detectable forms. The advisor must also
exercise judgment on the softer implications.

## How to apply

**Do:**

- Use range language: "historically, a diversified portfolio has produced returns of [X–Y]% over
  long periods, though any given period may be significantly different."
- State assumptions when projecting: "this projection assumes a [X]% average annual return, which
  is not guaranteed and may not be achieved."
- Include the mandatory past-performance disclosure whenever any historical return is cited:
  "Past performance does not guarantee future results."
- Frame Monte Carlo output as probability framing, not certainty: "in [X]% of 10,000 scenarios,
  the portfolio sustained withdrawals to age [Y]; in [100-X]% it did not."

**Don't:**

- Guarantee a return, even implicitly: "you won't lose money," "this is guaranteed income,"
  "this pays [X]% per year."
- Imply a return through selective historical data without the full disclosure: "this strategy
  returned 15% last year" without context or disclaimer.
- Use "safe" or "risk-free" to describe an investment that carries any market, credit, liquidity,
  or inflation risk.
- Omit the benchmark or the time period when citing a return figure.

## Edge cases / when the rule does NOT apply

- FDIC-insured bank deposits (up to coverage limits) and US Treasury securities held to maturity
  are genuinely principal-protected instruments — but even here, inflation risk and opportunity
  cost are real and should be disclosed.
- Fixed annuity guaranteed rates are contractually guaranteed by the insurance company — but the
  guarantee is only as strong as the insurer's claims-paying ability, and this should be disclosed.
- When describing these carve-outs, be precise: "the FDIC insures deposits up to $250,000 per
  depositor per institution [verify-at-use]" — do not generalize beyond the specific instrument.

## See also

- [`./suitability-and-reg-bi-clear-before-any-recommendation.md`](./suitability-and-reg-bi-clear-before-any-recommendation.md)
- [`../hooks/check-wealth-management-advisory-anti-patterns.sh`](../hooks/check-wealth-management-advisory-anti-patterns.sh) — automated flag for guarantee language

## Provenance

Codifies prohibitions under Investment Advisers Act §206 (anti-fraud), FINRA Rule 2210 (content
standards for communications with the public), and SEC guidance on performance advertising under
the 2022 Marketing Rule (Rule 206(4)-1 under the Advisers Act). Consult the firm's compliance
officer or legal counsel for firm-specific implementation. Not legal advice.

---

_Last reviewed: 2026-06-08 by `claude`._
