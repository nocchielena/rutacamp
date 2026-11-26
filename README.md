# rutacamp.com

Versione indipendente del sito di **Ruta – Summer Film School**, copiata dal sito Webflow originale.
È un sito **statico** (solo HTML, CSS, JavaScript e immagini): non dipende da Webflow né da altri
servizi a pagamento e si pubblica gratis con GitHub Pages (dalla cartella `docs/` del ramo `main`).

## Struttura

```
docs/      ← IL SITO. È questa la cartella che viene pubblicata e che si modifica.
  index.html                 home
  about/cose-ruta/           Cos'è Ruta
  edizioni/                  elenco edizioni + edizione-2021/2022/2023
  team/                      schede tutor
  404.html                   pagina "non trovata"
  assets/css/                stile originale di Webflow + custom.css (correzioni nostre)
  assets/images/, fonts/, js/
  (CNAME)                    va aggiunto al passaggio del dominio, vedi sotto
raw/       ← archivio: copia esatta scaricata da Webflow (immagini originali in alta risoluzione)
tools/     ← script usati una volta per creare docs/ da raw/
```

## Modificare un testo

1. Aprire su GitHub il file della pagina, ad esempio `docs/index.html`.
2. Premere la matita ✏️ (“Edit this file”), cercare il testo con Ctrl/Cmd+F e cambiarlo.
3. Premere **Commit changes**. Dopo 1–2 minuti il sito online è aggiornato.

Attenzione a non cancellare i segni `<` `>` intorno al testo.

## Cambiare un'immagine

Caricare la nuova immagine in `docs/assets/images/` (“Add file → Upload files”), poi nella pagina
sostituire il nome del vecchio file con quello nuovo, sia in `src="…"` sia in `srcset="…"`
(il modo più semplice: cancellare tutto l'attributo `srcset="…"` e `sizes="…"` di quell'immagine).
Meglio usare immagini larghe al massimo 2000 px, in formato `.webp` o `.jpg`.

## Anteprima sul computer

```bash
cd docs && python3 -m http.server 8080
```
poi aprire http://localhost:8080

## Differenze rispetto all'originale su Webflow

- Font (Pretendard, Rondal, Inter) ospitati nel sito e compressi: da 14 MB a 0,6 MB.
- Immagini più pesanti convertite in WebP: il sito passa da circa 107 MB a 20 MB.
- **Telefono e tablet**: il titolo della home e il pulsante non escono più dallo schermo (vedi `docs/assets/css/custom.css`).
- Nel menu da telefono i link social erano quelli di esempio di Webflow (Dribbble, Behance):
  ora puntano a Instagram, Facebook e Vimeo di Ruta.
- I video Vimeo sono incorporati direttamente, senza passare da Embedly/Webflow.
- Tolte le pagine di esempio del modello Webflow (`/work/…`, `/template/…`), non collegate da nessuna parte.
- Aggiunti `sitemap.xml`, `robots.txt` e indirizzi canonici per Google.

## Collegare il dominio www.rutacamp.com

1. Su GitHub: **Settings → Pages → Custom domain**, scrivere `www.rutacamp.com` e salvare
   (GitHub crea da solo il file `docs/CNAME`).
2. Il dominio è su **Aruba** (scadenza 2 marzo 2027). Da *Pannello Aruba → Gestione DNS* di rutacamp.com:
   - record **CNAME** `www` → `nocchielena.github.io`
   - record **A** per `@` (dominio senza www) → `185.199.108.153`, `185.199.109.153`, `185.199.110.153`, `185.199.111.153`
   - togliere i vecchi record di Webflow: CNAME `www` → `cdn.webflow.com` e A `@` → `198.202.211.1`.
   - **NON toccare i record MX** (`mx.rutacamp.com`): servono alla posta di info@rutacamp.com.
3. Quando su Settings → Pages compare il segno verde, spuntare **Enforce HTTPS**.
4. Solo dopo aver controllato che www.rutacamp.com mostri il nuovo sito, disdire l'abbonamento Webflow.
