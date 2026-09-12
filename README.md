# fly-fp-cli

A **frozen fruit-fly reservoir** that is only allowed to pick Founder+ CLI commands.

The fly does **not** run:

```sh
curl -fsSL https://academy.founderplus.id/install.sh | sh
```

That one-liner stays on **your** machine, once. After `fp` is on `PATH`, this repo maps terminal text → sensory channels → spikes → an allowlisted `fp …` argv.

```
terminal stdout/stderr/exit
        |
        v
encoder  (sweet / bitter / looming / target / hunger / satiety)
        |
        v
reservoir  (64 LIF stub, or MaleCNS via fly.ai)
        |
        v
linear readout  (the only trained piece)
        |
        v
Action enum  →  SafeExecutor  →  fp skills list | fp guidance | …
```

Wiring inside the brain never changes. `curl`, `| sh`, `sudo`, `rm` are rejected even if the readout hallucinates them — the fly never emits a raw shell string.

## Install this repo

```sh
git clone https://github.com/herbras/fly-fp-cli.git
cd fly-fp-cli
python -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
pytest
```

## Install Founder+ CLI on the host (not inside the fly)

macOS / Linux:

```sh
curl -fsSL https://academy.founderplus.id/install.sh | sh
fp --help
```

Windows PowerShell:

```powershell
irm https://academy.founderplus.id/install.ps1 | iex
```

Docs: [Founder+ CLI & Funnel Toolkit](https://cdn.founderplus.id/)

## Run

```sh
python -m fly_fp.cli actions
python -m fly_fp.cli demo
python -m fly_fp.cli once --stdout "Usage: fp skills guidance" --goal skill
python -m fly_fp.cli demo --live
python examples/dry_run.py
```

## What the fly is allowed to type

| Action | Command |
|---|---|
| idle | — |
| help | `fp --help` |
| skills_list | `fp skills list` |
| skills_search | `fp skills search marketing` |
| skills_install_mulai_jualan | `fp skills install mulai-jualan` |
| guidance | `fp guidance` |
| guidance_tutorials | `fp guidance tutorials` |
| catalog | `fp catalog` |
| products_list | `fp products list` |
| new_list | `fp new --list` |

Add a command by editing `fly_fp/allowlist.py` and adding a labeled row in `fly_fp/curriculum.py`. If it is not in that table, it does not run.

## Optional: real MaleCNS (fly.ai)

Default brain is a 64-unit LIF stub so `pytest` and `demo` work on a laptop with no 1.1 GB download.

```sh
git clone https://github.com/alextitonis/fly.ai
cd fly.ai
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
python build_brain.py
export PYTHONPATH="$PWD:$PYTHONPATH"
```

Then:

```sh
python -m fly_fp.cli --brain flyai demo
```

`FlyAiAdapter` injects sweet/bitter/loom/target channels into named cell types (`Gr64f`, `LPLC2`, `LC10a`) and reads descending-neuron activity. Missing cell types are skipped. This is a demo coupling, not a claim that Drosophila understands `fp skills`.

MaleCNS v1.0 data is CC BY 4.0 (Janelia / Cambridge / Google). fly.ai code is MIT.

## Training

`FlyOperator.fit_from_curriculum()` fits a ridge readout on hand-labeled terminal snapshots. Looming text (`curl | sh`) forces `IDLE` before the readout. Swap the readout for RL later. Do not train by letting the fly pipe install scripts.

## Safety

- `subprocess.run(argv, shell=False)` only
- argv[0] must be `fp`
- output scanned for `curl`, `| sh`, `sudo`, `rm -`
- `--live` is opt-in; default is dry-run
- host install of `fp` is documented, never an Action

## License

MIT. Not affiliated with Founder+, HHMI Janelia, or Google.
Not a biological emulation. Point neurons, frozen weights, toy encoder.
