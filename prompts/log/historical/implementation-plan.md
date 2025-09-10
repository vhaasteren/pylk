# Design addendum for an embedded IPython kernel

## Key idea

* Keep a **single source of truth** for PINT state in `PulsarModel` (wrapping PINT’s `pintk`-style `Pulsar` behavior).
* All mutating pathways (GUI actions, controllers, *and* kernel code) ultimately go through **controllers** that:

  1. validate / normalize the change,
  2. apply it to `PulsarModel`,
  3. emit **signals** so views/widgets update.

## New components

* **KernelController**

  * Starts/stops an IPython kernel (e.g., via `qtconsole` or `jupyter_client`).
  * Injects a **Pylk namespace**: `toas`, `model`, `pulsar` (`PulsarModel`), maybe helpers like `fit()`, `update_resids()`.
  * Listens for **execution finished** events; on completion, computes content hashes (see below) and, if changed, emits `modelChanged`, `toasChanged`, etc.
* **ObjectRegistry** (very small)

  * Holds references to the **live** `PulsarModel`, `ParController`, `TimController`, `FitController`.
  * Used by `KernelController` to (re)expose the *current* live objects after file open / project switch.

## Hash-based refresh (optional but recommended)

* Maintain cheap content hashes in `PulsarModel`:

  * `hash_model_params()` — hash parameter names, values, frozen flags.
  * `hash_toas()` — hash `toas.table` columns (`index`, `mjd`, `freq`, `flags`, etc.).
  * `hash_residuals()` — hash residual arrays (prefit/postfit) or a small digest (size, sum, mean, std).
* `KernelController` records pre-exec snapshot and compares post-exec; if any differs, it raises corresponding signals.
* Views subscribe and refresh only when relevant signals fire.

This keeps the kernel and GUI in sync but avoids redundant redraws.

---

# Updated module map (compatible with your plan)

```
pylk/
  app.py
  main_window.py
  controllers/
    project.py      # ProjectController
    par.py          # ParController
    tim.py          # TimController
    fit.py          # FitController
    kernel.py       # KernelController  <-- NEW
  models/
    pulsar.py       # PulsarModel (wraps PINT interactions)
  widgets/
    plk_view.py     # residuals/plot view (Qt + Matplotlib)
    par_editor.py   # par editor (Qt)
    tim_editor.py   # tim editor (Qt)
    console.py      # IPython/QtConsole widget  <-- NEW
    common.py
  utils/
    settings.py
    logging.py
    io.py
  services/
    registry.py     # ObjectRegistry  <-- NEW (tiny)
    events.py       # common Qt signals (optional) 
```

---

# UML sketch (ASCII)

```
+------------------+              +---------------------+
|   MainWindow     |<>----------->|  ProjectController  |
|  (QMainWindow)   |              +----------+----------+
| - menus/docks    |                          |
| - sets widgets   |                          |
+---------+--------+                          |
          |                                   |
          | holds refs                        v
          |                         +---------------------+
          |                         |     PulsarModel     |
          |                         |  (wraps PINT state) |
          |                         +---------------------+
          |                                   ^
          |                                   |
          |          +------------------------+---------------------------+
          |          |                        |                           |
          v          v                        v                           v
+---------+--------+ +---------------------+  +---------------------+  +-------------------+
|  ParController  | |    TimController     |  |    FitController    |  | KernelController |
+---------+--------+ +----------+----------+  +----------+----------+  +---------+--------+
          |                      |                       |                       |
          v                      v                       v                       |
+---------+--------+  +----------+-----------+  +--------+-----------+           |
|  ParWidget       |  |   TimWidget         |  |   PlkView          |           |
| (QTextEdit etc.) |  | (QTextEdit etc.)    |  | (Matplotlib canvas)|           |
+------------------+  +---------------------+  +--------------------+           |
                                                                                |
                                                          +---------------------+-----------+
                                                          |     ObjectRegistry (service)     |
                                                          |  exposes live model/controllers  |
                                                          +----------------------------------+
```

**Signals (examples)**

* `ProjectController`: `projectLoaded`, `projectClosed`
* `PulsarModel`: `modelChanged`, `toasChanged`, `residualsChanged`, `fitted`
* `ParController`/`TimController`/`FitController`: forward or specialize model signals
* `KernelController`: `kernelExecutionFinished(changes: set[str])`, and re-emits `modelChanged`/`toasChanged` after hash diff

---

# Detailed design spec

## 1) `PulsarModel` (models/pulsar.py)

* **Purpose:** canonical owner of PINT state: `prefit_model`, `postfit_model`, `all_toas`, `selected_toas`, residuals, fitter, etc.
* **API (mirrors pintk, see your context):**

  * Loading/resetting: `reset_model()`, `reset_TOAs()`, `resetAll()`
  * Accessors: `name`, `year()`, `dayofyear()`, `orbitalphase()`, etc.
  * Fitting: `fit(selected, iters=4, compute_random=False)`, `getDefaultFitter()`, random models workflow, `write_fit_summary()`
  * Editing: `add_model_params()`, `add_jump()`, `add_phase_wrap()`, `delete_TOAs()`
  * Residuals: `update_resids()`, `print_chi2(selected)`
  * **Hashers:** `hash_model_params()`, `hash_toas()`, `hash_residuals()`
* **Signals** (Qt signals or a small event bus):

  * `modelChanged`, `toasChanged`, `residualsChanged`, `fitted`, `jumpsChanged`
* **Notes from pintk RAG:** All the methods above are lifted/adapted from `pintk/pulsar.py` and used by widgets like Plk/Par/Tim in pintk.

## 2) Controllers

* **ProjectController**

  * Open/close project: loads `.par`/`.tim` into `PulsarModel`.
  * Rewires `ObjectRegistry` so kernel + widgets see the current model.
  * Emits `projectLoaded(model)`, `projectClosed()`.
* **ParController**

  * Methods: `apply_changes(text)`, `reset()`, `center_pepoch()`, `center_posepoch()`, `center_T0()`, `write_par(path)`.
  * Internally: uses PINT APIs (`pint.models.get_model(io)`), and if fitted state exists, keeps postfit consistent (as in `paredit.py`).
  * Emits/forwards `modelChanged`.
* **TimController**

  * Methods: `apply_changes(text)`, `reset()`, `write_tim(path)`, `set_toas_from_text(text)` (uses `pint.toa.get_TOAs(io)`), preserving flags (like in `timedit.py`).
  * Emits/forwards `toasChanged`.
* **FitController**

  * Methods: `fit(selected, iters)`, `random_models(selected)`, `print_chi2(selected)`.
  * Emits `fitted`, `residualsChanged`.
* **KernelController**

  * Starts a Qt-friendly IPython kernel (`qtconsole` or `jupyter_client` + custom console widget):

    * On kernel start or project switch, inject into user namespace:

      * `pulsar` → `PulsarModel`
      * `model` → `pulsar.prefit_model` (or a property that flips to postfit when `fitted`)
      * `toas` → `pulsar.all_toas` (and maybe `selected_toas`)
      * convenience funcs: `fit = controllers.fit.fit`, `update_resids = pulsar.update_resids`, `add_jump`, `delete_toas`, etc.
  * On **execution request**:

    * Take snapshots: `h_model0`, `h_toas0`, `h_res0`.
    * Run code.
    * Take snapshots again; compute `delta = {…}`.
    * For each changed facet, **emit** the corresponding signal(s).
  * Provides a small **policy hook** to coerce mutation through controllers (optional). In practice, users will call PINT APIs directly; hash diffing keeps GUI consistent.

## 3) Widgets

* **PlkView** (matplotlib in Qt):

  * Subscribes to `residualsChanged`, `modelChanged`, `toasChanged`.
  * Offers selection tools; emits `selectionChanged(mask)` to `FitController`.
  * Re-implements the pintk keyboard/mouse affordances over time.
* **ParWidget** / **TimWidget** (Qt equivalents of `paredit.py`/`timedit.py`):

  * Display/edit text and wire buttons:

    * `Apply Changes` → `ParController.apply_changes(text)` (or Tim)
    * `Reset` → controller.reset()
    * `Write` → controller.write\_par/write\_tim()
    * `Center PEPOCH/POSEPOCH/T0` → controller call
* **ConsoleWidget**:

  * A QtConsole or embedded terminal-like widget attached to `KernelController`.
  * Shows rich outputs; raises `executionFinished` events that the controller already listens for.

## 4) Events & updates (end-to-end)

* **GUI action (e.g., “Fit”)**:

  * PlkView emits `fitRequested(selected)`.
  * FitController calls `PulsarModel.fit(selected)`.
  * Model emits `fitted` + `residualsChanged`; PlkView redraws.
* **Kernel action**:

  * User does `model.F0.value *= 1.001` or `pulsar.add_jump(mask)`.
  * KernelController detects hash changes post-exec → emits `modelChanged` or `toasChanged`.
  * Controllers/views refresh.

## 5) Threading & safety

* Keep kernel and GUI in the **same process**; `qtconsole` already integrates with Qt event loop.
* Ensure any heavy recomputation (long fits) stays responsive:

  * Option A (simple initial): run on main thread; UI stays OK for short fits.
  * Option B (later): move `FitController.fit()` into a worker `QThread` and forward signals safely.

## 6) Logging

* Pipe `loguru`/PINT logs to a `QPlainTextEdit` dock via a custom handler; also mirror to stderr for dev convenience.

---

# Step-by-step implementation guide (Cursor-friendly)

**Phase 1 — Scaffolding controllers/models**

1. **Create `models/pulsar.py`**

   * Port the core of `pintk/pulsar.py` (from your snippets) into `PulsarModel`.
   * Keep the same methods (`reset_model`, `reset_TOAs`, `update_resids`, `fit`, `add_jump`, `delete_TOAs`, `add_phase_wrap`, `write_fit_summary`, `random_models`, etc.).
   * Add **hashers**:

     ```python
     def hash_model_params(self): ...
     def hash_toas(self): ...
     def hash_residuals(self): ...
     ```
   * Add Qt signals (or a small pub-sub) and emit them in appropriate spots (`update_resids`, `fit`, etc.).

2. **Create `controllers/project.py` (ProjectController)**

   * Methods: `open_project(par_path, tim_path, fitter='GLSFitter', ephem=None)`, `close_project()`.
   * Instantiate `PulsarModel` and wire signals to the main window.
   * Update `ObjectRegistry` with the new objects.

3. **Create `services/registry.py` (ObjectRegistry)**

   * Simple class with setters/getters for `pulsar_model`, `par_controller`, `tim_controller`, `fit_controller`.
   * `KernelController` will pull from here when injecting objects.

4. **Create `controllers/par.py`, `controllers/tim.py`, `controllers/fit.py`**

   * Port logic from `paredit.py` and `timedit.py` to *controllers*, calling `PulsarModel` and emitting/forwarding signals (e.g. `modelChanged`, `toasChanged`).
   * `FitController.fit()` calls `pulsar_model.fit()` and forwards `fitted` + `residualsChanged`.

**Phase 2 — Widgets**
5\. **Create `widgets/par_editor.py` & `widgets/tim_editor.py`**

* Use `QTextEdit` + buttons mirroring pintk actions (Apply/Reset/Write/Center\*).
* Connect buttons to the corresponding controller methods.
* Provide methods `set_text_from_model()` and update on `modelChanged`/`toasChanged`.

6. **Create `widgets/plk_view.py`**

   * Embed Matplotlib via `FigureCanvasQTAgg`.
   * Subscribe to `residualsChanged`, `modelChanged`, `toasChanged`.
   * Implement initial scatter/errorbar of residuals; add keyboard shortcuts incrementally (see your `plk.py` for reference).

**Phase 3 — Kernel integration**
7\. **Create `widgets/console.py`**

* Use `qtconsole.rich_jupyter_widget.RichJupyterWidget` (or classic) if available in your container, or fall back to a simple text console + `jupyter_client` for execution.

8. **Create `controllers/kernel.py` (KernelController)**

   * Start IPython kernel via `jupyter_client.KernelManager` (or `qtconsole.manager.QtKernelManager`).
   * On (re)attach or project change, **inject**:

     ```python
     ns = {
       "pulsar": registry.pulsar_model,
       "model": registry.pulsar_model.prefit_model,  # or a property
       "toas": registry.pulsar_model.all_toas,
       "fit": controllers.fit.fit,  # convenience
       "update_resids": registry.pulsar_model.update_resids,
       "add_jump": registry.pulsar_model.add_jump,
       # etc.
     }
     ```

     Use `%who` to verify in the console.
   * Before execution: record `h0 = (model, toas, resids)` hashes; after: rehash and **emit** model/toas/residuals change signals if needed.

**Phase 4 — Wire it all in `MainWindow`**
9\. Instantiate controllers and widgets, place widgets into docks/tabs.
10\. Connect menu items (`Open PAR/TIM`, `Close Project`) to `ProjectController`.
11\. After opening a project, call `ObjectRegistry.set_pulsar_model(model)` and have `KernelController.reinject_namespace()`.

**Phase 5 — Parity with pintk workflows**
12\. Bring over remaining pintk interactions into PlkView (selection, jumps, keybindings) and confirm the following *RAG-aligned* flows work:

* `PlkWidget.setPulsar(self.psr, updates=[...])` → we replace this with controller signals: when `ProjectController` loads a `PulsarModel`, we connect its signals to PlkView to refresh (equivalent effect).
* `ParWidget.setPulsar(psr, updates)` and `TimWidget.setPulsar(psr, updates)` → replaced with controllers wiring and `modelChanged`/`toasChanged` emissions.
* `pint.logging.setup` → map logs into a dock (optional now, easy to add later).

**Phase 6 — Testing**
13\. Manual tests:

* Load `.par` + `.tim`.
* Edit par in GUI → Apply → plot updates.
* Edit tim in GUI → Apply → plot updates.
* In console, mutate `model.F0.value`, call `fit()`, add/remove jumps → plots update after execution finishes.

---

# Notes mapping to your RAG context

* In pintk, the **main Tk class** (`PINTk`) directly wires widgets with a shared `Pulsar` object and uses callbacks like `setPulsar`, `update()` \[RAG 13–20].
  **In Pylk**, `ProjectController` + signals replace that manual wiring; widgets subscribe to updates (`modelChanged`, `toasChanged`, etc.).

* pintk **ParWidget/TimWidget** directly read/write text to/from PINT models/TOAs (`pint.models.get_model`, `pint.toa.get_TOAs`) \[paredit.py, timedit.py].
  **In Pylk**, the logic to parse/apply/save lives in `ParController`/`TimController`, keeping widgets thin.

* pintk’s **Pulsar class** handles fitting, residuals, random models, jumps (your long `pulsar.py` excerpts), and is the locus for PINT interaction.
  **In Pylk**, `PulsarModel` keeps exactly that role but is **UI-free** and emits signals. Controllers orchestrate its use.

* Command-line interface and logging in pintk can be added later; the new architecture doesn’t block them.

