# RiseProtocol

The protobuf and gRPC contract every Rise component speaks. Only `.proto` files live in this
repo, under `src/main/proto`; the Java and the Python artifacts are both generated from them, so
the schema has exactly one source of truth. Generated code is never committed.

RiseMatchmaker is the control plane and hosts most of the services. RiseProxy, RiseHubs,
RiseMinigames, RiseContainerCreator, DependSync and RiseSessionBroker call them, and host the few
services pointed back at them. Everything depends on this repo; this repo depends on nothing.
`src/main/proto` has one directory per domain — `common`, `container`, `database`, `depend`,
`error`, `game`, `moderation`, `proxy`, `queue`, `routing`, `server`, `session` — and one service
per domain, with its messages beside it or in a plain data file next to it where more than one
service shares them.

## Building

JDK 25. `./gradlew build` compiles the descriptors and generates the Java;
`./gradlew publishToMavenLocal` puts the artifact in `~/.m2` for a consumer to pick up before the
tag exists. `jitpack.yml` pins `openjdk21` for JitPack's own container, which only runs Gradle:
the foojay resolver in `settings.gradle.kts` downloads the JDK 25 toolchain the compile needs.

## Consuming from Java

JitPack serves each tag as `com.github.Rise-Newtork:RiseProtocol:<tag>`, `v` prefix included:

```kotlin
repositories { mavenCentral(); maven("https://jitpack.io") }
dependencies { implementation("com.github.Rise-Newtork:RiseProtocol:v1.17.0") }
```

JitPack has failed to build a tag before, and the Docker builds have no `~/.m2`, so most
consumers also vendor the artifact under `libs/m2` and declare that directory as a repository
ahead of everything else. To move one to a new version: `./gradlew publishToMavenLocal` here, copy
`~/.m2/repository/com/github/Rise-Newtork/RiseProtocol/<tag>` into the consumer's
`libs/m2/com/github/Rise-Newtork/RiseProtocol/`, and bump the version string in its
`build.gradle.kts`. RiseProxy has dropped its vendored copy and takes the tag from JitPack alone.
The `.proto` files ship inside the jar either way, so a consumer imports the schema out of the
artifact rather than keeping a copy of it.

## Consuming from Python

The repo is private, so pip needs a read-only token: a fine-grained PAT, owner `Rise-Newtork`,
repository access only RiseProtocol, Contents read-only. Don't put it in the URL, where it lands
in shell history and pip's logs; point git at it with `git config --global
url."https://x-access-token:<TOKEN>@github.com/".insteadOf "https://github.com/"`.

```bash
pip install "git+https://github.com/Rise-Newtork/RiseProtocol@v1.17.0"
```

Modules come out as `from rise_protocol.error import error_pb2, error_service_pb2_grpc`.
`hatch_build.py` runs protoc at install time, staging a throwaway copy of the proto tree under a
`rise_protocol/` prefix and rewriting that copy's imports, so the generated modules land in one
namespace instead of installing top-level `error` and `common` packages into site-packages. Only
file paths change: `package life;` is untouched, descriptor names stay `life.ErrorMessage`, and
the wire format is identical to Java's. The generated `rise_protocol/` is gitignored, so the wheel
target sets `ignore-vcs = true` — without it hatchling would honour the ignore and ship an empty
wheel.

## What a new proto file must look like

`package life;`, `option java_package = "com.risehytale.api";`,
`option java_multiple_files = true;`, camelCase field names, one service per domain. Every
response is an `Ack` carrying `bool success = 1; string error = 2;` — a failure is an unsuccessful
Ack with a reason, never a gRPC status — and every write is safe to retry, which means the caller
mints the id and a repeat is acknowledged as a duplicate. A game mode is the `GameMode` enum, and
where it has to be text, the protobuf constant name with its prefix.

Two traps. A basename that already exists in the same `java_package` derives the same Java outer
class and collides, which is why the match lifecycle is `game/match_lifecycle.proto` and not
`game/match.proto`. And inside a `service` a bare message name resolves to a method of the same
name first, so a `Heartbeat`-style RPC names its request fully qualified,
`.life.ContainerCreatorHeartbeat`.

## Enum numbers are not enum order

A number is wire identity. Appending a constant is backwards compatible; renumbering is not, and
would make every un-redeployed server's value arrive as something else. `ErrorSeverity` is the
standing example: `ERROR_SEVERITY_INFO` is the mildest level but carries **5**, because the other
four shipped first. Never rank by the raw number — map through a table; the order is
`UNSPECIFIED(0) < INFO(5) < WARN(1) < ERROR(2) < CRITICAL(3) < FATAL(4)`. Constant names are
deployment data in their own right, matched by string in repos that never see this one:
`SERVER_TYPE_*` in DependSync's manifests and the container entrypoint, `GAMEMODE_*` in the
RiseConfigured bucket's configs. Renaming one is a deployment change, not a refactor.

## Making a release

A published version is immutable, so a change to a released schema means a new version. Keep
`version` in `build.gradle.kts` and `pyproject.toml` in step with the tag, so one version string
means one protocol version everywhere. Gradle carries the `v` prefix and `pyproject.toml` does
not, because PEP 440 forbids it. Then tag and push the tag; JitPack builds it on first request.
