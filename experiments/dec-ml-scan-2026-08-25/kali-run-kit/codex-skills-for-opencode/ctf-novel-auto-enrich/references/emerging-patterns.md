# Emerging CTF Pattern Hints

Use this as a quick routing checklist for unfamiliar or hybrid CTF challenges.

## Browser and Frontend State

Signals: bundled JS, source maps, localStorage/sessionStorage, feature flags, client-side auth, web workers, WASM loaded by a web page.

Cheap probes: inspect routes, search JS for `flag`, `admin`, `debug`, `api`, `graphql`, `wasm`, `localStorage`; check source maps; replay API calls from DevTools/network logs.

## AI Agent or LLM Challenges

Signals: prompt injection, tool-use rules, hidden system text, RAG retrieval, moderation bypass, model extraction, "agent", "assistant", "memory", "tools".

Cheap probes: map inputs and outputs, identify tool boundaries, test benign instruction hierarchy, search for leaked context or retrieval keys, preserve exact prompts and responses.

## Web3 and ZK

Signals: smart contract address, ABI, wallet flow, Merkle proof, circuit, verifier, calldata, chain RPC, frontend/backend mismatch.

Cheap probes: read contract/source/ABI, inspect frontend calls, decode calldata/events, simulate locally when possible, compare claimed constraints with verifier checks.

## Cloud, CI, and Supply Chain

Signals: S3/GCS/Azure blob URLs, GitHub Actions logs, Docker images, package lockfiles, npm/pip tokens, metadata endpoints, Terraform.

Cheap probes: enumerate only challenge-scoped buckets/repos/images, inspect CI logs and artifacts, search env variable names, check image layers and package scripts.

## Weird Protocols and APIs

Signals: custom binary frames, GraphQL/gRPC/WebSocket, protobuf, IoT-like endpoints, state machines, challenge-specific DSLs.

Cheap probes: capture one valid request, infer schema from errors, replay minimal messages, mutate one field at a time, save a parser or request script once the frame shape is known.

## Constraint, Game, and Simulator Puzzles

Signals: rules engine, scoring oracle, scheduler, map/grid/physics, SAT-like conditions, randomized seeds.

Cheap probes: extract deterministic seed, write a local verifier, brute force only after reducing state, use SMT/ILP/search when constraints are explicit.
