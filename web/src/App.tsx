import { useEffect, useMemo, useState } from 'react'
import './App.css'
import MapView, { type FwiSloj, type Slojevi } from './MapView'
import SettlementCard from './SettlementCard'
import Trazilica from './Trazilica'
import PriorityList from './PriorityList'
import SourcesPage from './SourcesPage'
import { POVIJESNI_DAN, ucitajPodatke, ucitajPravce } from './data'
import { BOJA_PRIORITETA, fmtDatum } from './format'
import type { Podaci, Scenarij } from './types'

type Ekran = 'karta' | 'lista' | 'izvori'
const ODRICANJE = 'Alat za planiranje, ne za uzbunjivanje. U opasnosti slijedite upute 112 i civilne zaštite.'

const ekranIzHasha = (): Ekran => {
  const h = window.location.hash.replace('#', '').split('/')[0]
  return h === 'lista' || h === 'izvori' ? h : 'karta'
}
const naseljeIzHasha = () => window.location.hash.split('/naselje/')[1] ?? null

export default function App() {
  const [podaci, setPodaci] = useState<Podaci | null>(null)
  const [greska, setGreska] = useState<string | null>(null)
  const [ekran, setEkran] = useState<Ekran>(ekranIzHasha())
  const [odabrano, setOdabrano] = useState<string | null>(naseljeIzHasha())
  const [scenarij, setScenarij] = useState<Scenarij>('sred')
  const [slojevi, setSlojevi] = useState<Slojevi>({ fwi: 'nista', pozari: false, gorivo: false, drugeCeste: false, svaGrla: false })
  const [panel, setPanel] = useState(window.innerWidth > 800)
  const [pravci, setPravci] = useState<GeoJSON.FeatureCollection | null>(null)

  useEffect(() => {
    ucitajPodatke().then((p) => { setPodaci(p); ucitajPravce().then(setPravci) }).catch((e) => setGreska(String(e)))
  }, [])
  useEffect(() => {
    const f = () => { setEkran(ekranIzHasha()); setOdabrano(naseljeIzHasha()) }
    window.addEventListener('hashchange', f)
    return () => window.removeEventListener('hashchange', f)
  }, [])

  const idi = (e: Ekran, id: string | null = odabrano) => {
    window.location.hash = e === 'karta' && id ? `karta/naselje/${id}` : e
  }
  const odaberi = (id: string | null) => {
    setOdabrano(id)
    window.history.replaceState(null, '', `#karta${id ? `/naselje/${id}` : ''}`)
  }

  const naselja = useMemo(() => podaci?.naselja.features.map((f) => f.properties) ?? [], [podaci])
  const odabranoN = naselja.find((n) => n.id === odabrano) ?? null
  const ug = odabranoN?.usko_grlo_id
    ? podaci?.uskaGrla.features.find((f) => f.properties.id === odabranoN.usko_grlo_id)?.properties ?? null : null

  if (greska) return <main className="poruka" role="alert">Podaci se nisu učitali: {greska}</main>
  if (!podaci) return <main className="poruka" aria-busy="true">Učitavanje podataka…</main>

  const datum13 = fmtDatum(POVIJESNI_DAN)
  return (
    <div className="aplikacija">
      {podaci.meta.nacin === 'mock' && (
        <div className="mock" role="alert">MOCK — izmišljeni podaci za razvoj, nisu stvarni</div>
      )}
      <header className="zaglavlje">
        <div className="naslov">
          <h1><span aria-hidden="true">⇥</span> JEDAN IZLAZ</h1>
          <p>Koliko cestovnih izlaza ima naselje kad gori? · {podaci.meta.zupanija ?? ''} županija (pilot)</p>
        </div>
        <nav aria-label="Glavna navigacija">
          {([['karta', 'Karta'], ['lista', 'Prioritetna lista'], ['izvori', 'Izvori i metoda']] as const).map(([k, t]) => (
            <a key={k} href={`#${k}`} aria-current={ekran === k ? 'page' : undefined}
              onClick={(e) => { e.preventDefault(); idi(k, k === 'karta' ? odabrano : null) }}>{t}</a>
          ))}
        </nav>
        <fieldset className="scenarij">
          <legend>Scenarij</legend>
          {(['opt', 'sred', 'pes'] as const).map((s) => (
            <label key={s} className={scenarij === s ? 'aktivno' : ''}>
              <input type="radio" name="scenarij" value={s} checked={scenarij === s} onChange={() => setScenarij(s)} />
              {{ opt: 'optimistični', sred: 'središnji', pes: 'pesimistični' }[s]}
            </label>
          ))}
        </fieldset>
      </header>

      <p className="odricanje" role="note">{ODRICANJE}</p>

      {ekran === 'karta' && (
        <main className="karta-ekran">
          <MapView podaci={podaci} pravci={pravci} odabrano={odabrano} onOdaberi={odaberi} slojevi={slojevi} />
          <div className={`kontrole ${panel ? 'otvoreno' : ''}`}>
            <Trazilica naselja={naselja} onOdaberi={odaberi} />
            <button className="kontrole-gumb" aria-expanded={panel} aria-controls="kontrole-sadrzaj"
              onClick={() => setPanel(!panel)}>
              <span>Legenda i slojevi</span><span aria-hidden="true">{panel ? '▴' : '▾'}</span>
            </button>
            {panel && (
              <div id="kontrole-sadrzaj">
                <ul className="legenda">
                  {(['A', 'B', 'C', '-'] as const).map((p) => (
                    <li key={p}><span className="znak" style={{ background: BOJA_PRIORITETA[p].bg, color: BOJA_PRIORITETA[p].fg }}>
                      {p === '-' ? '–' : p}</span>{{ A: 'A – najhitniji plan evakuacije', B: 'B – povišen prioritet', C: 'C – ograničen izlaz', '-': '6+ izlaza, dovoljno' }[p]}</li>
                  ))}
                  <li><span className="linija ug" />usko grlo: jedina cesta prema van</li>
                  {odabranoN && <>
                    <li><span className="linija pr" />izlazni pravac (broj na crti)</li>
                    <li><span className="linija ugo" />usko grlo odabranog naselja</li>
                    <li><span className="linija dc" />kandidat za drugu cestu</li>
                  </>}
                </ul>
                <p className="sitno">Klikni naselje: karta pokaže njegove izlazne pravce i usko grlo. Veći krug = više ljudi ljeti.</p>
                <details className="slojevi-detalji">
                  <summary>Slojevi na karti</summary>
                  <fieldset className="slojevi">
                    <legend className="sr-only">Indeks opasnosti od požara (EFFIS FWI)</legend>
                    {([['nista', 'bez FWI-ja'], ['danas', 'FWI danas (prognoza)'], ['povijesni', `FWI ${datum13} (Lokva Rogoznica)`]] as [FwiSloj, string][]).map(([v, t]) => (
                      <label key={v}><input type="radio" name="fwi" checked={slojevi.fwi === v}
                        onChange={() => setSlojevi({ ...slojevi, fwi: v })} /> {t}</label>
                    ))}
                  </fieldset>
                  {slojevi.fwi !== 'nista' && (
                    <ul className="legenda fwi">
                      {[['#99e6a8', 'nizak < 11,2'], ['#e8e840', 'umjeren 11,2–21,3'], ['#f0a800', 'visok 21,3–38'],
                        ['#e8000b', 'vrlo visok 38–50'], ['#a50000', 'ekstreman 50–70'], ['#3a0010', 'vrlo ekstreman > 70']].map(([b, t]) => (
                        <li key={t}><span className="kvadrat" style={{ background: b }} />{t}</li>))}
                    </ul>
                  )}
                  <label><input type="checkbox" checked={slojevi.svaGrla}
                    onChange={(e) => setSlojevi({ ...slojevi, svaGrla: e.target.checked })} /> sva uska grla (i ona s 2–5 cesta)</label>
                  <label><input type="checkbox" checked={slojevi.drugeCeste}
                    onChange={(e) => setSlojevi({ ...slojevi, drugeCeste: e.target.checked })} /> svi kandidati za drugu cestu</label>
                  <label><input type="checkbox" checked={slojevi.pozari} disabled={!podaci.pozari}
                    onChange={(e) => setSlojevi({ ...slojevi, pozari: e.target.checked })} /> opožarene površine 2000.– (EFFIS)</label>
                  <label><input type="checkbox" checked={slojevi.gorivo}
                    onChange={(e) => setSlojevi({ ...slojevi, gorivo: e.target.checked })} /> karta goriva (EFFIS)</label>
                </details>
              </div>
            )}
          </div>
          {odabranoN && (
            <SettlementCard n={odabranoN} ug={ug} scenarij={scenarij} fwiDanas={podaci.fwiDanas}
              fwiPovijesni={podaci.fwiPovijesni} onZatvori={() => odaberi(null)} />
          )}
        </main>
      )}
      {ekran === 'lista' && (
        <main><PriorityList naselja={naselja} scenarij={scenarij} onOdaberi={(id) => idi('karta', id)} /></main>
      )}
      {ekran === 'izvori' && <main><SourcesPage meta={podaci.meta} kpi={podaci.kpi} /></main>}
    </div>
  )
}
