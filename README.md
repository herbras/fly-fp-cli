# fly-fp-cli

Allowlisted Founder+ CLI (`fp …`) plus a pointer to a **non-crypto** embodied fly.

The fly does **not** run:

```sh
curl -fsSL https://academy.founderplus.id/install.sh | sh
```

That stays on the host, once.

## Otak yang dipakai (bukan token)

[DenisSergeevitch/desktop-fly](https://github.com/DenisSergeevitch/desktop-fly) — FlyWire + ekstrak kaki MaleCNS, app desktop, kode ada, bukan coin.

```sh
python -m fly_fp.cli desktop-fly
git clone https://github.com/DenisSergeevitch/desktop-fly.git ~/src/desktop-fly
cd ~/src/desktop-fly && ./build.sh && ./DesktopFly   # macOS 13+
```

Detail: [docs/DESKTOP_FLY.md](docs/DESKTOP_FLY.md)

NeuroCraft Fly belum rilis kode. fly.ai / ticker diabaikan.

## CLI Founder+ (repo ini)

```sh
git clone https://github.com/herbras/fly-fp-cli.git
cd fly-fp-cli && pip install -e ".[dev]" && pytest
python -m fly_fp.cli type --action skills_list --delay 0.03
python -m fly_fp.cli demo
```

`--brain stub` = 64 LIF mainan untuk tes pipeline. Bukan connectome.

MIT. Data FlyWire / MaleCNS tetap lisensi hulu (CC BY). Bukan afiliasi Founder+, Janelia, Mojang, atau DesktopFly.
