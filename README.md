# fly-fp-cli

Allowlisted Founder+ CLI driven by either a **toy 64-unit LIF** (`--brain stub`) or the **real MaleCNS v1.0 connectome** (`--brain malecns`).

`stub` is **not** a fly brain. Say that out loud. The real wiring is 166,700 neurons / 25.6M synapses from Janelia + Cambridge + Google, simulated as LIF by [alextitonis/fly.ai](https://github.com/alextitonis/fly.ai).

## 1. Toy path (laptop, no download)

```sh
git clone https://github.com/herbras/fly-fp-cli.git
cd fly-fp-cli && pip install -e ".[dev]" && pytest
python -m fly_fp.cli type --action skills_list --delay 0.03
```

## 2. Real brain path

```sh
python -m fly_fp.cli brain              # ready? fly.ai importable?
python -m fly_fp.cli fetch-brain        # clone fly.ai + build_brain.py (~1.1 GB)
export PYTHONPATH=$HOME/src/fly.ai:$PYTHONPATH
export FLY_DATA=$HOME/fly-data
python -m fly_fp.cli --brain malecns brain
python -m fly_fp.cli --brain malecns type --action skills_list
```

`--brain malecns` without `~/fly-data/weights.npz` **exits**. It does not silently use the stub.

Sensor map into annotated cell types: `Gr64f` sweet, `Gr66a` bitter, `LPLC2` looming, `LC10a` target.
Readout from descending neurons: `DNa02`, `DNp01`, `DNg100`, `MDN`.

MaleCNS data CC BY 4.0. fly.ai MIT. This repo MIT. Not affiliated with Founder+ / Janelia / Google. Not a biological emulation.
