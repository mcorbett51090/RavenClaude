# 01: The M6 Mac mini, 16 GB / 256 GB

Checked 2026-11-16. This is the base configuration Apple sells, not the 24 GB / 512 GB configs and not the M5 Pro mini.

## What Apple publishes

Announced 2026-08-25, pre-order that day, in stores and shipping 2026-09-22 ([newsroom](https://www.apple.com/newsroom/2026/08/apple-unveils-a-more-powerful-mac-mini-featuring-the-all-new-m6-and-m5-pro/)). The tech specs are on [Apple's Mac mini specs](https://www.apple.com/mac-mini/specs/) and [support HT 128108](https://support.apple.com/en-us/128108).

| | This SKU | Where it says so |
|---|---|---|
| Chip | M6. 12-core CPU: 2 super, 4 performance, 6 efficiency. 12-core GPU with Neural Accelerators. Dual 16-core Neural Engine | specs page, model with 16 GB / 256 GB |
| Memory | 16 GB unified, **153 GB/s**. 24 GB and 32 GB move to 170 GB/s. Soldered; the configure-to-order list is purchase-time only | same pages. The support page lists both bandwidths on the chip, then ties 170 GB/s to the 24/32 GB options |
| Storage | 256 GB SSD, configurable at purchase to 512 GB, 1 TB, or 2 TB. Apple's footnote: 1 GB = 1 billion bytes, so formatted capacity is less. 256 × 10^9 / 2^30 ≈ **238 GiB** | specs footnote |
| Ports | Rear: 3× Thunderbolt 4 (40 Gb/s), HDMI, 2.5 Gb Ethernet (10 Gb is a purchase option). Front: 2× USB-C at USB 3 (10 Gb/s), headphone jack | specs page |
| Wireless | N1 chip, Wi-Fi 7, Bluetooth 6, Thread | specs page |
| OS | macOS 27. The newsroom says the mini ships with "the power of macOS 27". The Mac User Guide fetched the same day is titled for macOS 27 | newsroom; [user guide](https://support.apple.com/guide/mac-help/set-sleep-and-wake-settings-mchlp2401/mac) |
| Chassis | 5.0 × 5.0 × 2.0 in, 1.5 lb (M6) | specs page |
| Supply rating | 100–240 V, **maximum continuous power 155 W** | specs page. This is the supply, not the draw |
| Operating range | 10–35 °C, 5–90% non-condensing humidity | specs page |
| Idle acoustics | "Sound pressure level (operator position): 5 dBA at idle", and "acoustics may vary by configuration" | specs page |

The ECMA-109 table on that same support page (about 4 dB at idle and during a wireless-web test) has a footnote: the configuration tested was an **M5 Pro, 18-core CPU, 20-core GPU, 48 GB, 8 TB**. That table is not a measurement of this SKU.

## Power, for this exact SKU

[Apple's power and thermal table](https://support.apple.com/en-us/103253), published 2026-09-21, has a row "Mac mini (M6), Apple M6 chip, 16 GB unified memory, 256 GB SSD":

| | Idle | CPU max |
|---|---|---|
| From the wall | 4 W | 70 W |
| Heat | 14 BTU/h | 239 BTU/h |

Apple's notes: measured at the wall, including the supply. Idle is Finder open with the default power settings. CPU max is a compute test that loads the processor. The M4 mini's matching row on the same page is 4 W idle and 65 W max, so the idle figure did not move and the max rose by 5 W.

Other reviews measured other things, and they are not substitutes for that row:

- Les Numériques (2026): about 4.5 W at the desktop, 0.6 W asleep, under 0.1 W off, 48 W in a multi-core Cinebench run, 65 W with a CPU encode and a GPU render together, chassis 36.5 °C, fan about 37 dB in that combined test. The article does not say the unit was the 16 GB / 256 GB SKU.
- Notebookcheck's 24 GB / 512 GB sample, as cited by secondary write-ups: about 2.1–2.4 W idle, about 14.5 W single-core, about 55 W sustained and 74.3 W peak, 24.8 dB(A) idle and 41.7 dB(A) at full stress measured from 15 cm. Different memory, different SSD.

Ars Technica (2026-09) reports that `powermetrics` prints CPU power as 0 on the M6, so there is no usable per-core wattage from that tool until Apple's output changes.

Always-on electricity at the published idle is 4 W × 24 × 365 = **35 kWh/year**, before CI load. An extra 30 W for 8 hours a day would be about 88 kWh/year. That 30 W is a hypothesis, not a measurement of vitest on this machine. The box's and the Yoga's wall power were not measured here, so there is no watt-for-watt comparison yet. The structural point is that this mini is built to sit at a few watts, and the Yoga is a laptop that should not be the always-on machine.

## Storage implementation

Apple does not publish MB/s for the 256 GB SKU. The "up to 2× faster storage" line in the newsroom compares high-capacity configs (the footnotes and the secondary coverage put that comparison on 2 TB machines), so it does not describe the base SSD.

MacRumors (2026-09-22), citing a teardown and an AAPL Ch. Blackmagic Disk Speed Test with a 1 GB file:

| Config | Read | Write |
|---|---|---|
| M6, 256 GB | 3,216.8 MB/s | 3,000.2 MB/s |
| M6, 512 GB | 6,371.5 MB/s | 6,577.4 MB/s |
| M4, 256 GB | 2,792.5 MB/s | 2,014.5 MB/s |

The same report says the 256 GB M6 uses one NAND package, soldered, where the M4 mini's storage module could be swapped. IT Home (2026-09-24) reprints the same AAPL Ch. numbers. Treat them as one lab's sequential test. Random IO, and write latency once the machine is swapping, were not measured. No source published a terabytes-written endurance figure. The practical consequence is in [04](04-sizing-and-storage.md): the disk is large enough for two CI runners if Xcode and Docker stay off, and it is the wrong device for a machine that swaps all day.

## What the core mix means for CI

Six of the twelve cores are efficiency cores. The cores that finish a vitest worker are the two super cores and the four performance cores. A VM limited to 3 vCPU leaves the efficiency cores for macOS, the VM's own kernel, and the runner listeners. Giving the guest all 12 cores does not give it 12 fast cores, and it does let vitest start 12 workers.

Memory bandwidth at 16 GB is 153 GB/s, not the 170 GB/s of the 24/32 GB configs. Node and vitest are not bandwidth-bound at this width. The binding limits are the 16 GB capacity and the 238 GiB disk.
