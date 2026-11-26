"""Genera la cartella docs/ (sito pubblicabile) a partire da raw/ (copia scaricata da Webflow).

Uso una tantum, già eseguito. Da qui in poi si modifica direttamente docs/.
    python3 tools/build.py   (richiede: fonttools, brotli; cwebp; curl)
"""
import os, re, shutil, subprocess, sys, posixpath
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
RAW, SITE = ROOT / "raw", ROOT / "docs"
DOMAIN = "https://www.rutacamp.com"
EXCLUDE = ("work/",)  # pagine di esempio del template Webflow, non collegate da nessuna parte

if SITE.exists():
    shutil.rmtree(SITE)
shutil.copytree(RAW, SITE, ignore=lambda d, names: [n for n in names if n == ".DS_Store"])
for ex in EXCLUDE:
    shutil.rmtree(SITE / ex, ignore_errors=True)

pages = sorted(p for p in SITE.rglob("*.html"))

# ---------- Font: tutto in locale, in WOFF2, solo caratteri latini ----------
fonts = SITE / "assets/fonts"
LATIN = "U+0000-00FF,U+0131,U+0152-0153,U+02BB-02BC,U+02C6,U+02DA,U+02DC,U+0259,U+0300-0301,U+0304,U+0308,U+0329,U+1E00-1EFF,U+2000-206F,U+20AC,U+2122,U+2190-2199,U+2212,U+2215,U+FEFF,U+FFFD,U+0100-024F"
from fontTools import subset
for otf in list(fonts.glob("*.otf")):
    out = otf.with_suffix(".woff2")
    opts = subset.Options(); opts.flavor = "woff2"; opts.layout_features = ["*"]
    f = subset.load_font(str(otf), opts)
    s = subset.Subsetter(opts); s.populate(unicodes=subset.parse_unicodes(LATIN)); s.subset(f)
    subset.save_font(f, str(out), opts)
    otf.unlink()

css_path = next((SITE / "assets/css").glob("*.webflow.*.css"))
shutil.copy(ROOT / "tools/custom.css", SITE / "assets/css/custom.css")
css = css_path.read_text()
css = re.sub(r'url\((\.\./fonts/[^)]+)\.otf\)\s*format\(["\']opentype["\']\)', r'url(\1.woff2) format("woff2")', css)
css = re.sub(r'url\((\.\./fonts/[^)]+)\.otf\)', r'url(\1.woff2) format("woff2")', css)
css_path.write_text(css)

# Inter (prima caricato da Google Fonts): scaricato e servito in locale
UA = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0 Safari/537.36"
gcss = subprocess.run(["curl", "-s", "-A", UA, "https://fonts.googleapis.com/css2?family=Inter:wght@200;400;600;800&display=swap"],
                      capture_output=True, text=True, check=True).stdout
blocks = re.findall(r"/\* (latin-ext|latin) \*/\s*(@font-face \{.*?\})", gcss, re.S)
out_css, seen = [], {}
for subset_name, block in blocks:
    url = re.search(r"url\((https://[^)]+)\)", block).group(1)
    if url not in seen:
        name = f"inter-{subset_name}-{len(seen)}.woff2"
        subprocess.run(["curl", "-s", "-o", str(fonts / name), url], check=True)
        seen[url] = name
    out_css.append(block.replace(url, seen[url]))
(fonts / "inter.css").write_text("/* Inter, licenza SIL Open Font License */\n" + "\n".join(out_css) + "\n")

# ---------- Immagini: le più pesanti diventano WebP ----------
renamed = {}
for img in sorted((SITE / "assets/images").iterdir()):
    if img.suffix.lower() not in (".jpg", ".jpeg", ".png") or img.stat().st_size < 150_000:
        continue
    webp = img.with_suffix(".webp")
    w = int(re.search(r"pixelWidth: (\d+)", subprocess.run(["sips", "-g", "pixelWidth", str(img)], capture_output=True, text=True).stdout).group(1))
    args = ["cwebp", "-quiet", "-q", "80", "-metadata", "none"]
    if w > 2400:
        args += ["-resize", "2400", "0"]
    subprocess.run(args + [str(img), "-o", str(webp)], check=True)
    if webp.stat().st_size < img.stat().st_size:
        renamed[img.name] = webp.name
        img.unlink()
    else:
        webp.unlink()

# ---------- HTML ----------
HEAD_REMOVE = [
    r'<link href="https://cdn\.prod\.website-files\.com" rel="preconnect"[^>]*/>',
    r'<link href="https://fonts\.googleapis\.com" rel="preconnect"/>',
    r'<link href="https://fonts\.gstatic\.com" rel="preconnect"[^>]*/>',
    r'<script src="https://ajax\.googleapis\.com/ajax/libs/webfont/[^"]+" type="text/javascript"></script>',
    r'<script type="text/javascript">WebFont\.load\(\{.*?\}\);</script>',
    r'<meta content="Webflow" name="generator"/>',
    r'<!-- This site was created in Webflow\. https://webflow\.com -->',
    r'<!-- Last Published:[^>]*-->',
]
for page in pages:
    if not page.exists():
        continue
    rel = page.relative_to(SITE).as_posix()
    depth = "../" * rel.count("/")
    h = page.read_text()
    for pat in HEAD_REMOVE:
        h = re.sub(pat, "", h, flags=re.S)
    # link social del menu mobile: erano quelli di esempio del template Webflow
    h = h.replace('href="http://www.instagram.com/webflow"', 'href="https://www.instagram.com/ruta_camp/"')
    h = h.replace('<a href="http://www.dribbble.com/webflow" class="nav-link social w-inline-block"><div class="social-nav">Dribbble</div>',
                  '<a href="https://www.facebook.com/rutacampitaly" target="_blank" class="nav-link social w-inline-block"><div class="social-nav">Facebook</div>')
    h = h.replace('<a href="http://www.behance.net" target="_blank" class="nav-link social w-inline-block"><div class="social-nav">Behance</div>',
                  '<a href="https://vimeo.com/user188396094" target="_blank" class="nav-link social w-inline-block"><div class="social-nav">Vimeo</div>')
    # video: da Embedly (chiave legata a Webflow) al player Vimeo diretto
    h = re.sub(r'<iframe class="embedly-embed" src="//cdn\.embedly\.com/widgets/media\.html\?src=https%3A%2F%2Fplayer\.vimeo\.com%2Fvideo%2F(\d+)%3Fh%3D([0-9a-f]+)[^"]*"[^>]*></iframe>',
               r'<iframe src="https://player.vimeo.com/video/\1?h=\2&amp;dnt=1" width="1920" height="1080" title="Video Vimeo" frameborder="0" loading="lazy" allow="autoplay; fullscreen; picture-in-picture" allowfullscreen></iframe>', h)
    for old, new in renamed.items():
        h = h.replace("/" + old, "/" + new)
    # jQuery locale: l'attributo crossorigin non serve
    h = h.replace(' crossorigin="anonymous"></script>', "></script>")
    # og:image / twitter:image devono essere indirizzi assoluti
    h = re.sub(r'(<meta content=")(?:\.\./)*(assets/images/[^"]+)(" (?:property|name)="(?:og|twitter):image")', rf'\1{DOMAIN}/\2\3', h)
    # URL canonico
    url_path = "/" + re.sub(r"(^|/)index\.html$", r"\1", rel)
    if rel != "404.html":
        h = h.replace("</title>", f'</title><link rel="canonical" href="{DOMAIN}{url_path.rstrip("/") or "/"}"/>', 1)
    h = h.replace('rel="stylesheet" type="text/css"/>',
                  f'rel="stylesheet" type="text/css"/><link href="{depth}assets/fonts/inter.css" rel="stylesheet"/>'
                  f'<link href="{depth}assets/css/custom.css?v=2" rel="stylesheet"/>', 1)
    page.write_text(h)

# ---------- Elimina i file che nessuna pagina usa più ----------
used = "".join(p.read_text() for p in SITE.rglob("*.html")) + "".join(p.read_text() for p in SITE.rglob("*.css")) \
     + "".join(p.read_text() for p in SITE.rglob("*.js"))
for f in list((SITE / "assets/images").iterdir()):
    if f.name not in used:
        f.unlink()

# ---------- File per la pubblicazione ----------
# CNAME: lo crea GitHub quando si imposta il dominio in Settings → Pages
(SITE / ".nojekyll").write_text("")
(SITE / "robots.txt").write_text(f"User-agent: *\nAllow: /\n\nSitemap: {DOMAIN}/sitemap.xml\n")
urls = []
for p in sorted(SITE.rglob("index.html")):
    r = p.relative_to(SITE).as_posix()[: -len("index.html")]
    urls.append(f"  <url><loc>{DOMAIN}/{r.rstrip('/')}</loc></url>".replace(f"{DOMAIN}/<", f"{DOMAIN}<"))
(SITE / "sitemap.xml").write_text('<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n' + "\n".join(urls) + "\n</urlset>\n")
print("ok:", len(list(SITE.rglob("*.html"))), "pagine,", len(renamed), "immagini convertite in WebP")
