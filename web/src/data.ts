import type { Podaci } from './types'

export const POVIJESNI_DAN = '2026-08-13'
const BAZA = `${import.meta.env.BASE_URL}data/`

async function json<T>(ime: string, obavezno = true): Promise<T | null> {
  const r = await fetch(BAZA + ime, { cache: 'no-cache' })
  if (!r.ok) {
    if (obavezno) throw new Error(`Ne mogu učitati ${ime} (${r.status})`)
    return null
  }
  return (await r.json()) as T
}

export async function ucitajPodatke(): Promise<Podaci> {
  const [naselja, uskaGrla, meta, kpi, drugeCeste, pozari, fwiDanas, fwiPovijesni] = await Promise.all([
    json<Podaci['naselja']>('settlements.geojson'),
    json<Podaci['uskaGrla']>('bottlenecks.geojson'),
    json<Podaci['meta']>('meta.json'),
    json<Podaci['kpi']>('kpi.json', false),
    json<GeoJSON.FeatureCollection>('second_roads.geojson', false),
    json<GeoJSON.FeatureCollection>('burned.geojson', false),
    json<Podaci['fwiDanas']>('fwi_today.json', false),
    json<Podaci['fwiPovijesni']>(`fwi_${POVIJESNI_DAN}.json`, false),
  ])
  return {
    naselja: naselja!, uskaGrla: uskaGrla!, meta: meta!, kpi, drugeCeste, pozari,
    fwiDanas, fwiPovijesni,
  }
}

/** Izlazni pravci (~1,3 MB) učitavaju se u pozadini, nakon što se karta već prikaže. */
export async function ucitajPravce(): Promise<GeoJSON.FeatureCollection | null> {
  return json<GeoJSON.FeatureCollection>('routes.geojson', false).catch(() => null)
}
