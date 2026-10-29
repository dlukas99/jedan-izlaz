import { useMemo, useState } from 'react'
import type { Naselje, Scenarij } from './types'
import { BOJA_PRIORITETA, csvPolje, fmtBroj, fmtSati } from './format'

interface Props {
  naselja: Naselje[]
  scenarij: Scenarij
  onOdaberi: (id: string) => void
}

type Kljuc = 'prioritet' | 'naziv' | 'jls' | 'klasa' | 'ljudi' | 'iza' | 't' | 'h'
const RED_P = { A: 0, B: 1, C: 2, '-': 3 }
const RED_K = { E0: 0, E1: 1, 'E2-5': 2, 'E6+': 3 }

export default function PriorityList({ naselja, scenarij, onOdaberi }: Props) {
  const [jls, setJls] = useState('')
  const [samoOgraniceni, setSamoOgraniceni] = useState(true)
  const [sort, setSort] = useState<{ k: Kljuc; smjer: 1 | -1 }>({ k: 'prioritet', smjer: 1 })
  const sveJls = useMemo(() => [...new Set(naselja.map((n) => n.jls))].sort((a, b) => a.localeCompare(b, 'hr')), [naselja])

  const redovi = useMemo(() => {
    const v = (n: Naselje): number | string => {
      switch (sort.k) {
        case 'prioritet': return RED_P[n.prioritet] * 1000 - n.iz
        case 'naziv': return n.naziv
        case 'jls': return n.jls
        case 'klasa': return RED_K[n.klasa_izlaza]
        case 'ljudi': return n.p_ljeto[scenarij] ?? 0
        case 'iza': return n.ljudi_iza_reza?.[scenarij] ?? -1
        case 't': return n.t_evak_h?.[scenarij] ?? -1
        case 'h': return n.h_stat ?? -1
      }
    }
    return naselja
      .filter((n) => (!jls || n.jls === jls) && (!samoOgraniceni || n.klasa_izlaza !== 'E6+'))
      .sort((a, b) => {
        const x = v(a), y = v(b)
        const c = typeof x === 'string' ? x.localeCompare(String(y), 'hr') : x - (y as number)
        return c * sort.smjer
      })
  }, [naselja, jls, samoOgraniceni, sort, scenarij])

  const zaglavlje = (k: Kljuc, tekst: string, brojcano = false) => {
    const aktivno = sort.k === k
    return (
      <th scope="col" aria-sort={aktivno ? (sort.smjer === 1 ? 'ascending' : 'descending') : 'none'}
        className={brojcano ? 'broj' : undefined}>
        <button className="sort" onClick={() => setSort({ k, smjer: aktivno ? (-sort.smjer as 1 | -1) : (brojcano ? -1 : 1) })}>
          {tekst} <span aria-hidden="true">{aktivno ? (sort.smjer === 1 ? '▲' : '▼') : '↕'}</span>
        </button>
      </th>
    )
  }

  const izvozCsv = () => {
    const zag = ['matični broj', 'naselje', 'JLS', 'prioritet', 'indeks za sortiranje', 'klasa izlaza', 'broj izlaza',
      'stanovnici 2021', 'ljudi ljeti opt', 'ljudi ljeti sred', 'ljudi ljeti pes', 'ljudi iza uskog grla sred',
      'T evakuacije opt (h)', 'T evakuacije sred (h)', 'T evakuacije pes (h)', 'usko grlo', 'pokretni most',
      'izlaz morem', 'opasnost H (0–1)', 'razred opasnosti', 'druga cesta (km)']
    const red = (n: Naselje) => [n.id, n.naziv, n.jls, n.prioritet, n.iz, n.klasa_izlaza, n.izlazi_e, n.stanovnici_2021,
      n.p_ljeto.opt, n.p_ljeto.sred, n.p_ljeto.pes, n.ljudi_iza_reza?.sred, n.t_evak_h?.opt, n.t_evak_h?.sred,
      n.t_evak_h?.pes, n.usko_grlo_id, n.pokretni_most ? 'da' : 'ne', n.trajektna_linija, n.h_stat, n.h_razred,
      n.druga_cesta_km]
    const izvor = '# Izvor: JEDAN IZLAZ (DZS, DGU, OSM, EFFIS, ESA WorldCover, HC). Alat za planiranje, ne za uzbunjivanje.'
    const tekst = [izvor, zag.join(';'), ...redovi.map((n) => red(n).map(csvPolje).join(';'))].join('\r\n')
    const blob = new Blob(['﻿' + tekst], { type: 'text/csv;charset=utf-8' })
    const a = document.createElement('a')
    a.href = URL.createObjectURL(blob)
    a.download = `jedan-izlaz-prioriteti${jls ? '-' + jls : ''}.csv`
    a.click()
    URL.revokeObjectURL(a.href)
  }

  return (
    <section className="stranica" aria-labelledby="lista-naslov">
      <h2 id="lista-naslov">Prioritetna lista naselja</h2>
      <p className="uvod">Naselja kojima prvo treba plan evakuacije (uključujući morem). Razred prioriteta određuju broj
        izlaza, opasnost od požara i vrijeme evakuacije; unutar razreda redoslijed slijedi indeks. Brojke za
        odabrani scenarij; puni rasponi su na kartici naselja.</p>
      <div className="filteri">
        <label>JLS{' '}
          <select value={jls} onChange={(e) => setJls(e.target.value)}>
            <option value="">sve ({sveJls.length})</option>
            {sveJls.map((j) => <option key={j} value={j}>{j}</option>)}
          </select>
        </label>
        <label className="kvacica">
          <input type="checkbox" checked={samoOgraniceni} onChange={(e) => setSamoOgraniceni(e.target.checked)} />
          samo naselja s manje od 6 izlaza
        </label>
        <button className="gumb" onClick={izvozCsv}>Preuzmi CSV ({redovi.length})</button>
      </div>
      <div className="tablica-omot" tabIndex={0} role="region" aria-label="Tablica prioriteta, može se pomicati">
        <table>
          <caption className="sr-only">Naselja sortirana po prioritetu; kliknite naziv za karticu.</caption>
          <thead>
            <tr>
              {zaglavlje('prioritet', 'Prioritet')}
              {zaglavlje('naziv', 'Naselje')}
              {zaglavlje('jls', 'JLS')}
              {zaglavlje('klasa', 'Izlazi')}
              {zaglavlje('ljudi', 'Ljudi ljeti', true)}
              {zaglavlje('iza', 'Iza uskog grla', true)}
              {zaglavlje('t', 'Evakuacija', true)}
              {zaglavlje('h', 'Opasnost')}
            </tr>
          </thead>
          <tbody>
            {redovi.map((n) => {
              const b = BOJA_PRIORITETA[n.prioritet]
              return (
                <tr key={n.id}>
                  <td><span className="znacka mala" style={{ background: b.bg, color: b.fg }}>{n.prioritet === '-' ? '–' : n.prioritet}</span></td>
                  <td><button className="poveznica" onClick={() => onOdaberi(n.id)}>{n.naziv}</button></td>
                  <td>{n.jls}</td>
                  <td>{n.klasa_izlaza}{n.pokretni_most ? ' · pokretni most' : ''}
                    {n.klasa_izlaza === 'E0' ? (n.samo_putovi ? ' · samo putovi' : ' · more') : ''}</td>
                  <td className="broj">{fmtBroj(n.p_ljeto[scenarij])}</td>
                  <td className="broj">{fmtBroj(n.ljudi_iza_reza?.[scenarij])}</td>
                  <td className="broj">{n.klasa_izlaza === 'E0' ? (n.samo_putovi ? 'putovima' : 'morem') : fmtSati(n.t_evak_h?.[scenarij])}</td>
                  <td>{n.h_razred ?? '–'}</td>
                </tr>
              )
            })}
          </tbody>
        </table>
      </div>
    </section>
  )
}
