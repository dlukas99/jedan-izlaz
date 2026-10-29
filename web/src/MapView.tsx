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
}

interface Props {
  podaci: Podaci
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
        oznaka: f.properties.prioritet === '-' ? '–' : f.properties.prioritet,
        ljudi: f.properties.p_ljeto.sred ?? 0,
        red: { A: 4, B: 3, C: 2, '-': 1 }[f.properties.prioritet],
      },
    })),
  }
}

export default function MapView({ podaci, odabrano, onOdaberi, slojevi }: Props) {
  const div = useRef<HTMLDivElement>(null)
  const karta = useRef<maplibregl.Map | null>(null)
  const spremna = useRef(false)

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
      if (podaci.drugeCeste) {
        m.addSource('druge', { type: 'geojson', data: podaci.drugeCeste })
        m.addLayer({ id: 'druge', type: 'line', source: 'druge', layout: { visibility: 'visible', 'line-cap': 'round' },
          paint: { 'line-color': '#1b7837', 'line-width': 3, 'line-dasharray': [1.5, 1.5] } })
      }
      m.addSource('grla', { type: 'geojson', data: podaci.uskaGrla })
      // Debljina uskog grla raste s brojem ljudi iza njega (središnji scenarij).
      const ljudiIza: ExpressionSpecification = ['coalesce', ['get', 'sred', ['get', 'ljudi_iza']], 0]
      const sirina: ExpressionSpecification = ['interpolate', ['linear'], ljudiIza, 0, 2.5, 1000, 4, 10000, 7, 30000, 10]
      m.addLayer({ id: 'grla-obrub', type: 'line', source: 'grla', layout: { 'line-cap': 'round' },
        paint: { 'line-color': '#ffffff', 'line-width': ['+', sirina, 3] } })
      m.addLayer({ id: 'grla', type: 'line', source: 'grla', layout: { 'line-cap': 'round' },
        paint: { 'line-color': '#54278f', 'line-width': sirina } })
      m.addSource('naselja', { type: 'geojson', data: zaKartu(podaci) })
      const radijus: ExpressionSpecification = ['interpolate', ['linear'], ['sqrt', ['get', 'ljudi']], 0, 7, 50, 11, 200, 20]
      m.addLayer({ id: 'naselja-krug', type: 'circle', source: 'naselja',
        layout: { 'circle-sort-key': ['get', 'red'] },
        paint: { 'circle-color': bojaPrioriteta, 'circle-radius': radijus,
          'circle-stroke-color': ['case', ['==', ['get', 'id'], ''], '#000', '#ffffff'], 'circle-stroke-width': 1.5 } })
      m.addLayer({ id: 'naselja-odabrano', type: 'circle', source: 'naselja', filter: ['==', ['get', 'id'], ''],
        paint: { 'circle-color': 'rgba(0,0,0,0)', 'circle-radius': ['+', radijus, 5],
          'circle-stroke-color': '#000000', 'circle-stroke-width': 3 } })
      m.addLayer({ id: 'naselja-slovo', type: 'symbol', source: 'naselja',
        layout: { 'text-field': ['get', 'oznaka'], 'text-font': ['Noto Sans Bold'], 'text-size': 12,
          'text-allow-overlap': true, 'symbol-sort-key': ['get', 'red'] },
        paint: { 'text-color': bojaTeksta } })
      m.addLayer({ id: 'naselja-ime', type: 'symbol', source: 'naselja', minzoom: 9.5,
        layout: { 'text-field': ['concat', ['get', 'naziv'], ' · ', ['get', 'klasa']], 'text-font': ['Noto Sans Regular'],
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
      for (const sloj of ['naselja-krug', 'grla']) {
        m.on('mouseenter', sloj, () => { m.getCanvas().style.cursor = 'pointer' })
        m.on('mouseleave', sloj, () => { m.getCanvas().style.cursor = '' })
      }
      spremna.current = true
      m.fire('spremna')
    })
    return () => { m.remove(); karta.current = null; spremna.current = false }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [podaci])

  // Slojevi (FWI, požari, gorivo, druge ceste)
  useEffect(() => {
    const m = karta.current
    if (!m) return
    const primijeni = () => {
      const vid = (id: string, v: boolean) => m.getLayer(id) && m.setLayoutProperty(id, 'visibility', v ? 'visible' : 'none')
      vid('gorivo', slojevi.gorivo)
      vid('pozari', slojevi.pozari)
      vid('druge', slojevi.drugeCeste)
      if (slojevi.fwi !== 'nista') {
        const datum = slojevi.fwi === 'danas' ? danas() : POVIJESNI_DAN
        const src = m.getSource('fwi') as maplibregl.RasterTileSource | undefined
        src?.setTiles([`${EFFIS}&layers=mf010.fwi&time=${datum}`])
      }
      vid('fwi', slojevi.fwi !== 'nista')
    }
    if (spremna.current) primijeni()
    else m.once('spremna', primijeni)
  }, [slojevi])

  // Odabrano naselje: obrub + let do naselja
  useEffect(() => {
    const m = karta.current
    if (!m) return
    const primijeni = () => {
      m.setFilter('naselja-odabrano', ['==', ['get', 'id'], odabrano ?? ''])
      const f = podaci.naselja.features.find((x) => x.properties.id === odabrano)
      if (f) {
        // Naselje centriramo u dio karte koji kartica ne prekriva (desno na računalu, dolje na mobitelu).
        const mobitel = window.innerWidth <= 800
        const v = m.getContainer().clientHeight
        m.easeTo({
          center: f.geometry.coordinates as [number, number], zoom: Math.max(m.getZoom(), 10.5), duration: 600,
          padding: mobitel ? { top: 0, bottom: Math.round(v * 0.6), left: 0, right: 0 }
            : { top: 0, bottom: 0, left: 320, right: 420 },
        })
      }
    }
    if (spremna.current) primijeni()
    else m.once('spremna', primijeni)
  }, [odabrano, podaci])

  useEffect(() => {
    const m = karta.current
    if (m && spremna.current) (m.getSource('naselja') as GeoJSONSource | undefined)?.setData(zaKartu(podaci))
  }, [podaci])

  return <div ref={div} className="karta" role="region" aria-label="Karta naselja po prioritetu i uskih grla" />
}
