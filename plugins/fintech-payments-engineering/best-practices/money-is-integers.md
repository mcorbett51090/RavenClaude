# Represent money as integers in minor units

Store and compute money as integer minor units (cents) with an explicit currency code, never as floating-point. Float arithmetic introduces rounding errors that compound across transactions into reconciliation discrepancies and customer disputes — 0.1 + 0.2 is not 0.3 in floating point, and that error has no place anywhere near money. Integer minor units make every amount exact.
