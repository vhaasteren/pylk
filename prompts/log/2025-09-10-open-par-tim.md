You are the Pylk project planner and implementer.

## Goal

“Open PAR+TIM → show pre-fit residuals (read-only)”, includes:

* `PulsarModel` (loads par+tim via PINT, computes pre-fit residuals).
* `ProjectController` (opens/closes project).
* `PlkView` (Matplotlib in Qt; shows residuals vs MJD with error bars).
* `MainWindow` wiring (swap placeholder → PlkView when PAR+TIM loaded).
* Basic tests and integration with our quality gates.

## Inputs (already prepared)

* I ran:
  `make rag-dump QUERY="PINT residuals calculation" OUT=.cursor/rag_context.md`
  `make ai-plan GOAL="Add pre-fit residuals plot from PAR+TIM" AI_OUT=.cursor/cursor_context.md`
* You can rely on both files inside `.cursor/`.

## Workflow rules (from `development-workflow.md`)

* **Do not** run shell/git commands or auto-stage/commit. You propose **direct code edits**; I accept/reject in the UI. Make sure to run the pre-commits that do linting formattting.
* Work in **milestones**, one at a time. After each milestone, **STOP** and tell me to run `make fast`.
* Keep edits **small (< \~300 LOC per milestone)**.
* When logic changes, include tests (unit for models/controllers; `pytest-qt` for widgets).
* **No PINT calls in widgets** — only in models/controllers.
* Style: Black (100 cols), Ruff import sort, type hints, clear docstrings.

## Global constraints

* Use `qtpy` signals/slots.
* Pre-fit residuals for plotting: use **time residuals in microseconds**; signals should emit plain arrays/floats (no Astropy Quantities).
* No long-running tasks or threads yet.
* Tests: if PINT not importable, mark with **xfail(reason=...)** (do not silently skip).

---

## Milestone roadmap (4 slices)

### Milestone 1 — Model & Project controller (no UI yet)

**Scope**

* `pylk/models/pulsar.py`: `PulsarModel(QObject)` with signals:

  * `modelChanged`, `toasChanged`, `residualsChanged: dict`
* Methods:

  * `load(par_path: str, tim_path: str, fitter: str = "auto", ephem: str | None = None) -> None`
    (Use simple, robust PINT flow; e.g., `get_model_and_toas` or `get_model` + `toa.get_TOAs`.)
  * `compute_prefit_residuals() -> dict`  → keys: `mjd: np.ndarray`, `res: np.ndarray` (µs), `err: np.ndarray` (µs), `rms_us: float`, `n: int`
  * lightweight digests: `hash_model_params()`, `hash_toas()`, `hash_residuals()`
* `pylk/controllers/project.py`: `ProjectController(QObject)`:

  * signals: `projectLoaded(PulsarModel)`, `projectClosed()`
  * methods: `open_project(par_path, tim_path, fitter="auto", ephem=None) -> PulsarModel`, `close_project() -> None`
* Tests:

  * `tests/test_pulsar_model_unit.py`: asserts returned dict has expected keys, lengths, and numeric types; mark **xfail** if PINT missing.
  * Ensure `tests/test_boot.py` (or add) still passes (smoke imports).

**Out of scope**: UI edits; no changes to `main_window.py`.

### Milestone 2 — PlkView (plotting widget)

**Scope**

* `pylk/widgets/plk_view.py`: `PlkView(QWidget)` with an embedded `FigureCanvasQTAgg`.
* Public API:

  * `set_model(PulsarModel)` to connect to `residualsChanged(dict)`.
  * slot `on_residuals_changed(payload: dict)` → errorbar plot (x = MJD, y = residual \[µs]), labels, grid, `tight_layout`.
  * action “Save Plot…” (write PNG via file dialog).
* Tests:

  * `tests/test_plk_view_qt.py`: `pytest-qt` smoke test that instantiates the widget and calls `on_residuals_changed` with a tiny synthetic payload (no PINT needed).

**Out of scope**: hooking into `MainWindow`.

### Milestone 3 — Wire into MainWindow

**Scope**

* Edit `pylk/main_window.py`:

  * Instantiate `ProjectController`.
  * When both PAR & TIM chosen (`_maybe_enable_project()`), call `open_project(...)`.
  * Create one `PlkView`, call `set_model(model)` upon `projectLoaded`.
  * Swap central placeholder → `PlkView`.
  * Status bar: show “TOAs: N | RMS: X µs” on `residualsChanged`.
  * “Close Project” restores placeholder, calls `close_project()`.
* Tests:

  * `tests/test_main_window_integration.py`: `pytest-qt` verifies that emitting `projectLoaded(model)` swaps the central widget to `PlkView`.

### Milestone 4 — Polish & UX

**Scope**

* Improve status text: “Loaded PAR: … | TIM: … | TOAs: N | RMS: X µs”.
* Guard against missing keys in payload gracefully.
* Ensure “Save Plot…” is reachable (widget button or menu injection).
* Update `CHANGELOG.md` (**Unreleased → Added**) with a bullet for this feature.

---

## How to respond each time

* Start with a **Short plan** (6–10 bullets tailored to the milestone).
* Then apply **direct code edits for the current milestone only**.
* End with this exact line (verbatim):

```
=== PAUSE: Run `make fast` now. I will wait for your signal to proceed to the next milestone. ===
```

---

## First run now: Milestone 1 only

Produce:

1. Short plan for Milestone 1.
2. Direct file edits for:

   * `pylk/models/pulsar.py` (new file)
   * `pylk/controllers/project.py` (new file)
   * `tests/test_pulsar_model_unit.py` (new or updated)
   * `tests/test_boot.py` (ensure smoke import remains green; create if missing)
3. Stop with the PAUSE line above.

Remember:

* No UI edits yet.
* Signals: `modelChanged`, `toasChanged`, `residualsChanged(dict)`.
* Residuals in microseconds (floats); payload is plain numpy arrays and floats/ints.
* If PINT is not importable in the environment, tests must be `xfail(reason="PINT not available")`.

Only deliver **Milestone 1** now.

