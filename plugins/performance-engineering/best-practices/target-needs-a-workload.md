# A performance target needs a workload attached

"Fast" is unfalsifiable, so it is unmeetable. Every performance NFR names the percentile, the threshold, *and* the load it holds at — "p99 ≤ 200 ms at 5,000 req/s with a 70/30 read/write mix", never "the API should be fast". A target with no load is a wish; you cannot pass or fail it, gate a release on it, or size capacity from it. Write the number with its workload or send the requirement back to product until you can.
