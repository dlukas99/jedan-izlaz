import type { Klasa, Prioritet, Raspon } from './types'

const broj = new Intl.NumberFormat('hr-HR', { maximumFractionDigits: 0 })
const dec1 = new Intl.NumberFormat('hr-HR', { minimumFractionDigits: 1, maximumFractionDigits: 1 })

/** „2026-08-13“ → „13. 8. 2026.“ (hrvatski pravopis) */
export const fmtDatum = (iso: string | null | undefined) => {
  if (!iso) return '–'
  const [g, m, d] = iso.slice(0, 10).split('-').map(Number)
  return `${d}. ${m}. ${g}.`
}

export const fmtBroj =(v: number | null | undefined) => (v == null ? '–' : broj.format(v))
export const fmtDec = (v: number | null | undefined) => (v == null ? '–' : dec1.format(v))

/** Raspon ljudi: „3.200–4.100 (središnje 3.600)“ */
export function fmtRasponLjudi(r: Raspon | null | undefined): string {
  if (!r || r.sred == null) return '–'
  return `${fmtBroj(r.opt)}–${fmtBroj(r.pes)} (središnje ${fmtBroj(r.sred)})`
}

/** Jedno vrijeme: ispod sat vremena u minutama, inače u satima s jednom decimalom. */
export const fmtSati = (h: number | null | undefined) =>
  h == null ? '–' : h < 1 ? `${Math.max(1, Math.round(h * 60))} min` : `${dec1.format(h)} h`

/** Vrijeme: „1,2 h – 4,8 h (središnje 2,4 h)“ */
export function fmtRasponSati(r: Raspon | null | undefined): string {
  if (!r || r.sred == null) return '–'
  return `${fmtSati(r.opt)} – ${fmtSati(r.pes)} (središnje ${fmtSati(r.sred)})`
}

export const OPIS_KLASE: Record<Klasa, string> = {
  E0: 'Nema cestovnog izlaza – izlaz samo morem',
  E1: 'Jedan cestovni izlaz',
  'E2-5': '2–5 izlaznih pravaca',
  'E6+': '6 ili više izlaznih pravaca',
}

export const OPIS_PRIORITETA: Record<Prioritet, string> = {
  A: 'A – najviši prioritet za plan evakuacije',
  B: 'B – povišen prioritet',
  C: 'C – ograničen izlaz, niži prioritet',
  '-': '– dovoljno izlaza (6+)',
}

/** Boje prioriteta (kontrast teksta provjeren za WCAG AA). Boja nikad nije sama: uvijek ide i slovo. */
export const BOJA_PRIORITETA: Record<Prioritet, { bg: string; fg: string }> = {
  A: { bg: '#a50f15', fg: '#ffffff' },
  B: { bg: '#b54000', fg: '#ffffff' },
  C: { bg: '#fdd49e', fg: '#3b2300' },
  '-': { bg: '#d9d9d9', fg: '#252525' },
}

export const OPIS_IZVORA: Record<string, string> = {
  dzs_popis_naselja: 'DZS, Popis 2021.',
  dzs_stanovi: 'DZS, Popis 2021. – stanovi za odmor',
  dzs_turizam_2025: 'DZS, Turizam u 2025. (tab. 2.11)',
  dzs_popunjenost_2025_08: 'DZS, popunjenost postelja, kolovoz 2025.',
  dgu_au: 'DGU, Upravne jedinice',
  dgu_rgi: 'DGU, Registar geografskih imena',
  osm: '© OpenStreetMap contributors',
  worldcover: 'ESA WorldCover 2021',
  effis_ba: 'EFFIS, opožarene površine',
  effis_fwi: 'EFFIS, FWI',
  hc_brojenje_2025: 'Hrvatske ceste, brojenje prometa 2025.',
  jadrolinija: 'Jadrolinija',
  tz_tisno_most: 'TZ Tisno',
}

export function csvPolje(v: unknown): string {
  const s = v == null ? '' : String(v)
  return /[";\n]/.test(s) ? `"${s.replace(/"/g, '""')}"` : s
}
