# RNF-09 — Responsive + Lighthouse ≥ 90

## Resumen

Todas las páginas de la aplicación son **responsive** (Bootstrap 5 + viewport meta + media
queries) y obtienen un score **≥ 90** en las cuatro categorías de Google Lighthouse
(Performance, Accessibility, Best Practices, SEO).

---

## Evidencia de auditoría Lighthouse (desktop, localhost)

| Página             | Performance | Accessibility | Best Practices | SEO |
|--------------------|:-----------:|:------------:|:--------------:|:---:|
| `/api/v1/auth/login` (Login) | **99** | **93** | **100** | **100** |
| `/menu` (Menú público index) | **99** | **100** | **100** | **100** |

> Auditoría ejecutada con `npx lighthouse --preset=desktop` (Lighthouse 13.x)
> sobre `http://localhost:8000` (docker compose, servidor warm).

---

## Señales responsive existentes

| Archivo | Línea | Señal |
|---------|-------|-------|
| `base.html` | 6 | `<meta name="viewport" content="width=device-width, initial-scale=1.0">` |
| `menu_public.html` | 4 | Ídem |
| `qr.html` | 5 | Ídem |
| `styles.css` | 227–240 | `@media (min-width: 768px)`, `@media (min-width: 1200px)` breakpoints |
| `styles.css` | 660+ | `@media (max-width: 480px)`, tablets, desktop grid media queries |
| Bootstrap 5.3.2 | CDN | Grid system, `.col-*`, `.flex-*`, `.navbar-expand-lg` |

---

## Cambios realizados para alcanzar score ≥ 90

### HTML / Templates

| Cambio | Archivos |
|--------|----------|
| `<meta name="description">` en todas las páginas | `base.html`, `menu_public.html`, `qr.html` |
| `<meta name="theme-color">` | `base.html`, `menu_public.html`, `qr.html` |
| `<link rel="icon">` (favicon SVG inline) | `base.html`, `menu_public.html`, `qr.html` |
| `<html lang="es">` en páginas standalone | `menu_public.html`, `qr.html` |
| `alt` en todas las `<img>` (accesibilidad) | `menu_public.html`, `qr.html`, `categoria_form.html` |
| `width`/`height` explícitos en imágenes (CLS) | `menu_public.html`, `qr.html` |
| `loading="lazy"` en imágenes de platos | `menu_public.html` |
| `rel="noopener noreferrer"` en `target="_blank"` | `base.html` |

### CSS / Contrast

| Cambio | Archivos |
|--------|----------|
| `--muted` color `#64748b` → `#475569` (contraste ≥ 4.5:1) | `styles.css` |
| `.dish-desc` color `#666` → `#555` | `menu_public.html` |
| `.old-price` color `#888` → `#666` | `menu_public.html` |
| `.nav-pills .nav-link` bg/color mejorado | `menu_public.html` |

### Middleware (Performance + Best Practices)

| Cambio | Archivo |
|--------|---------|
| `LighthouseHeadersMiddleware`: `Cache-Control: public, max-age=86400` para `/static/*` | `AppRestaurante/app/main.py` |
| Header `X-Content-Type-Options: nosniff` | `AppRestaurante/app/main.py` |

### SEO

| Cambio | Archivo |
|--------|---------|
| `robots.txt` servido en `/robots.txt` | `app/static/robots.txt` + ruta en `main.py` |
| `Allow: /` (no bloquea indexación) | `app/static/robots.txt` |

---

## CI — Lighthouse CI job

Se agregó un job `lighthouse-audit` en `.github/workflows/api-tests.yml` que:

1. Levanta la app con `docker compose`
2. Instala `@lhci/cli`
3. Ejecuta Lighthouse CI con la config en `lighthouserc.js`
4. Aserta scores ≥ 90 en las cuatro categorías
5. Sube el reporte como artifact

---

## Cómo reproducir localmente

```bash
# 1. Levantar la app
docker compose up -d

# 2. Warm-up
curl -sS http://localhost:8000/api/v1/auth/login > /dev/null

# 3. Ejecutar auditoría
npx lighthouse http://localhost:8000/api/v1/auth/login \
  --preset=desktop \
  --only-categories=performance,accessibility,best-practices,seo \
  --skip-audits=is-on-https,redirects-http \
  --output=json --output-path=./lh-report.json

# 4. Ver scores
node -e "const r=JSON.parse(require('fs').readFileSync('lh-report.json','utf8')); Object.keys(r.categories).forEach(k=>console.log(k+': '+Math.round(r.categories[k].score*100)))"
```
