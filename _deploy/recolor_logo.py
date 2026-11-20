"""Mulesi logosunu oyunların renk skalasına boyar: python3 _deploy/recolor_logo.py
Kaynak assets/img/mulesi-logo.webp (turuncu). Doygun turuncu pikseller (güneş, ağaçlar, kenar ışıkları, GAMES, nokta)
parlaklıklarına göre oyunun renk geçişine eşlenir; katırın kahverengi tüyü, gözlük ve krem "mulesi" yazısı (düşük doygunluk) korunur.
Çıktı: <oyun>/img/mulesi-logo.webp (640x707, şeffaf)."""
import os
import numpy as np
from PIL import Image

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "assets/img/mulesi-logo.webp")

# parlaklık (0 koyu → 1 açık) → renk duraklari; oyunların sitedeki css renkleri
# GAMES satırı (y > 614) ve i'nin noktası ayrı, okunaklı vurgu rengiyle
ACCENT = {
    "dontdrop": [(0.0, "784205"), (0.45, "d68000"), (0.75, "ffc82e"), (1.0, "fff0a0")],
    "shoottocrush": [(0.0, "8a4a00"), (0.45, "f08a1c"), (0.75, "ffc21a"), (1.0, "ffe14d")],
    "threeforcefive": [(0.0, "0a101d"), (0.40, "fa1f7d"), (0.70, "fbe002"), (1.0, "fff7a8")],
}
PALETTES = {
    "dontdrop": [(0.0, "0b2a08"), (0.30, "1a5c05"), (0.52, "45a312"), (0.72, "7fd11f"), (0.86, "adf238"), (1.0, "ffe680")],
    "shoottocrush": [(0.0, "061646"), (0.30, "0e3d99"), (0.50, "1e5fd6"), (0.66, "2f6fe0"), (0.82, "ffc21a"), (1.0, "ffe14d")],
    "threeforcefive": [(0.0, "0a101d"), (0.28, "5a0d3c"), (0.48, "fa1f7d"), (0.64, "b04cff"), (0.80, "01dcfb"), (1.0, "fbe002")],
}


def hexrgb(h):
    return np.array([int(h[i:i + 2], 16) for i in (0, 2, 4)], float) / 255


def ramp(t, stops):
    xs = np.array([s[0] for s in stops])
    cs = np.stack([hexrgb(s[1]) for s in stops])
    return np.stack([np.interp(t, xs, cs[:, k]) for k in range(3)], -1)


def recolor(stops, accent):
    im = np.array(Image.open(SRC).convert("RGBA")).astype(float) / 255
    rgb, a = im[..., :3], im[..., 3:]
    mx, mn = rgb.max(-1), rgb.min(-1)
    sat = np.where(mx > 0, (mx - mn) / np.maximum(mx, 1e-6), 0)
    r, g, b = rgb[..., 0], rgb[..., 1], rgb[..., 2]
    d = np.maximum(mx - mn, 1e-6)
    hue = np.where(mx == r, ((g - b) / d) % 6, np.where(mx == g, (b - r) / d + 2, (r - g) / d + 4)) * 60
    # turuncu-sarı ton aralığı ve yeterli doygunluk; yumuşak geçiş, kenar kırpılmasın
    w = np.clip((sat - 0.5) / 0.2, 0, 1) * np.clip((62 - hue) / 8, 0, 1) * np.clip((hue + 2) / 4, 0, 1)
    lum = 0.2126 * r + 0.7152 * g + 0.0722 * b
    t = np.clip((lum - 0.03) / 0.80, 0, 1)
    target = ramp(t, stops)
    h, wd = lum.shape
    yy, xx = np.mgrid[0:h, 0:wd]
    # GAMES satırı ve "i" noktası (sağ alttaki daire)
    zone = ((yy > 614) | ((yy > 440) & (yy < 515) & (xx > 560))) & (lum > 0.22)   # koyu harf kenarları ana geçişte kalır
    target = np.where(zone[..., None], ramp(t, accent), target)
    out = rgb * (1 - w[..., None]) + target * w[..., None]
    return Image.fromarray((np.concatenate([out, a], -1) * 255 + 0.5).astype(np.uint8))


if __name__ == "__main__":
    for game, stops in PALETTES.items():
        path = os.path.join(ROOT, game, "img", "mulesi-logo.webp")
        recolor(stops, ACCENT[game]).save(path, "WEBP", quality=92, method=6)
        print(path)
