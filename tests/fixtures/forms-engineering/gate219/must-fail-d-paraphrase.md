# Fixture — the paraphrase that evades B and C

Never let the client's declared content type decide what a file is — read the leading bytes of the
upload itself and match them against your allow-list. Reject the request at the boundary if it
exceeds your size ceiling, and store it under an identifier you generated, never under the name the
browser sent. The challenge token stops being accepted after a short window and may only be redeemed
once.

This paragraph carries none of the guarded literals and no vendor token, so sub-checks B and C read
it as clean. Sub-check D catches it, because the file discusses uploads and points nowhere.
