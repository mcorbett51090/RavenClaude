# Check Sample-Ratio-Mismatch before trusting a result

Before reading any experiment metric, verify the observed traffic split matches the intended split. A Sample-Ratio-Mismatch means assignment, exposure logging, or randomization is broken, and the result is invalid no matter how significant it appears — SRM is the single most common cause of confidently-wrong experiment conclusions. Trust the plumbing before you trust the numbers.
