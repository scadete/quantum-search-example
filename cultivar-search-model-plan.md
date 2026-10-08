# Cultivar Search Model Plan

## Overview

Extend the quantum search notebook to support a **structured, named search model** for soy cultivar
selection based on real agronomic attributes from the Embrapa Centro-Sul 2013 catalogue.

The current notebook uses an opaque 5-variable boolean expression (`a–e`) with no mapping to domain
attributes. This plan replaces that with:

1. A typed `SearchQuery` dataclass that captures the user's search criteria by name.
2. A boolean variable registry that maps each named attribute to a single-letter quantum variable.
3. A dataset cell that encodes a sample of cultivars from the Embrapa PDF as Python dicts.
4. A query builder that translates a `SearchQuery` into a `PhaseOracle` boolean expression.
5. A result decoder that maps quantum bitstrings back to matching cultivar names.

The solution targets the **local Aer simulator** (no qubit limit constraint). Real hardware
requires a device with ≥ the number of active boolean variables; `ibmq_belem` (5 qubits) is
**not compatible** with the full 12-variable model and is noted as such in the notebook.

---

## Sub-Tasks

---

### Sub-Task 1 — Define the Attribute Schema and Boolean Variable Registry

**Intent**
Create a single authoritative mapping from every named domain attribute to a short boolean
variable name. This registry is the contract between the user-facing data model and the
`PhaseOracle` string builder. It must be defined before any other cell can reference it.

**Expected Outcomes**
- A Python dict `ATTRIBUTE_REGISTRY` in a new notebook cell that maps every attribute name to
  its single-letter (or short) boolean variable identifier.
- Coverage of all attribute groups split as follows:
  - `macro_regiao`: one boolean per macro-region group: `macro_1`, `macro_2`, `macro_3`
  - `sub_regiao`: one boolean per sub-region index: `sub_1`, `sub_2`, `sub_3`, `sub_4`
    A region code like `201` is expressed in the oracle as `(macro_2 & sub_1)`.
    A user query for `['101', '301']` becomes `(macro_1 & sub_1) | (macro_3 & sub_1)`.
  - `mes_semeadura`: one boolean variable per sowing month
    (e.g. `mes_set`, `mes_out`, `mes_nov`, `mes_dez`)
  - 10 disease resistances (R only = True):
    `res_cancro_haste`, `res_mancha_olho_ra`, `res_oidio`, `res_podridao_parda_haste`,
    `res_podridao_fitoftora`, `res_mosaico_comum`, `res_virus_necrose_haste`,
    `res_nema_incognita`, `res_nema_javanica`, `res_nema_cisto`
- Each variable name is a valid Python identifier and unique across the full registry.

**Todo List**
- [ ] Add a new cell at the top of the notebook (after imports).
- [ ] Define `ATTRIBUTE_REGISTRY` as `dict[str, str]` mapping attribute name → boolean var name.
- [ ] Add an inline comment documenting the R-only convention for disease resistance booleans.
- [ ] Add an inline comment noting the qubit count implication (total variables = len of registry).
- [ ] Add an inline comment explaining the macro/sub-region split and listing the 12 region codes
      (101–104, 201–204, 301–304) as defined in the Embrapa Centro-Sul 2013 catalogue.

**Relevant Context**
- Cell ordering: this cell must appear before the `SearchQuery` cell and before the dataset cell.
- Variable names feed directly into the `PhaseOracle` expression string — they must be valid
  Python identifiers (no hyphens, no spaces).

**Status** — `[ ] pending`

---

### Sub-Task 2 — Define the `SearchQuery` Dataclass

**Intent**
Give the user a typed, self-documenting interface for expressing search criteria. Each field
corresponds to a real agronomic attribute. Fields are optional (default `None`) so the user
can search on any subset of criteria; `None` means "don't constrain this attribute".

**Expected Outcomes**
- A `SearchQuery` dataclass (using `@dataclass` from `dataclasses` stdlib) in a new notebook cell.
- Fields:
  - `regiao_edafoclimatica: list[str] | None` — list of acceptable full region codes
    (e.g. `['101', '102', '301']`); `None` = any region. The builder decomposes each code
    into its macro and sub-region boolean pair internally.
  - `mes_semeadura: list[str] | None` — list of acceptable sowing months
    (e.g. `['OUT', 'NOV']`); `None` = any month.
  - One `bool | None` field per disease resistance:
    `cancro_haste`, `mancha_olho_ra`, `oidio`, `podridao_parda_haste`,
    `podridao_fitoftora`, `mosaico_comum`, `virus_necrose_haste`,
    `nema_incognita`, `nema_javanica`, `nema_cisto`.
    `True` = must be resistant (R); `False` = not constrained; `None` = not constrained.
- A docstring on the class explaining the `None` / `True` / `False` semantics.
- A usage example in a markdown cell immediately after.

**Todo List**
- [ ] Add a new code cell after Sub-Task 1's cell.
- [ ] Import `dataclass` and `field` from `dataclasses`.
- [ ] Define `SearchQuery` with all fields, correct types, and `field(default=None)` defaults.
- [ ] Add a docstring to the class.
- [ ] Add a markdown cell with a short usage example showing a concrete `SearchQuery` instance.

**Relevant Context**
- Field names intentionally differ from the registry variable names — the registry handles the
  mapping internally. Keep field names human-readable.
- `list[str]` for region/month lets the user express OR logic ("PR or SC") naturally.

**Status** — `[ ] pending`

---

### Sub-Task 3 — Build the Cultivar Dataset Cell

**Intent**
Encode a representative sample of cultivars from the Embrapa Centro-Sul 2013 PDF as a Python
list of dicts. This is the "database" the quantum search runs against. Each cultivar entry
must use the same attribute keys as `ATTRIBUTE_REGISTRY` so the query builder can match them.

**Expected Outcomes**
- A new notebook cell containing `CULTIVARES: list[dict]`.
- Each dict has keys matching `ATTRIBUTE_REGISTRY` plus a `"nome"` key for the cultivar name.
- Boolean values for disease resistance use the R-only convention (True = rated R).
- Region and month values are stored as lists (a cultivar can span multiple regions/months).
- A markdown cell above explaining the data source (Embrapa PDF URL) and the R-only convention.
- At minimum 10–15 cultivar entries sourced manually from the Embrapa PDF.

**Todo List**
- [ ] Attempt to fetch and parse the Embrapa PDF programmatically
      (URL: https://www.infoteca.cnptia.embrapa.br/infoteca/bitstream/doc/976493/1/CATALOGOSojaCentrosul2013.pdf).
      If the PDF cannot be fetched or parsed (network block, format issues), ask the user to
      provide the raw table data before proceeding with this sub-task.
- [ ] Extract cultivar rows: nome, regiões (codes 101–304), meses de semeadura, and all 10
      disease resistance ratings (R = True, anything else = False).
- [ ] Add a markdown cell citing the source PDF URL and noting the R-only convention.
- [ ] Add a code cell defining `CULTIVARES` as a list of attribute dicts, one per cultivar.
- [ ] Verify that every dict has exactly the same set of keys (matching `ATTRIBUTE_REGISTRY`
      plus `"nome"`).
- [ ] Add an inline comment noting this is a sample or full extraction — state how many
      cultivars were captured vs the total in the catalogue.

**Relevant Context**
- PDF URL: https://www.infoteca.cnptia.embrapa.br/infoteca/bitstream/doc/976493/1/CATALOGOSojaCentrosul2013.pdf
- Standard resistance codes: R, MR, MS, S, AT — store `True` only for R.
- Cultivar name format: prefix + number or descriptor (e.g. `BRS 1001`, `TMG 308`).
- This cell must appear after the registry and `SearchQuery` cells but before the search cells.

**Status** — `[ ] pending`

---

### Sub-Task 4 — Implement the Expression Builder

**Intent**
Translate a `SearchQuery` instance into a boolean expression string accepted by `PhaseOracle`.
This is the bridge between the human-readable query model and the quantum oracle.

**Expected Outcomes**
- A function `build_expression(query: SearchQuery) -> str` in a new code cell.
- Logic:
  - For each non-None field in the query, add the corresponding boolean variable(s) to the expression.
  - Region and month lists become OR clauses: `(regiao_pr | regiao_sc)`.
  - Disease resistance `True` fields become AND-required terms.
  - All active constraints are ANDed together at the top level.
  - If no constraints are set, raise a `ValueError` (an unconstrained search is not useful).
- A short test/demo cell beneath it showing `build_expression` called with a sample `SearchQuery`
  and printing the resulting expression string.

**Todo List**
- [ ] Add a new code cell after the dataset cell.
- [ ] Implement `build_expression(query: SearchQuery) -> str`.
- [ ] Handle region OR logic: decompose each code (e.g. `'201'`) into
      `(macro_2 & sub_1)`, then OR the resulting pairs:
      `['101', '301']` → `((macro_1 & sub_1) | (macro_3 & sub_1))`.
- [ ] Handle month OR logic (list → `(v1 | v2 | ...)`).
- [ ] Handle disease AND logic (True field → include variable in top-level AND).
- [ ] Raise `ValueError` with a descriptive message when all fields are None.
- [ ] Add a demo cell that prints the expression for a concrete query.

**Relevant Context**
- `PhaseOracle` accepts standard Python boolean operators: `&`, `|`, `~`, parentheses.
- Variable names must match exactly what is in `ATTRIBUTE_REGISTRY`.
- The number of unique variables in the expression determines the qubit count used by Grover.

**Status** — `[ ] pending`

---

### Sub-Task 5 — Implement the Result Decoder

**Intent**
Map quantum bitstrings returned by Grover back to cultivar names. The Grover result is a
bitstring over all boolean variables; a cultivar matches if its attribute profile satisfies
the same expression.

**Expected Outcomes**
- A function `decode_result(top_measurement: str, query: SearchQuery) -> list[str]` that
  returns the names of cultivars whose attribute profile is consistent with the measurement.
- A helper `cultivar_matches(cultivar: dict, query: SearchQuery) -> bool` that classifies
  a cultivar against a query classically (used to validate/cross-check quantum output).
- A demo cell that runs the full pipeline: constructs a `SearchQuery`, calls `build_expression`,
  runs Grover on the local simulator, decodes the result, and prints matching cultivar names.

**Todo List**
- [ ] Add a new code cell after the expression builder cell.
- [ ] Implement `cultivar_matches(cultivar: dict, query: SearchQuery) -> bool`.
- [ ] Implement `decode_result(top_measurement: str, query: SearchQuery) -> list[str]`
      using classical matching against `CULTIVARES`.
- [ ] Update the existing Grover execution cell to use `build_expression` instead of the
      hardcoded `'(a | b | c | d | e) & (a & d & e)'` expression.
- [ ] Add a final demo cell that prints: query used, expression built, top measurement,
      and matching cultivar names.

**Relevant Context**
- `result.top_measurement` from `Grover.amplify()` is the most probable bitstring.
- Classical matching in `cultivar_matches` is the ground-truth validator — quantum result
  should agree with it for the target cultivar(s).
- The existing cell 11 (`grover = Grover(sampler=Sampler(), iterations=1024)`) is the
  local simulator execution cell to update.

**Status** — `[ ] pending`

---

## Architecture Diagram

```
SearchQuery (dataclass)
    |
    v
build_expression()  <--  ATTRIBUTE_REGISTRY (name → var mapping)
    |
    v
PhaseOracle(expression)
    |
    v
AmplificationProblem + Grover (local Aer simulator)
    |
    v
result.top_measurement  (bitstring)
    |
    v
decode_result() / cultivar_matches()  <--  CULTIVARES (dataset)
    |
    v
Matching cultivar names
```

## Qubit Count Note

The full registry has 21 boolean variables (3 macro-regions + 4 sub-regions + 4 months + 10 diseases).
This is down from 26 had all 12 region codes been represented as flat booleans.
A query that constrains all groups uses up to 21 qubits. The local `qasm_simulator`
supports this. `ibmq_belem` (5 qubits) cannot run the full model — only sub-expressions
of ≤ 5 active variables are compatible with that device.

## Region Encoding Reference

Region codes are decomposed into two independent boolean dimensions:

| Code | macro var | sub var | Combined expression  |
|------|-----------|---------|----------------------|
| 101  | macro_1   | sub_1   | macro_1 & sub_1      |
| 102  | macro_1   | sub_2   | macro_1 & sub_2      |
| 103  | macro_1   | sub_3   | macro_1 & sub_3      |
| 104  | macro_1   | sub_4   | macro_1 & sub_4      |
| 201  | macro_2   | sub_1   | macro_2 & sub_1      |
| 202  | macro_2   | sub_2   | macro_2 & sub_2      |
| 203  | macro_2   | sub_3   | macro_2 & sub_3      |
| 204  | macro_2   | sub_4   | macro_2 & sub_4      |
| 301  | macro_3   | sub_1   | macro_3 & sub_1      |
| 302  | macro_3   | sub_2   | macro_3 & sub_2      |
| 303  | macro_3   | sub_3   | macro_3 & sub_3      |
| 304  | macro_3   | sub_4   | macro_3 & sub_4      |

Exact geographic descriptions for each code must be confirmed from the Embrapa PDF during
Sub-Task 3. Update this table once extracted.

## Post-Dataset Pattern Analysis (Optional — Sub-Task 6)

Once `CULTIVARES` is fully populated, analyse the dataset to find structural patterns that
could simplify the oracle further. For example:
- Do all cultivars in macro-region 2 cover all 4 sub-regions? If so, sub-region becomes
  irrelevant for that macro and can be dropped from certain queries.
- Are any disease resistance attributes perfectly correlated across cultivars?
  If so, the two variables can be collapsed into one without information loss.

This analysis should be implemented as a standalone exploratory cell added after the full
dataset is confirmed. It does not change the data model — it informs future optimisations.
