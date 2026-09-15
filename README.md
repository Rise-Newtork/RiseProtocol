# RiseProtocol

The repo where protobuf messages and services live. DO NOT commit generated
proto code to this repo, just `.proto` files under `src/main/proto`.

Both the Java and the Python artifacts are built from these files, so the schema
has exactly one source of truth.

## Java — via JitPack

### 1. Add JitPack

In your `build.gradle.kts`:

```kotlin
repositories {
    mavenCentral()
    maven("https://jitpack.io")
}
```

### 2. Add the Protocol dependency

```kotlin
dependencies {
    implementation("com.github.Rise-Newtork:RiseProtocol:VERSION")
}
```

Grab the version from the newest tag/release. The `.proto` files ship inside the
jar, so consumers can import the schema straight out of the artifact.

## Python — via pip

The repo is private, so pip needs a read-only token (see below):

```bash
pip install "git+https://github.com/Rise-Newtork/RiseProtocol@VERSION"
```

```python
from rise_protocol.error import error_pb2, error_service_pb2_grpc
```

`hatch_build.py` runs protoc at install time and stages the protos under a
`rise_protocol/` prefix, so the generated modules land in one namespace rather
than installing top-level `error` and `common` packages into site-packages.
Only the file paths change — the proto `package life;` is untouched, so
descriptor names stay `life.ErrorMessage` and the wire format is identical on
both sides.

### Read-only token

For CI and Docker builds, use a fine-grained PAT scoped to this repo alone:
Resource owner `Rise-Newtork`, Repository access → only RiseProtocol,
Permissions → Contents: **Read-only**.

Don't put the token in the URL — it ends up in shell history and pip's logs.
Point git at it instead:

```bash
git config --global url."https://x-access-token:<TOKEN>@github.com/".insteadOf "https://github.com/"
```

## Making a release

Keep `version` in `build.gradle.kts` and `pyproject.toml` in step with the tag,
so one version string means one protocol version everywhere. Note that Gradle
carries the `v` prefix and `pyproject.toml` does not — PEP 440 forbids it.

```bash
git tag v1.0.0
git push origin v1.0.0
```
