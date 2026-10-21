# Qiskit 2.x Migration — Lessons Learned
<!-- Agent memory. Concise, reusable across projects. Load before any Qiskit migration. -->

## PhaseOracle → PhaseOracleGate (deprecated 2.2, removed 3.0)

`PhaseOracleGate` is a `Gate`, not a `QuantumCircuit`. Must wrap before use:
```python
from qiskit.circuit.library import PhaseOracleGate
gate = PhaseOracleGate(expression)
oracle = QuantumCircuit(gate.num_qubits)
oracle.append(gate, range(gate.num_qubits))
```
`evaluate_bitstring` is gone. Evaluate the expression with project-side logic or
`BooleanExpression.simulate()` — but see warning below.

**`qiskit.circuit.classicalfunction` is an optional C-extension — often missing even
with `qiskit[all]`.** Any import raises `ModuleNotFoundError`. Do not use it.
Prefer a pure-Python oracle checker the project already owns, or implement one.

`tweedledum` no longer needed — `PhaseOracleGate` uses built-in synthesis. Remove from deps.

---

## qiskit-algorithms → native grover_operator

`qiskit_algorithms.Grover` + `AmplificationProblem` = community package over removed
`qiskit.algorithms`. Replace with native `qiskit.circuit.library.grover_operator` (function):
```python
from qiskit.circuit.library import grover_operator
from qiskit.primitives import StatevectorSampler

grover_op = grover_operator(oracle)          # oracle = QuantumCircuit
circuit = QuantumCircuit(oracle.num_qubits)
circuit.h(range(oracle.num_qubits))          # state prep
circuit.compose(grover_op, inplace=True)     # 1 iteration; loop for more
circuit.measure_all()

counts = StatevectorSampler().run([circuit], shots=1024).result()[0].data.meas.get_counts()
top = max(counts, key=counts.get)
```
For k iterations: `for _ in range(k): circuit.compose(grover_op, inplace=True)`.
Large k on many qubits is slow with `StatevectorSampler`; use 1 for debugging.

`GroverResult` fields gone: `top_measurement`, `oracle_evaluation`, `circuit_results[0]`.
Manual equivalents: `max(counts, key=counts.get)`, project oracle fn, `counts` directly.

`grover_operator(oracle).decompose().draw('mpl')` replaces
`problem.grover_operator.oracle.decompose().draw('mpl')`.

---

## SamplerV2 result access chain

```python
counts = job.result()[0].data.<creg_name>.get_counts()
# measure_all() → creg name is 'meas' → .data.meas
```
DataBin attribute = classical register name. Custom creg → use that name.

---

## plot_state_qsphere

Requires `Statevector`, not bare `QuantumCircuit`:
```python
plot_state_qsphere(Statevector(circuit))
```

---

## generate_preset_pass_manager import

```python
from qiskit.transpiler import generate_preset_pass_manager        # correct
# NOT: from qiskit.transpiler.preset_passmanagers import ...
```

---

## qiskit-docs MCP — efficient lookup pattern

1. `search_docs_tool(query, scope="api")` — scope cuts noise for API lookups.
2. `get_page_tool(url)` on the returned URL for full content.

Confirmed useful URLs (prefix `https://quantum.cloud.ibm.com/docs/en/`):
- `api/qiskit/qiskit.circuit.library.PhaseOracleGate`
- `api/qiskit/qiskit.circuit.library.grover_operator`
- `api/qiskit/qiskit.circuit.library.GroverOperator`
- `api/qiskit/qiskit.primitives.StatevectorSampler`
- `api/qiskit/utils#qiskitutilsoptionalshas_tweedledum`
- `guides/qiskit-2.0`

---

## executor_sampler.Sampler version gate

`qiskit_ibm_runtime.executor_sampler.Sampler` was introduced in **0.50.0**.
On 0.47.x (pinned here) it does not exist — `ImportError` on any attempt.

For 0.47.x use `from qiskit_ibm_runtime import SamplerV2 as Sampler`.
Upgrade to `qiskit-ibm-runtime~=0.50` to use `executor_sampler.Sampler`.

---

## Dependency audit (Qiskit 2.5.x)

| Remove | Reason |
|---|---|
| `tweedledum` | `PhaseOracleGate` uses built-in synthesis |
| `qiskit-algorithms` | Replaced by `grover_operator` in `qiskit.circuit.library` |

Minimal viable install: `qiskit[all]`, `qiskit-aer`, `qiskit-ibm-runtime`, `matplotlib`.
