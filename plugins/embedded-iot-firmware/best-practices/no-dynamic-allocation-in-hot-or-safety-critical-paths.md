# No dynamic allocation in hot or safety-critical paths

**Status:** Absolute rule
**Domain:** Embedded firmware — memory management
**Applies to:** `embedded-iot-firmware`

---

## Why this exists

`malloc`, `new`, and `free` on a microcontroller introduce three problems that are unacceptable
in hot or safety-critical firmware paths:

1. **Non-deterministic latency.** A heap allocator may scan free lists of variable length; on a
   fragmented heap, allocation time is unbounded. This violates any real-time guarantee.
2. **Heap fragmentation.** Repeated allocation and deallocation of variable-size objects
   fragments the heap. A device that works on day 1 may fail with `NULL` from `malloc` after
   days of operation.
3. **Silent failure under pressure.** When the heap is exhausted, `malloc` returns `NULL`.
   Firmware that does not check — and much firmware doesn't — dereferences `NULL`, hard-faults,
   and resets. In a safety-adjacent system this is an uncontrolled failure.

"Hot path" means: any ISR, any periodic control loop executing at > 10 Hz, any path that runs
more than a few hundred times per second. "Safety-critical" means: any path whose failure mode
is a physical hazard, an undetectable data corruption, or an unrecoverable device state.

---

## How to apply

**Do:**

- Pre-allocate all objects as `static` arrays sized at link time.
- Use a fixed-size pool allocator for types that need runtime "allocation":

```c
/* Static pool — N objects pre-allocated; allocation is O(1) and bounded */
#define SENSOR_MSG_POOL 16
typedef struct { uint16_t raw; uint32_t timestamp; } sensor_msg_t;
static sensor_msg_t pool[SENSOR_MSG_POOL];
static uint8_t      pool_used[SENSOR_MSG_POOL];

sensor_msg_t *pool_alloc(void) {
    for (int i = 0; i < SENSOR_MSG_POOL; i++) {
        if (!pool_used[i]) { pool_used[i] = 1; return &pool[i]; }
    }
    return NULL;  /* pool exhausted — this is a design error, not a runtime surprise */
}

void pool_free(sensor_msg_t *p) {
    pool_used[p - pool] = 0;
}
```

- Use `_Static_assert(sizeof(pool) < SRAM_BUDGET_BYTES, "pool exceeds SRAM budget");` to
  make an oversized pool a compile-time error.
- Use FreeRTOS static allocation APIs (`xQueueCreateStatic`, `xTaskCreateStatic`) instead of
  the heap-allocating versions where determinism is required.

**Don't:**

```c
/* WRONG — malloc in a periodic control loop */
void control_loop_1kHz(void) {
    float *state = malloc(sizeof(float) * N_STATES);  /* non-deterministic, fragmentation */
    compute_control(state);
    free(state);
}

/* WRONG — new in a driver method called from ISR context */
void SPI1_IRQHandler(void) {
    Message *m = new Message(rxbuf);  /* C++ heap allocation in ISR — double violation */
    queue.push(m);
}
```

---

## Edge cases / when the rule does NOT apply

- **Startup / initialization paths** (called once, before the scheduler starts or before any
  real-time constraint is active): dynamic allocation is acceptable if the total allocation is
  bounded and verified, and if there is no `free` at runtime.
- **Non-realtime background tasks** (e.g. an OTA download task running at the lowest priority
  with no deadline): dynamic allocation is acceptable if the task is not in any safety-critical
  subsystem and heap exhaustion is handled gracefully.
- **C++ constructors at static scope** (global/static objects with constructors): evaluated at
  startup — acceptable if bounded.

The rule is absolute for ISRs and any periodic path with a real-time or safety requirement.

---

## See also

- [`./never-block-in-an-isr.md`](./never-block-in-an-isr.md)
- `firmware-engineer` agent — static pool allocator patterns, ring buffers.
- `rtos-engineer` agent — FreeRTOS static allocation APIs.
- MISRA-C:2012 Rule 21.3 (the use of `malloc` and `free` is not allowed).
- CERT-C MEM35-C — allocate sufficient memory for an object.

## Provenance

Reflects MISRA-C:2012 Rule 21.3, the FreeRTOS best-practices guide on static vs dynamic
allocation, and embedded-systems engineering consensus (Barr Group, Jack Ganssle). The
non-determinism and fragmentation arguments are verified in the FreeRTOS documentation and
in standard embedded-systems textbooks (e.g. _Making Embedded Systems_, Elecia White).

---

_Last reviewed: 2026-06-08 by `claude`._
