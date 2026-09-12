# DesktopFly — otak yang kami pakai

Bukan fly.ai. Bukan token.

Upstream: https://github.com/DenisSergeevitch/desktop-fly

## Apa yang disimulasi

- Otak: FlyWire (betina, spike LIF)
- Kaki: ekstrak MaleCNS v1.0 ~1.045 neuron, 17.224 koneksi, 6 kaki
- Dunia: kursor / jendela Mac atau overlay Windows

Bukan 166.700 neuron MaleCNS utuh. Mapping sensor–motor dipilih manusia.

## Pasang

```sh
git clone https://github.com/DenisSergeevitch/desktop-fly.git ~/src/desktop-fly
cd ~/src/desktop-fly
./build.sh
./DesktopFly
```

Windows: `cd windows && npm install && npm start`

```sh
python -m fly_fp.cli desktop-fly
```

## Hubungan dengan fly-fp

Dua proses. DesktopFly = lalat 3D. fly-fp = ngetik `fp …` allowlist. Host = installer Founder+ sekali, manusia. Lalat tidak menjalankan `curl | sh`.
