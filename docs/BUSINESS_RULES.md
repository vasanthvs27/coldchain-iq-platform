# Business Rules & Compliance Logic Specification

## 1. Core Business Rules (Rules 1 to 10)

The ColdChain IQ compliance engine enforces 10 deterministic business rules to evaluate pharmaceutical transit integrity. Every rule operates solely on source records.

---

### Rule 1: Product Temperature Requirements
- Each product must have an established lower temperature limit ($T_{\min}$) and upper temperature limit ($T_{\max}$).
- **Validation**: Enforce $T_{\min} < T_{\max}$. A configuration where $T_{\min} \ge T_{\max}$ is invalid and rejected at creation.
- Common pharmaceutical thermal envelopes:
  - Refrigerated (Cold Chain): $+2.0^\circ\text{C}$ to $+8.0^\circ\text{C}$
  - Controlled Room Temperature (CRT): $+15.0^\circ\text{C}$ to $+25.0^\circ\text{C}$
  - Frozen: $-25.0^\circ\text{C}$ to $-15.0^\circ\text{C}$
  - Ultra-Low (Cryogenic): $-80.0^\circ\text{C}$ to $-60.0^\circ\text{C}$

---

### Rule 2: Effective Threshold Policy
- When evaluating a shipment for product $P$ during transit interval $[t_{\text{start}}, t_{\text{end}}]$, the applicable threshold policy must:
  1. Belong explicitly to product $P$ (`policy.product_id == shipment.product_id`).
  2. Have an active effective status (`policy_status == 'ACTIVE'`).
  3. Cover the temporal window ($\text{effective\_from} \le t_{\text{start}}$ and ($\text{effective\_until}$ is null or $\ge t_{\text{end}}$)).
- Historical decisions preserve the exact `policy_version` (e.g. `v1.2`) in the compliance audit record.
- **Violation**: Applying a policy for product $A$ to a shipment carrying product $B$ triggers `POLICY_MISMATCH` and blocks compliance certification.

---

### Rule 3: Logger Assignment Verification
- A temperature reading $R$ recorded at timestamp $t_R$ by logger $L$ for shipment $S$ is trusted as valid shipment evidence **if and only if**:
  1. Logger $L$ exists in master data.
  2. A valid assignment record exists in `shipment_logger_assignments` linking $L$ to $S$.
  3. The reading timestamp falls strictly within the assignment window:
     $$\text{assigned\_at} \le t_R \le \text{unassigned\_at (or transit end)}$$
- Readings recorded outside this window or from an unassigned logger are flagged `reading_status = 'UNASSIGNED_LOGGER'`, quarantined from trusted evidence, and prevent automatic compliance sign-off.

---

### Rule 4: Calibration & Uncertainty Separation
- Logger hardware must possess a valid NIST-traceable calibration certificate on the date of shipment:
  $$\text{calibration\_date} \le \text{shipment.actual\_departure} \le \text{calibration\_expiry}$$
- The platform maintains two distinct values for every temperature observation:
  1. `measured_temperature`: Raw reading emitted by the sensor probe.
  2. `corrected_temperature`: Temperature adjusted by certified offset:
     $$\text{corrected\_temperature} = \text{measured\_temperature} + \text{calibration\_offset}$$
- Certified `measurement_uncertainty` (e.g. $\pm 0.15^\circ\text{C}$) is never discarded and is evaluated during borderline excursion analyses.

---

### Rule 5: Temperature Excursion Calculation
- An observation is out-of-specification if:
  $$\text{corrected\_temperature} < T_{\min} \quad \text{OR} \quad \text{corrected\_temperature} > T_{\max}$$
- **Continuous Duration Calculation**:
  - Excursions are calculated using strictly chronologically ordered valid readings belonging to the **same shipment and logger assignment**.
  - Let readings $r_1, r_2, \dots, r_k$ be contiguous out-of-spec observations. The excursion duration is:
    $$\Delta t = t_k - t_1$$
  - Consecutive excursions separated by less than the configurable recovery threshold are grouped into a cumulative excursion dossier.

---

### Rule 6: Allowed Excursion Duration Disposition
- Every product has a defined cumulative allowable excursion duration $D_{\text{allowed}}$ (in minutes):
  - If cumulative excursion duration $\sum \Delta t \le D_{\text{allowed}}$, the thermal deviation is classified as an **Approved Minor Excursion** (Disposition: `RELEASE` with qualification).
  - If cumulative excursion duration $\sum \Delta t > D_{\text{allowed}}$, the shipment is classified as `NON_COMPLIANT` (Disposition: `QUARANTINE_LOT` or `SCRAP_LOT`).

---

### Rule 7: Missing Data Detection
- Telemetry loggers are programmed to transmit at an expected interval of $\tau = 10\text{ minutes}$.
- For consecutive valid readings $r_i$ and $r_{i+1}$ recorded at $t_i$ and $t_{i+1}$:
  - If $t_{i+1} - t_i > 15\text{ minutes}$ ($1.5 \times \tau$), a **Telemetry Gap** is flagged.
  - The number of missing readings in this gap is estimated as:
    $$N_{\text{missing}} = \left\lfloor \frac{t_{i+1} - t_i}{\tau} \right\rfloor - 1$$
- **Inconclusive Mandate**: If total missing readings exceed 10% of expected telemetry (or 3 consecutive missing intervals), the shipment **must never** result in `COMPLIANT`. The compliance engine returns `INCONCLUSIVE` due to insufficient evidence.

---

### Rule 8: Chain of Custody Integrity
- All custody events for a shipment must form a contiguous unbroken graph:
  1. The `new_custodian` of handoff $H_j$ must match the `previous_custodian` of subsequent handoff $H_{j+1}$.
  2. Timestamps must be strictly chronological: $t(H_j) < t(H_{j+1})$.
  3. All transfers must have `acknowledgement_status == 'ACKNOWLEDGED'`.
- An unmatched custodian or missing intermediate handoff triggers `CUSTODY_GAP`.

---

### Rule 9: Route Dwell Monitoring
- For every intermediate transit stop (e.g. airport tarmac, customs bonded warehouse):
  $$\text{dwell\_duration} = t_{\text{departure}} - t_{\text{arrival}}$$
- If $\text{dwell\_duration} > \text{max\_allowed\_dwell}$ (e.g. > 180 minutes on airport tarmac), an alert is logged, and temperature variance during the dwell window is subjected to elevated risk scoring.

---

### Rule 10: 12-Step Compliance Determination
The compliance engine follows a strict 12-step deterministic pipeline:
1. Validate shipment existence and completed transit timestamps.
2. Validate product and lot manufacturing/expiry release status.
3. Validate logger assignment window.
4. Validate effective threshold policy match.
5. Validate logger calibration certificate validity.
6. Evaluate all timestamped temperature readings.
7. Identify missing reading intervals.
8. Calculate continuous and cumulative excursion durations.
9. Audit route stop dwell times and transit delays.
10. Validate chain of custody handoffs and signatures.
11. Determine final compliance status:
    - **`COMPLIANT`**: Zero excursions exceeding threshold, valid calibration, unbroken custody, complete telemetry.
    - **`NON_COMPLIANT`**: One or more confirmed excursions exceeding allowed duration, or expired lot release.
    - **`INCONCLUSIVE`**: Insufficient telemetry (telemetry gaps > threshold) or missing custody verification without confirmed non-compliance.
    - **`UNDER_REVIEW`**: Transit still in progress or open QA investigation pending.
12. Generate traceable compliance certificate with reason codes and evidence references.

---

## 2. Five Mandatory Negative Scenarios

| Scenario | Code | Injected Condition | Operational Detection | Compliance Outcome |
| :--- | :--- | :--- | :--- | :--- |
| **Scenario 1** | `UNASSIGNED_LOGGER` | A temperature reading is ingested from a logger that has no valid assignment to the shipment at that timestamp. | `TemperatureService` audits assignment table; marks reading as `UNASSIGNED_LOGGER`. | Reading quarantined; shipment marked `INCONCLUSIVE` or `UNDER_REVIEW`. |
| **Scenario 2** | `POLICY_MISMATCH` | A threshold policy belonging to Product B is applied during the evaluation of Product A. | `ComplianceService` verifies `policy.product_id == shipment.product_id`. | Hard block on compliance evaluation; raises `POLICY_MISMATCH` exception. |
| **Scenario 3** | `MISSING_DATA` | Telemetry readings drop out for 60+ minutes during transit (6 consecutive intervals missed). | `TemperatureService.detect_gaps` compares expected vs. actual reading cadence. | Rejects false-positive `COMPLIANT` label; returns `INCONCLUSIVE` with code `INSUFFICIENT_TELEMETRY`. |
| **Scenario 4** | `CUSTODY_GAP` | Carrier A hands off to Warehouse B, but the next recorded handoff is Carrier C to Clinic D without Warehouse B record. | `CustodyService` detects broken custodian chain ($C_{\text{new}, 1} \ne C_{\text{prev}, 2}$). | Flags `CUSTODY_GAP`; decision downgraded to `INCONCLUSIVE` or `UNDER_REVIEW`. |
| **Scenario 5** | `CROSS_SHIPMENT_DURATION` | Two concurrent shipments have excursions in the same hour. System recalculates duration isolating shipment IDs. | `ExcursionService` strictly filters by `shipment_id` during duration aggregation. | Rejects cross-contamination; correctly computes each shipment's duration independently. |
