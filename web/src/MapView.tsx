import { useEffect, useRef } from 'react'
import maplibregl, { type ExpressionSpecification, type GeoJSONSource } from 'maplibre-gl'
import 'maplibre-gl/dist/maplibre-gl.css'
import type { Podaci } from './types'
import { BOJA_PRIORITETA } from './format'
import { POVIJESNI_DAN } from './data'

export type FwiSloj = 'nista' | 'danas' | 'povijesni'
export interface Slojevi {
  fwi: FwiSloj
  pozari: boolean
  gorivo: boolean
  drugeCeste: boolean
  svaGrla: boolean
}

interface Props {
  podaci: Podaci
  pravci: GeoJSON.FeatureCollection | null
  odabrano: string | null
  onOdaberi: (id: string | null) => void
  slojevi: Slojevi
}

// Otvoreni vektorski stil (OpenFreeMap, podaci © OpenStreetMap contributors).
const STIL = 'https://tiles.openfreemap.org/styles/positron'
// EFFIS WMS (Copernicus EMS / JRC, CC BY 4.0) — dohvaća se uživo iz preglednika.
// Pločice od 512 px: četiri puta manje zahtjeva prema EFFIS-u nego 256 px.
const EFFIS = 'https://maps.effis.emergency.copernicus.eu/effis?service=WMS&version=1.1.1&request=GetMap&srs=EPSG:3857&bbox={bbox-epsg-3857}&width=512&height=512&format=image/png&transparent=true&styles='
const ATRIB_EFFIS = 'FWI i gorivo: <a href="https://forest-fire.emergency.copernicus.eu/">EFFIS</a>, Copernicus EMS / JRC (CC BY 4.0)'

// Boje odabranog naselja: plavo = izlazni pravci, crveno = usko grlo, zeleno = kandidat za drugu cestu.
// Uz svaku boju ide i natpis na karti (broj pravca, „usko grlo“), pa boja nije jedini nositelj značenja.
export const BOJA_PRAVCA = '#0b57d0'
export const BOJA_GRLA = '#d7191c'
export const BOJA_DRUGE = '#1b7837'

const PRAZNO: GeoJSON.FeatureCollection = { type: 'FeatureCollection', features: [] }
const danas = () => new Date().toISOString().slice(0, 10)

const bojaPrioriteta: ExpressionSpecification = [
  'match', ['get', 'prioritet'],
  'A', BOJA_PRIORITETA.A.bg, 'B', BOJA_PRIORITETA.B.bg, 'C', BOJA_PRIORITETA.C.bg, BOJA_PRIORITETA['-'].bg,
]
const bojaTeksta: ExpressionSpecification = [
  'match', ['get', 'prioritet'],
  'A', BOJA_PRIORITETA.A.fg, 'B', BOJA_PRIORITETA.B.fg, 'C', BOJA_PRIORITETA.C.fg, BOJA_PRIORITETA['-'].fg,
]

/** Ravna svojstva za MapLibre (ugniježđeni objekti se u izrazima ne mogu čitati). */
function zaKartu(p: Podaci) {
  return {
    type: 'FeatureCollection' as const,
    features: p.naselja.features.map((f) => ({
      type: 'Feature' as const,
      geometry: f.geometry,
      properties: {
        id: f.properties.id,
        naziv: f.properties.naziv,
        prioritet: f.properties.prioritet,
        klasa: f.properties.klasa_izlaza,
        izlazi: f.properties.klasa_izlaza === 'E0' ? 'samo morem'
          : f.properties.izlazi_e >= 6 ? '6+ izlaza'
            : `${f.properties.izlazi_e} ${f.properties.izlazi_e === 1 ? 'izlaz' : 'izlaza'}`,
        oznaka: f.properties.prioritet === '-' ? '–' : f.properties.prioritet,
        ljudi: f.properties.p_ljeto.sred ?? 0,
        red: { A: 4, B: 3, C: 2, '-': 1 }[f.properties.prioritet],
      },
    })),
  }
}

/** Krajnje točke pravaca odabranog naselja („1 · autocesta“), da se vidi kamo pravac vodi. */
function krajeviPravaca(pravci: GeoJSON.FeatureCollection | null, id: string | null): GeoJSON.FeatureCollection {
  if (!pravci || !id) return PRAZNO
  return {
    type: 'FeatureCollection',
    features: pravci.features.filter((f) => f.properties?.naselje_id === id).map((f) => {
      const c = (f.geometry as GeoJSON.LineString).coordinates
      return { type: 'Feature', geometry: { type: 'Point', coordinates: c[c.length - 1] },
        properties: { natpis: `${f.properties?.redni} · ${f.properties?.kraj}`, vrsta: 'kraj' } }
    }),
  }
}

/** Sredina najdulje dionice linije — tu stavljamo natpis („USKO GRLO“), jer natpis duž
 *  kratke dionice MapLibre ne prikaže kad je tekst dulji od same crte. */
function sredina(g: GeoJSON.Geometry): number[] | null {
  const dijelovi = g.type === 'LineString' ? [g.coordinates] : g.type === 'MultiLineString' ? g.coordinates : []
  const dio = dijelovi.sort((a, b) => b.length - a.length)[0]
  return dio?.length ? dio[Math.floor(dio.length / 2)] : null
}

/** Natpisi za odabrano naselje: krajevi pravaca, usko grlo, druga cesta. */
function natpisi(podaci: Podaci, pravci: GeoJSON.FeatureCollection | null, id: string | null): GeoJSON.FeatureCollection {
  const n = podaci.naselja.features.find((x) => x.properties.id === id)
  if (!n) return PRAZNO
  const tocka = (c: number[] | null, natpis: string, vrsta: string): GeoJSON.Feature[] =>
    c ? [{ type: 'Feature', geometry: { type: 'Point', coordinates: c }, properties: { natpis, vrsta } }] : []
  const ugId = n.properties.usko_grlo_id
  return {
    type: 'FeatureCollection',
    features: [
      ...krajeviPravaca(pravci, id).features,
      ...podaci.uskaGrla.features.filter((x) => x.properties.id === ugId)
        .flatMap((x) => tocka(sredina(x.geometry), 'USKO GRLO', 'grlo')),
      ...(podaci.drugeCeste?.features ?? []).filter((x) => x.properties?.usko_grlo_id === ugId)
        .flatMap((x) => tocka(sredina(x.geometry), 'druga cesta?', 'druga')),
    ],
  }
}

/** Obuhvat odabranog naselja: točka + njegovi pravci + usko grlo + druga cesta. */
function obuhvat(podaci: Podaci, pravci: GeoJSON.FeatureCollection | null, id: string): maplibregl.LngLatBounds | null {
  const f = podaci.naselja.features.find((x) => x.properties.id === id)
  if (!f) return null
  const b = new maplibregl.LngLatBounds(f.geometry.coordinates as [number, number], f.geometry.coordinates as [number, number])
  const dodaj = (g: GeoJSON.Geometry) => {
    const koord = g.type === 'LineString' ? g.coordinates : g.type === 'MultiLineString' ? g.coordinates.flat() : []
    for (const c of koord) b.extend(c as [number, number])
  }
  pravci?.features.filter((x) => x.properties?.naselje_id === id).forEach((x) => dodaj(x.geometry))
  const ugId = f.properties.usko_grlo_id
  podaci.uskaGrla.features.filter((x) => x.properties.id === ugId).forEach((x) => dodaj(x.geometry))
  podaci.drugeCeste?.features.filter((x) => x.properties?.usko_grlo_id === ugId).forEach((x) => dodaj(x.geometry))
  return b
}

export default function MapView({ podaci, pravci, odabrano, onOdaberi, slojevi }: Props) {
  const div = useRef<HTMLDivElement>(null)
  const karta = useRef<maplibregl.Map | null>(null)
  const spremna = useRef(false)

  // Kad je karta spremna, odmah izvrši; inače pričekaj događaj 'spremna'.
  const kadSpremna = (f: (m: maplibregl.Map) => void) => {
    const m = karta.current
    if (!m) return
    if (spremna.current) f(m)
    else m.once('spremna', () => f(m))
  }

  useEffect(() => {
    if (!div.current) return
    const m = new maplibregl.Map({
      container: div.current,
      style: STIL,
      center: [15.9, 43.8],
      zoom: 8.6,
      attributionControl: { compact: true, customAttribution: ATRIB_EFFIS },
    })
    karta.current = m
    m.addControl(new maplibregl.NavigationControl({ showCompass: false }), 'top-right')
    m.addControl(new maplibregl.ScaleControl({ unit: 'metric' }), 'bottom-left')
    const oblacic = new maplibregl.Popup({ closeButton: false, closeOnClick: false, offset: 12, className: 'oblacic' })

    m.on('load', () => {
      m.addSource('gorivo', { type: 'raster', tiles: [`${EFFIS}&layers=fuel_map`], tileSize: 512 })
      m.addLayer({ id: 'gorivo', type: 'raster', source: 'gorivo', paint: { 'raster-opacity': 0.55 },
        layout: { visibility: 'none' } })
      m.addSource('fwi', { type: 'raster', tiles: [`${EFFIS}&layers=mf010.fwi&time=${danas()}`], tileSize: 512 })
      m.addLayer({ id: 'fwi', type: 'raster', source: 'fwi', paint: { 'raster-opacity': 0.55 },
        layout: { visibility: 'none' } })
      if (podaci.pozari) {
        m.addSource('pozari', { type: 'geojson', data: podaci.pozari })
        m.addLayer({ id: 'pozari', type: 'fill', source: 'pozari', layout: { visibility: 'none' },
          paint: { 'fill-color': '#6b3a1e', 'fill-opacity': 0.35, 'fill-outline-color': '#3d1f0d' } })
      }

      // --- opći prikaz: uska grla (zadano samo ona s jednom cestom) i kandidati za drugu cestu
      m.addSource('druge', { type: 'geojson', data: podaci.drugeCeste ?? PRAZNO })
      m.addLayer({ id: 'druge', type: 'line', source: 'druge', layout: { visibility: 'none', 'line-cap': 'round' },
        paint: { 'line-color': BOJA_DRUGE, 'line-width': 2.5, 'line-dasharray': [1.5, 1.5] } })
      m.addSource('grla', { type: 'geojson', data: podaci.uskaGrla })
      // Debljina uskog grla raste s brojem ljudi iza njega (središnji scenarij).
      const ljudiIza: ExpressionSpecification = ['coalesce', ['get', 'sred', ['get', 'ljudi_iza']], 0]
      const sirina: ExpressionSpecification = ['interpolate', ['linear'], ljudiIza, 0, 2.5, 1000, 4, 10000, 7, 30000, 10]
      m.addLayer({ id: 'grla-obrub', type: 'line', source: 'grla', layout: { 'line-cap': 'round' },
        paint: { 'line-color': '#ffffff', 'line-width': ['+', sirina, 3] } })
      m.addLayer({ id: 'grla', type: 'line', source: 'grla', layout: { 'line-cap': 'round' },
        paint: { 'line-color': '#54278f', 'line-width': sirina } })

      // --- odabrano naselje: izlazni pravci, njegovo usko grlo, njegova druga cesta
      m.addSource('pravci', { type: 'geojson', data: PRAZNO })
      m.addLayer({ id: 'pravci-obrub', type: 'line', source: 'pravci', filter: ['==', ['get', 'naselje_id'], ''],
        layout: { 'line-cap': 'round', 'line-join': 'round' }, paint: { 'line-color': '#ffffff', 'line-width': 8 } })
      m.addLayer({ id: 'pravci', type: 'line', source: 'pravci', filter: ['==', ['get', 'naselje_id'], ''],
        layout: { 'line-cap': 'round', 'line-join': 'round' }, paint: { 'line-color': BOJA_PRAVCA, 'line-width': 4.5 } })
      m.addLayer({ id: 'druge-odabrano', type: 'line', source: 'druge', filter: ['==', ['get', 'usko_grlo_id'], ''],
        layout: { 'line-cap': 'round' },
        paint: { 'line-color': BOJA_DRUGE, 'line-width': 4.5, 'line-dasharray': [1.2, 1] } })
      m.addLayer({ id: 'grla-odabrano-obrub', type: 'line', source: 'grla', filter: ['==', ['get', 'id'], ''],
        layout: { 'line-cap': 'round' }, paint: { 'line-color': '#ffffff', 'line-width': 15 } })
      m.addLayer({ id: 'grla-odabrano', type: 'line', source: 'grla', filter: ['==', ['get', 'id'], ''],
        layout: { 'line-cap': 'round' }, paint: { 'line-color': BOJA_GRLA, 'line-width': 9 } })
      m.addLayer({ id: 'pravci-broj', type: 'symbol', source: 'pravci', filter: ['==', ['get', 'naselje_id'], ''],
        layout: { 'symbol-placement': 'line', 'symbol-spacing': 180, 'text-field': ['to-string', ['get', 'redni']],
          'text-font': ['Noto Sans Bold'], 'text-size': 14, 'text-keep-upright': true },
        paint: { 'text-color': BOJA_PRAVCA, 'text-halo-color': '#ffffff', 'text-halo-width': 2.5 } })
      m.addSource('krajevi', { type: 'geojson', data: PRAZNO })
      m.addLayer({ id: 'krajevi', type: 'circle', source: 'krajevi', filter: ['==', ['get', 'vrsta'], 'kraj'],
        paint: { 'circle-radius': 6, 'circle-color': '#ffffff', 'circle-stroke-color': BOJA_PRAVCA, 'circle-stroke-width': 3 } })
      // Isti izvor nosi natpise krajeva pravaca, uskog grla i druge ceste; boja i položaj ovise o vrsti.
      m.addLayer({ id: 'krajevi-natpis', type: 'symbol', source: 'krajevi',
        layout: { 'text-field': ['get', 'natpis'], 'text-font': ['Noto Sans Bold'],
          'text-size': ['match', ['get', 'vrsta'], 'grlo', 14, 12],
          'text-anchor': ['match', ['get', 'vrsta'], 'kraj', 'left', 'bottom'] as ExpressionSpecification,
          'text-offset': ['match', ['get', 'vrsta'], 'kraj', ['literal', [0.9, 0]], ['literal', [0, -0.8]]] as ExpressionSpecification,
          'text-allow-overlap': true },
        paint: { 'text-color': ['match', ['get', 'vrsta'], 'kraj', BOJA_PRAVCA, 'grlo', BOJA_GRLA, BOJA_DRUGE],
          'text-halo-color': '#ffffff', 'text-halo-width': 2.5 } })

      // --- naselja (iznad svega)
      m.addSource('naselja', { type: 'geojson', data: zaKartu(podaci) })
      const radijus: ExpressionSpecification = ['interpolate', ['linear'], ['sqrt', ['get', 'ljudi']], 0, 7, 50, 11, 200, 20]
      m.addLayer({ id: 'naselja-krug', type: 'circle', source: 'naselja',
        layout: { 'circle-sort-key': ['get', 'red'] },
        paint: { 'circle-color': bojaPrioriteta, 'circle-radius': radijus,
          'circle-stroke-color': '#ffffff', 'circle-stroke-width': 1.5 } })
      m.addLayer({ id: 'naselja-odabrano', type: 'circle', source: 'naselja', filter: ['==', ['get', 'id'], ''],
        paint: { 'circle-color': 'rgba(0,0,0,0)', 'circle-radius': ['+', radijus, 5],
          'circle-stroke-color': '#000000', 'circle-stroke-width': 3 } })
      m.addLayer({ id: 'naselja-slovo', type: 'symbol', source: 'naselja',
        layout: { 'text-field': ['get', 'oznaka'], 'text-font': ['Noto Sans Bold'], 'text-size': 12,
          'text-allow-overlap': true, 'symbol-sort-key': ['get', 'red'] },
        paint: { 'text-color': bojaTeksta } })
      m.addLayer({ id: 'naselja-ime', type: 'symbol', source: 'naselja', minzoom: 9.5,
        layout: { 'text-field': ['concat', ['get', 'naziv'], ' · ', ['get', 'izlazi']], 'text-font': ['Noto Sans Regular'],
          'text-size': 12, 'text-offset': [0, 1.5], 'text-anchor': 'top', 'text-optional': true },
        paint: { 'text-color': '#1a1a1a', 'text-halo-color': '#ffffff', 'text-halo-width': 1.5 } })

      m.on('click', 'naselja-krug', (e) => {
        const f = e.features?.[0]
        if (f) onOdaberi(String(f.properties?.id))
      })
      m.on('click', 'grla', (e) => {
        const f = e.features?.[0]
        const iza = f && JSON.parse(String(f.properties?.naselja_iza ?? '[]'))
        if (iza?.length) onOdaberi(iza[0])
      })
      // Oblačić s imenom i brojem izlaza pri prelasku mišem — brzo „skeniranje“ karte bez klikanja.
      m.on('mousemove', 'naselja-krug', (e) => {
        const f = e.features?.[0]
        if (!f) return
        m.getCanvas().style.cursor = 'pointer'
        oblacic.setLngLat((f.geometry as GeoJSON.Point).coordinates as [number, number])
          .setText(`${f.properties?.naziv} · ${f.properties?.izlazi} · prioritet ${f.properties?.oznaka}`).addTo(m)
      })
      m.on('mouseleave', 'naselja-krug', () => { m.getCanvas().style.cursor = ''; oblacic.remove() })
      m.on('mouseenter', 'grla', () => { m.getCanvas().style.cursor = 'pointer' })
      m.on('mouseleave', 'grla', () => { m.getCanvas().style.cursor = '' })
      spremna.current = true
      m.fire('spremna')
    })
    return () => { m.remove(); karta.current = null; spremna.current = false }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [podaci])

  // Pravci stižu u pozadini (nakon prvog prikaza karte).
  useEffect(() => {
    kadSpremna((m) => {
      (m.getSource('pravci') as GeoJSONSource | undefined)?.setData(pravci ?? PRAZNO)
      ;(m.getSource('krajevi') as GeoJSONSource | undefined)?.setData(natpisi(podaci, pravci, odabrano))
    })
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [pravci])

  // Slojevi (FWI, požari, gorivo, druge ceste, sva uska grla)
  useEffect(() => {
    kadSpremna((m) => {
      const vid = (id: string, v: boolean) => m.getLayer(id) && m.setLayoutProperty(id, 'visibility', v ? 'visible' : 'none')
      vid('gorivo', slojevi.gorivo)
      vid('pozari', slojevi.pozari)
      vid('druge', slojevi.drugeCeste)
      // Zadano su vidljiva samo uska grla s jednom jedinom cestom — ostalo je previše „šara“.
      const filterGrla: maplibregl.FilterSpecification | null = slojevi.svaGrla ? null : ['==', ['get', 'broj_izlaza'], 1]
      m.setFilter('grla', filterGrla)
      m.setFilter('grla-obrub', filterGrla)
      if (slojevi.fwi !== 'nista') {
        const datum = slojevi.fwi === 'danas' ? danas() : POVIJESNI_DAN
        const src = m.getSource('fwi') as maplibregl.RasterTileSource | undefined
        src?.setTiles([`${EFFIS}&layers=mf010.fwi&time=${datum}`])
      }
      vid('fwi', slojevi.fwi !== 'nista')
    })
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [slojevi])

  // Odabrano naselje: pravci, usko grlo, druga cesta, ostalo prigušeno, karta se namjesti na obuhvat.
  useEffect(() => {
    kadSpremna((m) => {
      const f = podaci.naselja.features.find((x) => x.properties.id === odabrano)
      const id = f ? f.properties.id : ''
      const ugId = f?.properties.usko_grlo_id ?? ''
      m.setFilter('naselja-odabrano', ['==', ['get', 'id'], id])
      for (const s of ['pravci', 'pravci-obrub', 'pravci-broj']) m.setFilter(s, ['==', ['get', 'naselje_id'], id])
      for (const s of ['grla-odabrano', 'grla-odabrano-obrub']) m.setFilter(s, ['==', ['get', 'id'], ugId])
      m.setFilter('druge-odabrano', ['==', ['get', 'usko_grlo_id'], ugId])
      ;(m.getSource('krajevi') as GeoJSONSource | undefined)?.setData(natpisi(podaci, pravci, odabrano))
      // Prigušivanje: odabrano naselje i ono što mu pripada ostaje jasno, ostalo blijedi.
      const prigusi = (x: number) => (f ? x : 1)
      m.setPaintProperty('naselja-krug', 'circle-opacity', f ? ['case', ['==', ['get', 'id'], id], 1, 0.35] : 1)
      m.setPaintProperty('naselja-krug', 'circle-stroke-opacity', f ? ['case', ['==', ['get', 'id'], id], 1, 0.35] : 1)
      m.setPaintProperty('naselja-slovo', 'text-opacity', f ? ['case', ['==', ['get', 'id'], id], 1, 0.4] : 1)
      m.setPaintProperty('grla', 'line-opacity', prigusi(0.2))
      m.setPaintProperty('grla-obrub', 'line-opacity', prigusi(0.2))
      m.setPaintProperty('druge', 'line-opacity', prigusi(0.25))
      if (!f) return
      // Naselje i pravce smjestimo u dio karte koji ploče ne prekrivaju (desno kartica, lijevo tražilica).
      const mobitel = window.innerWidth <= 800
      const v = m.getContainer().clientHeight
      const w = m.getContainer().clientWidth
      const padding = mobitel ? { top: 70, bottom: Math.round(v * 0.55) + 20, left: 30, right: 30 }
        : { top: 60, bottom: 50, left: w > 1150 ? 370 : 40, right: 520 }
      const b = obuhvat(podaci, pravci, id)
      if (b && (b.getWest() !== b.getEast() || b.getSouth() !== b.getNorth())) {
        m.fitBounds(b, { padding, maxZoom: 13, duration: 700 })
      } else {
        m.easeTo({ center: f.geometry.coordinates as [number, number], zoom: Math.max(m.getZoom(), 12), padding, duration: 700 })
      }
    })
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [odabrano, podaci, pravci != null])

  useEffect(() => {
    kadSpremna((m) => (m.getSource('naselja') as GeoJSONSource | undefined)?.setData(zaKartu(podaci)))
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [podaci])

  return <div ref={div} className="karta" role="region" aria-label="Karta naselja: broj cestovnih izlaza, uska grla i izlazni pravci" />
}
