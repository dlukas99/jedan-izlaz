# web – karta JEDAN IZLAZ

Vite + React + TypeScript + MapLibre GL JS. Podatke čita isključivo iz `public/data/` (generira ih `python -m etl.pipeline`).

```powershell
npm install
npm run dev        # http://localhost:5173/
npm run build      # dist/ za GitHub Pages (base /jedan-izlaz/)
node scripts/snimke.mjs http://localhost:4173/jedan-izlaz/ ../docs/snimke   # snimke zaslona (nakon npm run preview)
```

Podloga: OpenFreeMap (© OpenMapTiles, © OpenStreetMap contributors). FWI i karta goriva: EFFIS WMS uživo (CC BY 4.0).
