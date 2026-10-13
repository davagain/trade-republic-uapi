# TRA-23: local read-only wrapper boundary

## Intent

Publish the preserved local wrapper changes in the personal fork. Restrict the
HTTP server to loopback, allow only selected read queries by default, and protect
browser session state while saving or refreshing it.

## Acceptance criteria

- Missing or invalid HTTP credentials reject the request.
- Order and price-alarm mutations are rejected before broker transport is called.
- Other routes fail closed unless explicitly enabled by `TR_UAPI_ALLOW_WRITES=1`.
- The server binds to `127.0.0.1`.
- Session state is written inside a directory with mode `0700`, through a
  temporary file with mode `0600`, then atomically replaces the previous state.
- A failed capture or replacement preserves the previous session file and
  removes temporary files.

## Scope limits

The wrapper does not reduce permissions of the underlying broker session.
Human authentication and independent live reads have not been validated here.
Timeouts, reconnection, pagination and recurrent import remain separate pending
work. No broker mutations, deployment, PyPI release or live authentication are
performed by this change. The market-signals adapter is a separate PR.

## Validation

Eleven offline unittest cases cover the access policy, HTTP key validation,
transport isolation, loopback binding, session permissions and failed refresh
or replacement. Package/test compilation and `git diff --check` pass.
