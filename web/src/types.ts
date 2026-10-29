export type Scenarij = 'opt' | 'sred' | 'pes'
export type Raspon = Record<Scenarij, number | null>
export type Klasa = 'E0' | 'E1' | 'E2-5' | 'E6+'
export type Prioritet = 'A' | 'B' | 'C' | '-'

export interface Naselje {
  id: string
  naziv: string
  jls: string
  zupanija: string
  stanovnici_2021: number
  stanovnici_65plus: number
  postelje_jls: number
  stanovi_odmor_jls: number
  p_ljeto: Raspon
  udio_naselja: number
  udio_metoda: string
  izlazi_e: number
  klasa_izlaza: Klasa
  usko_grlo_id: string | null
  ljudi_iza_reza: Raspon | null
  t_evak_h: Raspon | null
  pokretni_most: boolean
  samo_putovi: boolean
  trajektna_linija: string | null
  h_stat: number | null
  h_gorivo: number | null
  h_pozari_udio: number | null
  h_razred: 'nizak' | 'srednji' | 'visok' | null
  prioritet: Prioritet
  iz: number
  druga_cesta_km: number | null
  druga_cesta_udio_track: number | null
  tocka_izvor: string
  napomene: string[]
  izvori: string[]
}

export interface UskoGrlo {
  id: string
  cesta_ref: string | null
  naziv: string | null
  pokretni_most: boolean
  most: boolean
  pokretni_most_iza: boolean
  broj_izlaza: number
  kapacitet_voz_h: Raspon
  ljudi_iza: Raspon
  t_evak_h: Raspon
  naselja_iza: string[]
  naselja_iza_nazivi: string[]
  pldp: { godina: number; vrijednost: number; brojilo: string; naziv: string } | null
  druga_cesta_km: number | null
}

export interface Izvor {
  kljuc: string
  naziv: string
  izdavac: string
  url: string | null
  url_paketa?: string
  licenca: string
  navod: string
  dohvaceno: string | null
  metadata_modified: string | null
}

export interface Meta {
  generirano: string
  nacin: 'live' | 'cache' | 'mock'
  zupanija?: string
  scenariji: Record<string, unknown>
  izvori: Izvor[]
  odricanje: string
  validacija?: Record<string, unknown>
  h_tercili?: [number, number]
}

export interface Fwi {
  datum: string
  sloj: string
  izvor: string
  dohvaceno: string
  vrijednosti: Record<string, number | null>
  razredi: Record<string, string | null>
}

export interface Kpi {
  datum: string
  broj_naselja: number
  naselja_po_klasi: Record<string, number>
  naselja_po_prioritetu: Record<string, number>
  ljudi_ljeti_u_naseljima_E0: Record<Scenarij, number>
  ljudi_ljeti_u_naseljima_E1: Record<Scenarij, number>
}

export interface Podaci {
  naselja: GeoJSON.FeatureCollection<GeoJSON.Point, Naselje>
  uskaGrla: GeoJSON.FeatureCollection<GeoJSON.Geometry, UskoGrlo>
  drugeCeste: GeoJSON.FeatureCollection | null
  pozari: GeoJSON.FeatureCollection | null
  meta: Meta
  kpi: Kpi | null
  fwiDanas: Fwi | null
  fwiPovijesni: Fwi | null
}
