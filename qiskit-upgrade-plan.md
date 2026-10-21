# Qiskit Upgrade Plan

> **Reviewed against live Qiskit docs** (qiskit~=2.5.2, qiskit-ibm-runtime~=0.47.0) on 2026-10-08.
> Source pages: [Qiskit 1.0 feature changes](https://quantum.cloud.ibm.com/docs/guides/qiskit-1.0-features),
> [Qiskit 2.0 migration guide](https://quantum.cloud.ibm.com/docs/guides/qiskit-2.0),
> [Exact simulation with Qiskit SDK primitives](https://quantum.cloud.ibm.com/docs/guides/simulate-with-qiskit-sdk-primitives),
> [Run your first circuit on hardware](https://quantum.cloud.ibm.com/docs/guides/hello-world),
> [PhaseOracle API](https://quantum.cloud.ibm.com/docs/api/qiskit/qiskit.circuit.library.PhaseOracle),
> [PhaseOracleGate API](https://quantum.cloud.ibm.com/docs/api/qiskit/qiskit.circuit.library.PhaseOracleGate),
> [fake_provider API](https://quantum.cloud.ibm.com/docs/api/qiskit-ibm-runtime/fake-provider),
> [IBM Quantum Compute Service changelog](https://quantum.cloud.ibm.com/docs/guides/changelog-quantum-compute-service)

## Overview

Upgrade `quantum-search-example.ipynb` from Qiskit 0.43 / qiskit-terra 0.24 (the legacy pre-1.x
pinned environment) to the current **Qiskit 2.x** + latest `qiskit-ibm-runtime`. The work has two
independent migration layers:

**Layer 1 — Qiskit core (`qiskit.*`)**:
- `qiskit.algorithms` removed in Qiskit 1.0 → replaced by `qiskit-algorithms` community package
- `qiskit.primitives.Sampler` (V1) has no implementation in Qiskit 2.x → `qiskit.primitives.StatevectorSampler` (V2 reference, confirmed in Qiskit 1.0 migration guide)
- `from qiskit import Aer` → `from qiskit_aer import AerSimulator` (confirmed in Qiskit 1.0 guide)
- **Open risk**: `qiskit-algorithms.Grover(sampler=...)` — whether it accepts `BaseSamplerV2` or requires `BaseSamplerV1` depends on the installed `qiskit-algorithms` version. IBM docs do not cover this package. The implementing subtask must verify this before editing.
- **`PhaseOracle` is deprecated** as of Qiskit 2.2 (removal in Qiskit 3.0); replacement is `PhaseOracleGate`. Per user instruction, all `PhaseOracle` usages are **migrated** to `PhaseOracleGate` in this task. **Important structural difference**: `PhaseOracleGate` is a `Gate`, not a `QuantumCircuit`. It must be wrapped: `qc = QuantumCircuit(gate.num_qubits); qc.append(gate, range(gate.num_qubits))` before being passed to `AmplificationProblem`. Also, `PhaseOracleGate` has **no** `evaluate_bitstring` method — `is_good_state` in `AmplificationProblem` must be provided as a standalone callable or list of good bitstrings instead.

**Layer 2 — `qiskit-ibm-runtime`**:
- V1 `Sampler` + flat `Options` → client-side Executor-backed `SamplerV2` (hop B, confirmed in hello-world guide: `from qiskit_ibm_runtime.executor_sampler import Sampler`)
- `channel="ibm_quantum"` → not needed. Newest IBM docs show `QiskitRuntimeService.save_account(token=..., instance=...)` without `channel=` at all (defaults to `ibm_quantum_platform`). Update the commented markdown cell to the current pattern.
- `Session(service=service, backend=backend)` → `Session(backend_object)`
- ISA circuit transpilation via `generate_preset_pass_manager(backend=backend, optimization_level=1)` required before `.run()` (confirmed in Qiskit 2.0 docs; `backend=` preferred over loose args)
- **QPU reference**: `ibmq_belem` (5 qubits, retired) → **`ibm_kingston`** (Heron r2, 156 qubits). `ibm_kingston` was added to the **Open Plan** in April 2026 (confirmed in IBM Quantum Compute Service changelog) — it is the highest-performing QPU available to free-tier users. `ibm_phoenix` (Nighthawk r2, 120 qubits) is available only on Premium/Flex/Pay-As-You-Go plans, not Open Plan. The full 21-variable model requires ≥ 21 qubits; `ibm_kingston` at 156 qubits covers this comfortably. Per user instruction, `ibm_kingston` replaces `ibmq_belem` throughout.
- **Fake backend for local testing**: `FakeKingston` (156 qubits) — confirmed in the `qiskit-ibm-runtime` fake provider docs — is the correct local-testing substitute for `ibm_kingston`.

**Scope**: Only cells that contain Qiskit quantum execution code are modified. Pure-Python cells
(ATTRIBUTE_REGISTRY, SearchQuery dataclass, CULTIVARES dataset, build_expression, decode_result,
cultivar_matches) are untouched — they have zero Qiskit dependency.

---

## Sub-Task 1 — Update `requirements.txt` and environment for Qiskit 2.x

**Status**: [ ] pending

### Intent
The `requirements.txt` is a conda-format pinfile locking everything to the `linux-64` Qiskit 0.43
era. Running the upgraded notebook requires:
- `qiskit >= 2.0` (removes `qiskit-terra` as a separate package; `qiskit.algorithms` is gone; V1 primitives have no implementation)
- `qiskit-aer` (standalone since Qiskit 1.0; `qiskit[all]` pulls it in, but listing explicitly is clearer)
- `qiskit-algorithms` (community continuation of the removed `qiskit.algorithms` module)
- `qiskit-ibm-runtime >= 0.50.0` (for hop B client-side Executor primitives)
- `tweedledum` (required by `PhaseOracle`; cells already guard with `try/except MissingOptionalLibraryError`)

### Expected Outcomes
- `requirements.txt` is updated so a fresh environment produces a working Qiskit 2.x + modern runtime setup.
- The file clearly lists which package provides which symbol, with a comment block at the top.
- First markdown cell of the notebook updated to match the new install command.

### Todo List
1. Read `requirements.txt` to identify the current pinned packages.
2. Determine latest compatible versions of `qiskit`, `qiskit-aer`, `qiskit-algorithms`, and `qiskit-ibm-runtime`.
3. Rewrite the file. If Qiskit 2.x conda packages are unavailable on `defaults`/`conda-forge`, switch to a plain pip `requirements.txt`. Keep usable for `linux-64` Python 3.11+.
4. Add a comment block at the top mapping each package to the symbols it provides.
5. Update the first markdown cell in the notebook to reflect the new install command.

### Relevant Context
- [`requirements.txt`](requirements.txt)
- IBM docs recommend `pip install qiskit[all]` for the full Qiskit SDK (includes `qiskit-aer`)
- `qiskit-algorithms` PyPI package is the community continuation of `qiskit.algorithms`
- `tweedledum` is needed for `PhaseOracle`; `MissingOptionalLibraryError` is already caught

---

## Sub-Task 2 — Replace `qiskit.algorithms` imports with `qiskit_algorithms`

**Status**: [ ] pending

### Intent
`qiskit.algorithms` was removed in Qiskit 1.0. All three execution cells that import `Grover` or
`AmplificationProblem` from it must switch to `qiskit_algorithms` (the PyPI package
`qiskit-algorithms`). The API is identical — this is a mechanical import-path change.

Additionally, `PhaseOracle` is **deprecated as of Qiskit 2.2** (removed in 3.0). The cells already
use `try/except MissingOptionalLibraryError`; add a `# TODO: migrate to PhaseOracleGate before
Qiskit 3.0` comment in each cell that uses it, so the deprecation is visible without forcing a
structural rewrite in this task.

**Open risk — `qiskit-algorithms` sampler interface**: The `Grover(sampler=...)` parameter
expects either a `BaseSamplerV1` or `BaseSamplerV2`. Older `qiskit-algorithms` versions (< 0.3)
required V1; newer versions (≥ 0.3) support V2. **Before editing Sub-Task 4**, the implementer
must confirm which interface the installed version of `qiskit-algorithms` requires. If it requires
V1, the `StatevectorSampler` plan in Sub-Task 4 is wrong and `StatevectorSampler` cannot be used
directly — a V1 shim or a newer `qiskit-algorithms` version is needed.

### Expected Outcomes
- All `from qiskit.algorithms import ...` replaced with `from qiskit_algorithms import ...`.
- No `ImportError` on cells 1, 7, and the full pipeline cell.
- A `# TODO: migrate to PhaseOracleGate before Qiskit 3.0` comment appears in each cell that uses `PhaseOracle`.

### Todo List
1. Confirm the `qiskit-algorithms` version being installed and whether `Grover` there accepts `BaseSamplerV2`. Document the finding in the plan before Sub-Task 4 begins.
2. In cell at notebook line ~34: `from qiskit.algorithms import AmplificationProblem` → `from qiskit_algorithms import AmplificationProblem`.
3. In cell at notebook line ~836: `from qiskit.algorithms import Grover` → `from qiskit_algorithms import Grover`.
4. In full pipeline cell at notebook line ~962: same two imports.
5. Add `# TODO: migrate to PhaseOracleGate before Qiskit 3.0` comment in all three `PhaseOracle` cells (lines ~889, ~919, ~962).
6. Grep for any remaining `qiskit.algorithms` imports.

### Relevant Context
- Notebook line 34: `from qiskit.algorithms import AmplificationProblem`
- Notebook line 836: `from qiskit.algorithms import Grover`
- Notebook line 962: full pipeline cell
- Notebook lines ~889, ~919, ~962: `PhaseOracle` usage
- [PhaseOracle API docs](https://quantum.cloud.ibm.com/docs/api/qiskit/qiskit.circuit.library.PhaseOracle): deprecated Qiskit 2.2, removed Qiskit 3.0; replacement is `PhaseOracleGate`

---

## Sub-Task 3 — Replace `Aer.get_backend` + `backend.run()` with `AerSimulator`

**Status**: [ ] pending

### Intent
`from qiskit import Aer` and `Aer.get_backend('qasm_simulator')` are removed in Qiskit 1.0.
The oracle-test cell uses this pattern to run a circuit and get counts. The documented replacement
(Qiskit 1.0 migration guide) is `from qiskit_aer import AerSimulator` + `transpile` + `backend.run()`.

### Expected Outcomes
- `from qiskit import Aer` replaced with `from qiskit_aer import AerSimulator`.
- `Aer.get_backend('qasm_simulator')` → `AerSimulator()`.
- `simulador.run(teste_oraculo)` → `simulador.run(transpile(teste_oraculo, simulador))`.
- `.result().get_counts()` unchanged — this return format is the same.
- Histogram cell still works.

### Todo List
1. In the first import cell (line ~34): replace `from qiskit import Aer` with `from qiskit_aer import AerSimulator`.
2. In the oracle-test cell (line ~799): replace:
   ```python
   simulador = Aer.get_backend('qasm_simulator')
   resultado_simulador = simulador.run(teste_oraculo).result()
   ```
   with:
   ```python
   from qiskit import transpile
   simulador = AerSimulator()
   resultado_simulador = simulador.run(transpile(teste_oraculo, simulador)).result()
   ```
3. Grep for any remaining `Aer.get_backend` calls.

### Relevant Context
- Notebook line 34: `from qiskit import Aer`
- Notebook lines 799–806: oracle-test execution cell
- [Qiskit 1.0 guide — Aer section](https://quantum.cloud.ibm.com/docs/guides/qiskit-1.0-features): "`qiskit.Aer` is not available in Qiskit v1.0. Instead, use the same object from the `qiskit_aer` namespace."
- `get_counts()` is unchanged; `AerSimulator.run()` requires a transpiled circuit in Qiskit 2.x.

---

## Sub-Task 4 — Replace `qiskit.primitives.Sampler` with `StatevectorSampler`

**Status**: [ ] pending

### Intent
`qiskit.primitives.Sampler` (V1) has no concrete implementation in Qiskit 2.x — only its abstract
base class `BaseSamplerV1` remains for backward compatibility. The V2 replacement confirmed by the
Qiskit 1.0 migration guide is `qiskit.primitives.StatevectorSampler`. This is the reference
implementation used throughout current Qiskit docs (`qiskit[all]~=2.5.2`).

**Prerequisite**: Sub-Task 2 must have confirmed the `qiskit-algorithms` version's sampler
interface requirement. If `qiskit_algorithms.Grover` requires `BaseSamplerV1`, `StatevectorSampler`
(a `BaseSamplerV2`) cannot be passed directly — resolve that first.

**Note**: `StatevectorSampler.run()` uses the V2 PUB interface (`run([(circuit,)])`), not the
V1 list form. `qiskit-algorithms.Grover` calls the sampler internally, so the caller code
(`Grover(sampler=StatevectorSampler())`) does not change — only the import changes.

### Expected Outcomes
- `from qiskit.primitives import Sampler` → `from qiskit.primitives import StatevectorSampler`.
- `Grover(sampler=Sampler())` → `Grover(sampler=StatevectorSampler())` in all cells.
- `result.circuit_results[0]` still works for `plot_histogram` (this is a `qiskit-algorithms` result attribute, unaffected by the Sampler swap).

### Todo List
1. Verify Sub-Task 2's sampler-interface finding is recorded before proceeding.
2. In the Grover+QuantumCircuit cell (line ~837): `from qiskit.primitives import Sampler` → `from qiskit.primitives import StatevectorSampler` and `Grover(sampler=Sampler())` → `Grover(sampler=StatevectorSampler())`.
3. In the full pipeline cell (line ~962): same replacement.
4. Confirm `result.circuit_results[0]` is a valid accessor on `qiskit_algorithms.GroverResult`.

### Relevant Context
- Notebook line 837: `from qiskit.primitives import Sampler`
- Notebook line 962: same import in the full pipeline cell
- [Qiskit 1.0 guide](https://quantum.cloud.ibm.com/docs/guides/qiskit-1.0-features): `qiskit.primitives.Sampler` → `qiskit.primitives.StatevectorSampler`
- [Simulate with Qiskit SDK primitives](https://quantum.cloud.ibm.com/docs/guides/simulate-with-qiskit-sdk-primitives): confirms `StatevectorSampler` is the current reference (docs use `qiskit[all]~=2.5.2`)
- AGENTS.md: "`iterations` is not portable — 1024 works on the local simulator but is impractical on real hardware"

---

## Sub-Task 5 — Migrate the IBM Runtime cell (V1 → V2 + hop B)

**Status**: [ ] pending

### Intent
The IBM hardware cells use multiple removed/deprecated `qiskit-ibm-runtime` APIs. The target is
the **client-side Executor-backed** `SamplerV2` (hop B), confirmed as the current recommended
destination in the IBM docs (`hello-world` guide, `qiskit-ibm-runtime~=0.47.0`).

| Issue | Old form | New form (doc-confirmed) |
|---|---|---|
| Auth pattern | `channel='ibm_quantum'` + `instance=` | `QiskitRuntimeService.save_account(token=..., instance=...)` — no `channel=` needed |
| Service constructor | `QiskitRuntimeService(channel='ibm_quantum', instance=...)` | `QiskitRuntimeService()` after saved credentials |
| V1 Sampler import | `from qiskit_ibm_runtime import ... Sampler` | `from qiskit_ibm_runtime.executor_sampler import Sampler` |
| V1 Options | `Options(optimization_level=3)` + `options.execution.shots = 1024` | `sampler.options.default_shots = 1000` |
| Session API | `Session(service=service, backend=backend)` | `Session(backend_object)` |
| ISA circuit | none | `generate_preset_pass_manager(backend=backend, optimization_level=1).run(circuit)` |
| V1 run() | `sampler.run(circuits=circuit, shots=1000)` | `sampler.run([(isa_circuit,)])` |
| V1 result | `result.quasi_dists` | `result[0].data.meas.get_counts()` |
| QPU target | `"ibmq_belem"` (5 qubits, retired) | `"ibm_kingston"` (Heron r2, 156 qubits, on Open Plan since April 2026) |
| Fake backend | `"ibmq_belem"` string | `FakeKingston()` — 156 qubits, confirmed in fake provider docs |

The hardware cell already uses `iterations=1` (correct for real hardware — `iterations=1024` is
only in the local simulator pipeline cell, not this cell).

### Expected Outcomes
- Import line splits: `QiskitRuntimeService, Session` stay on the original line; `Sampler` moves to `executor_sampler`.
- Auth markdown cell updated to reflect the current `save_account(token=..., instance=...)` pattern and note that `channel` is no longer required.
- `Options` class and its usage removed; shots set via `sampler.options.default_shots = 1000`.
- `Session(service=service, backend=backend)` → `with Session(backend) as session:` and `Sampler(mode=session)`.
- Circuit transpiled via `generate_preset_pass_manager(backend=backend, optimization_level=1).run(circuit)` before `.run()`.
- `sampler.run(circuits=circuit, shots=1000)` → `sampler.run([(isa_circuit,)])`.
- `result.quasi_dists` → `result[0].data.meas.get_counts()`.
- `plot_histogram(result.quasi_dists)` → `plot_histogram(result[0].data.meas.get_counts())`.
- A commented-out local-testing block using `FakeKingston` added for offline verification.

### Todo List
1. Read cells at lines 1039–1057 (service/options setup) and 1088–1119 (run/plot) precisely.
2. Split the import line: keep `QiskitRuntimeService, Session`; add `from qiskit_ibm_runtime.executor_sampler import Sampler`.
3. Update the markdown cell (lines ~1009–1036) to show the current `save_account(token=..., instance=...)` pattern (no `channel=`); add note that `ibm_kingston` is the Open Plan QPU.
4. Remove `Options(...)` and `options.execution.shots = 1024`.
5. Replace service constructor `QiskitRuntimeService(channel='ibm_quantum', instance=...)` with `QiskitRuntimeService()`.
6. Replace `backend = "ibmq_belem"` with `backend = service.backend("ibm_kingston")`. Add `# Alternatively: backend = service.least_busy(simulator=False, operational=True)` as a comment.
7. Replace `Session(service=service, backend=backend)` → `Session(backend)`.
8. Add `from qiskit.transpiler import generate_preset_pass_manager` import and transpile step.
9. Update `sampler.run(circuits=circuit, shots=1000)` → `sampler.run([(isa_circuit,)])` with `sampler.options.default_shots = 1000` set beforehand.
10. Update `result.quasi_dists` → `result[0].data.meas.get_counts()` throughout.
11. Update `plot_histogram(result.quasi_dists)` → `plot_histogram(result[0].data.meas.get_counts())`.
12. Add a commented-out local-testing block using `FakeKingston()` as the alternative backend.

### Relevant Context
- Notebook lines 1039–1057: service setup + Options
- Notebook lines 1088–1110: Grover circuit + Session + Sampler run
- Notebook lines 1113–1119: histogram plot cell
- [hello-world guide](https://quantum.cloud.ibm.com/docs/guides/hello-world): shows `executor_sampler` import, `Session(backend)`, `generate_preset_pass_manager`, `result[0].data.meas.get_counts()`
- [IBM Quantum Compute Service changelog April 2026](https://quantum.cloud.ibm.com/docs/guides/changelog-quantum-compute-service): `ibm_kingston` added to Open Plan
- [fake_provider docs](https://quantum.cloud.ibm.com/docs/api/qiskit-ibm-runtime/fake-provider): `FakeKingston` is 156 qubits
- AGENTS.md: "`iterations=1` for real hardware" — runtime cell already correct on this point

---

## Sub-Task 6 — Validation

**Status**: [ ] pending

### Intent
Verify the migrated notebook is syntactically correct and all targeted APIs are replaced. IBM
hardware cells cannot be executed without credentials, but structural checks catch the most
common mistakes.

### Expected Outcomes
- No remaining legacy API references (grep clean on all targeted patterns).
- Notebook JSON is valid.
- All sub-tasks marked `[x] done`.

### Todo List
1. Grep for remaining legacy patterns (each must return zero matches):
   - `qiskit.algorithms`
   - `from qiskit import Aer`
   - `quasi_dists`
   - `channel='ibm_quantum'` and `channel="ibm_quantum"`
   - `Session(service=`
   - `from qiskit_ibm_runtime import.*Options`
   - `from qiskit.primitives import Sampler`
2. Grep for expected new patterns (each must have at least one match):
   - `from qiskit_algorithms import`
   - `from qiskit_aer import AerSimulator`
   - `StatevectorSampler`
   - `from qiskit_ibm_runtime.executor_sampler import`
   - `generate_preset_pass_manager`
3. Validate notebook JSON: `python -m json.tool quantum-search-example.ipynb > /dev/null`.
4. Run `python -m py_compile` on extracted cell source if an environment is available.
5. Mark all sub-tasks `[x] done`.

### Relevant Context
- Entire notebook: [`quantum-search-example.ipynb`](quantum-search-example.ipynb)
- AGENTS.md: "No state is shared between kernel restarts — imports and all variable definitions must be re-run top-to-bottom."
