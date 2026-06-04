# Hardened multi-stage Dockerfile (pattern)

```dockerfile
# --- build stage ---
FROM build-base@sha256:<PIN> AS build
WORKDIR /src
COPY <lockfiles> ./
RUN <install deps>            # cached layer keyed on lockfiles
COPY . .
RUN <build>

# --- runtime stage: minimal, non-root, no toolchain ---
FROM distroless@sha256:<PIN>
USER 65532:65532
COPY --from=build /src/out /app
ENTRYPOINT ["/app/server"]
```

- Base images pinned by **digest**.
- No compiler/package manager in the runtime layer.
- Runs as **non-root**.
- SBOM generated at build and attached; image scanned on push.
