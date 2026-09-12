# fly-fp-cli

A **frozen fruit-fly reservoir** that is only allowed to pick Founder+ CLI commands.

The fly does **not** run:

```sh
curl -fsSL https://academy.founderplus.id/install.sh | sh
```

That one-liner stays on **your** machine, once. After `fp` is on `PATH`, this repo maps terminal text → sensory channels → spikes → an allowlisted `fp …` argv.

## Keyboard (lalat paham apa yang diketik)

Keyboard adalah *badan*, bukan huruf di dalam neuron:

1. tiap tombol punya koordinat tangan (kiri/kanan, baris atas/bawah)
2. buffer terminal di-parse jadi token (`fp`, `skills`, `list`)
3. token di-map ke arti Founder+ (`modul skill`, `pasang mulai-jualan`, …)
4. `curl | sh` menyalakan looming — Enter ditahan

```sh
python -m fly_fp.cli type --action skills_list --delay 0.05
python -m fly_fp.cli type --action guidance --clear
```

Cockpit: prompt, next key, arti token, spike bar, QWERTY.

## Install this repo

```sh
git clone https://github.com/herbras/fly-fp-cli.git
cd fly-fp-cli
python -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
pytest
python -m fly_fp.cli type --action skills_list --delay 0.03
```

## Install Founder+ CLI on the host (not inside the fly)

```sh
curl -fsSL https://academy.founderplus.id/install.sh | sh
fp --help
```

Docs: [Founder+ CLI & Funnel Toolkit](https://cdn.founderplus.id/)

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

## Optional: real MaleCNS (fly.ai)

```sh
python -m fly_fp.cli --brain flyai demo
```

Not a biological emulation. MIT. Not affiliated with Founder+, Janelia, or Google.
