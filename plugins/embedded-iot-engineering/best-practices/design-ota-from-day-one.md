# Design OTA from day one — dual-bank with rollback

Every connected field device needs an over-the-air update path, designed in from the start, not bolted on for v2. A device you cannot update in the field is a security liability with a fixed expiry. The baseline is dual-bank / A-B flash partitioning plus a rollback-on-failed-boot path so one bad update can't brick the fleet — budget the second image bank in the flash layout up front. Keep the bootloader minimal and verified, since it is often the one piece you cannot OTA.
