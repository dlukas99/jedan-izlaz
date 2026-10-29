import type { Fwi, Naselje, Scenarij, UskoGrlo } from './types'
import {
  BOJA_PRIORITETA, OPIS_IZVORA, OPIS_PRIORITETA, fmtBroj, fmtDatum, fmtDec, fmtKratkiRaspon, fmtRasponLjudi,
  fmtRasponSati, fmtSati,
} from './format'
import { POVIJESNI_DAN } from './data'
import { BOJA_DRUGE, BOJA_GRLA, BOJA_PRAVCA } from './MapView'

interface Props {
  n: Naselje
  ug: UskoGrlo | null
  scenarij: Scenarij
  fwiDanas: Fwi | null
  fwiPovijesni: Fwi | null
  onZatvori: () => void
}

const NAZIV_SCENARIJA: Record<Scenarij, string> = { opt: 'optimistični', sred: 'središnji', pes: 'pesimistični' }

function Izvor({ k }: { k: string[] }) {
  return <span className="izvor">Izvor: {k.map((x) => OPIS_IZVORA[x] ?? x).join('; ')}</span>
}

/** Jedna brojka u sažetku: velika vrijednost odabranog scenarija, ispod raspon i izvor. */
function Brojka({ naslov, vrijednost, raspon, izvor }: {
  naslov: string; vrijednost: React.ReactNode; raspon?: string; izvor: string[]
}) {
  return (
    <div className="brojka">
      <span className="brojka-naslov">{naslov}</span>
      <span className="brojka-vrijednost">{vrijednost}</span>
      {raspon && <span className="brojka-raspon">{raspon}</span>}
      <Izvor k={izvor} />
    </div>
  )
}

function Redak({ naslov, vrijednost, izvor, children }: {
  naslov: string; vrijednost: React.ReactNode; izvor?: string[]; children?: React.ReactNode
}) {
  return (
    <div className="redak">
      <dt>{naslov}</dt>
      <dd>
        <span className="vrijednost">{vrijednost}</span>
        {children}
        {izvor && <Izvor k={izvor} />}
      </dd>
    </div>
  )
}

/** Glavna poruka kartice u jednoj rečenici — ono što stožer mora vidjeti u prve dvije sekunde. */
function poruka(n: Naselje): { naslov: string; tekst: string; razina: 'kriticno' | 'upozorenje' | 'ok' } {
  if (n.klasa_izlaza === 'E0') {
    return n.samo_putovi
      ? { naslov: 'Nema vozive ceste', tekst: 'Do naselja vode samo šumski ili poljski putovi.', razina: 'kriticno' }
      : { naslov: 'Nema cestovnog izlaza', tekst: 'Evakuacija je moguća samo morem.', razina: 'kriticno' }
  }
  if (n.klasa_izlaza === 'E1') return { naslov: 'Samo jedan cestovni izlaz', tekst: 'Ako se ta cesta zatvori, nema drugog puta kopnom.', razina: 'kriticno' }
  if (n.klasa_izlaza === 'E6+') return { naslov: '6 ili više cestovnih izlaza', tekst: 'Dovoljno neovisnih pravaca (prag ≈ 6, PNAS 2026.).', razina: 'ok' }
  return { naslov: `${n.izlazi_e} neovisna cestovna izlaza`, tekst: 'Ograničen broj pravaca — ispod praga od 6.', razina: 'upozorenje' }
}

export default function SettlementCard({ n, ug, scenarij, fwiDanas, fwiPovijesni, onZatvori }: Props) {
  const boja = BOJA_PRIORITETA[n.prioritet]
  const fwiRazred = (f: Fwi | null) => (f && f.vrijednosti[n.id] != null ? f.razredi[n.id] ?? '–' : 'nema podatka')
  const t = n.t_evak_h
  const ljudi = n.ljudi_iza_reza ?? n.p_ljeto
  const p = poruka(n)
  const pravci = n.izlazni_pravci ?? []
  const ostali = ug ? ug.naselja_iza_nazivi.filter((x) => x !== n.naziv) : []
  const naslovLjudi = n.klasa_izlaza === 'E0' ? 'Ljeti na otoku / iza' : n.ljudi_iza_reza ? 'Ljeti iza uskog grla' : 'Ljeti u naselju'

  return (
    <aside className="kartica" aria-labelledby="kartica-naslov">
      <header className="kartica-zaglavlje">
        <div>
          <h2 id="kartica-naslov">{n.naziv}</h2>
          <p className="podnaslov">{n.jls} · <span className="znacka mala-znacka" style={{ background: boja.bg, color: boja.fg }}>
            prioritet {n.prioritet === '-' ? '–' : n.prioritet}</span></p>
        </div>
        <button className="zatvori" onClick={onZatvori} aria-label="Zatvori karticu naselja">×</button>
      </header>

      <div className={`poruka-izlaza ${p.razina}`}>
        <span className="poruka-broj" aria-hidden="true">{n.klasa_izlaza === 'E0' ? '0' : n.izlazi_e >= 6 ? '6+' : n.izlazi_e}</span>
        <div>
          <strong>{p.naslov}</strong>
          <span>{p.tekst}</span>
        </div>
      </div>

      <div className="brojke">
        <Brojka naslov={naslovLjudi} vrijednost={fmtBroj(ljudi[scenarij])}
          raspon={`raspon ${fmtKratkiRaspon(ljudi, fmtBroj)} ljudi`}
          izvor={['dzs_popis_naselja', 'dzs_turizam_2025']} />
        {t ? (
          <Brojka naslov="Evakuacija cestom" vrijednost={fmtSati(t[scenarij])}
            raspon={`raspon ${fmtKratkiRaspon(t, fmtSati)}`} izvor={['osm', 'dzs_turizam_2025']} />
        ) : (
          <Brojka naslov="Evakuacija cestom" vrijednost={n.klasa_izlaza === 'E0' ? 'samo morem' : 'bez uskog grla'}
            raspon={n.klasa_izlaza === 'E0' ? (n.trajektna_linija ?? 'brodska linija nije upisana') : '6+ neovisnih pravaca'}
            izvor={n.trajektna_linija ? ['jadrolinija'] : ['osm']} />
        )}
        <Brojka naslov="Opasnost od požara" vrijednost={n.h_razred ?? '–'}
          raspon={`relativno u županiji · ${fmtDatum(POVIJESNI_DAN)}: ${fwiRazred(fwiPovijesni)}`}
          izvor={['worldcover', 'effis_ba', 'effis_fwi']} />
        <Brojka naslov="Stalni stanovnici" vrijednost={fmtBroj(n.stanovnici_2021)}
          raspon={`od toga 65+: ${fmtBroj(n.stanovnici_65plus)}`} izvor={['dzs_popis_naselja']} />
      </div>
      <p className="sitno">Brojke su za <strong>{NAZIV_SCENARIJA[scenarij]}</strong> scenarij (promijeni gore desno).</p>

      {n.napomene.length > 0 && (
        <ul className="napomene" aria-label="Napomene">{n.napomene.map((x) => <li key={x}>{x}</li>)}</ul>
      )}

      <section className="odjeljak" aria-labelledby="pravci-naslov">
        <h3 id="pravci-naslov">Na karti</h3>
        <ul className="na-karti">
          {pravci.length > 0 ? pravci.map((x) => (
            <li key={x.redni}>
              <span className="pravac-broj" style={{ borderColor: BOJA_PRAVCA, color: BOJA_PRAVCA }}>{x.redni}</span>
              <span><strong>Izlazni pravac {x.redni}</strong>: {x.ceste.length ? x.ceste.slice(0, 4).join(' → ') : 'nerazvrstane ceste'}
                {x.ceste.length > 4 ? ' → …' : ''} · {fmtDec(x.km)} km do {x.kraj === 'autocesta' ? 'autoceste' : 'izlaza iz županije'}</span>
            </li>
          )) : (
            <li><span className="pravac-broj" aria-hidden="true">0</span>
              <span><strong>Nema cestovnog pravca</strong> do kopnene mreže{n.trajektna_linija ? ` — brodska linija: ${n.trajektna_linija}` : ''}.</span></li>
          )}
          {ug && (
            <li>
              <span className="linija-znak" style={{ background: BOJA_GRLA }} aria-hidden="true" />
              <span><strong>Usko grlo</strong>: {[ug.cesta_ref, ug.naziv].filter(Boolean).join(' ') || 'cesta bez oznake'}
                {' '}({ug.broj_izlaza === 1 ? 'jedini prolaz' : `${ug.broj_izlaza} ceste u rezu`}
                {ug.pokretni_most ? ', pokretni most' : ug.most ? ', most' : ''}).
                {ostali.length > 0 && <> Iza njega su i: {ostali.slice(0, 6).join(', ')}
                  {ostali.length > 6 ? ` i još ${ostali.length - 6}` : ''}.</>}</span>
            </li>
          )}
          {n.druga_cesta_km != null && (
            <li>
              <span className="linija-znak isprekidano" style={{ color: BOJA_DRUGE }} aria-hidden="true" />
              <span><strong>Kandidat za drugu cestu</strong>: {fmtDec(n.druga_cesta_km)} km mimo uskog grla,
                {' '}{fmtDec((n.druga_cesta_udio_track ?? 0) * 100)} % po šumskim/poljskim putovima — prohodnost provjeriti na terenu.</span>
            </li>
          )}
        </ul>
        <Izvor k={['osm']} />
      </section>

      <details className="detalji">
        <summary>Kako je izračunato (formule, izvori, svi scenariji)</summary>
        <p className="opis-prioriteta">{OPIS_PRIORITETA[n.prioritet]}.</p>
        <dl>
          <Redak naslov="Izlazni cestovni pravci" vrijednost={`${n.izlazi_e === 6 ? '6 ili više' : n.izlazi_e} (${n.klasa_izlaza})`}
            izvor={['osm']}>
            <span className="objasnjenje">Broj neovisnih cestovnih putova (bez zajedničke dionice) do mreže izvan županije
              ili autoceste — minimalni rez grafa; prag ≈ 6 prema Fong i sur., PNAS 2026.</span>
          </Redak>
          <Redak naslov="Ljudi ljeti u naselju" vrijednost={fmtRasponLjudi(n.p_ljeto)}
            izvor={['dzs_popis_naselja', 'dzs_turizam_2025', 'dzs_stanovi', 'dzs_popunjenost_2025_08', 'osm']}>
            <span className="objasnjenje">Stanovnici + stalne postelje JLS-a ({fmtBroj(n.postelje_jls)}) × popunjenost
              + stanovi za odmor ({fmtBroj(n.stanovi_odmor_jls)}) × osoba po stanu, × udio naselja {fmtDec(n.udio_naselja * 100)} %
              ({n.udio_metoda === 'osm_turisticki_objekti' ? 'po OSM turističkim objektima' : 'po broju stanovnika'}).</span>
          </Redak>
          {n.ljudi_iza_reza && (
            <Redak naslov={n.klasa_izlaza === 'E0' ? 'Ljudi ljeti na istom otoku' : 'Ljudi ljeti iza uskog grla'}
              vrijednost={fmtRasponLjudi(n.ljudi_iza_reza)} izvor={['dzs_popis_naselja', 'dzs_turizam_2025', 'osm']} />
          )}
          {t && (
            <Redak naslov="Vrijeme evakuacije cestom" vrijednost={fmtRasponSati(t)} izvor={['dzs_turizam_2025', 'osm']}>
              <span className="objasnjenje">Ljudi iza uskog grla ÷ osoba po vozilu ÷ kapacitet
                ({fmtBroj(ug?.kapacitet_voz_h[scenarij])} voz/h u odabranom scenariju, jedna traka u izlaznom smjeru).</span>
            </Redak>
          )}
          {ug?.pldp && (
            <Redak naslov="Izmjereni ljetni promet (PLDP)" vrijednost={`${fmtBroj(ug.pldp.vrijednost)} vozila/dan`}
              izvor={['hc_brojenje_2025']}>
              <span className="objasnjenje">Brojilo {ug.pldp.brojilo} „{ug.pldp.naziv}“, {ug.pldp.godina}. — prosječni ljetni dnevni promet.</span>
            </Redak>
          )}
          <Redak naslov="Statička opasnost od požara"
            vrijednost={n.h_razred ? `${n.h_razred} (H = ${fmtDec((n.h_stat ?? 0) * 100)} / 100)` : 'nema podatka'}
            izvor={['worldcover', 'effis_ba']}>
            <span className="objasnjenje">Relativno unutar županije. Gorivo (šuma, grmlje, trava) u krugu 2 km:
              {' '}{n.h_gorivo != null ? `${fmtDec(n.h_gorivo * 100)} %` : '–'}; izgorjelo u krugu 5 km od 2000.:
              {' '}{n.h_pozari_udio != null ? `${fmtDec(n.h_pozari_udio * 100)} %` : '–'}
              {n.h_podloznost != null && <>; modelirana podložnost terena u krugu 5 km: {fmtDec(n.h_podloznost * 100)} %
                (vjerojatnost da ćelija od 250 m izgori, model D11)</>}.</span>
          </Redak>
          <Redak naslov="Indeks vremenske opasnosti (FWI)"
            vrijednost={`danas: ${fwiRazred(fwiDanas)}; ${fmtDatum(POVIJESNI_DAN)}: ${fwiRazred(fwiPovijesni)}`}
            izvor={['effis_fwi']}>
            <span className="objasnjenje">Dnevna prognoza EFFIS-a (razlučivost ~8 km), ne prikazuje gdje požar trenutno gori.</span>
          </Redak>
        </dl>
      </details>

      <p className="odricanje-mali">Alat za planiranje, ne za uzbunjivanje. U opasnosti slijedite upute 112 i civilne zaštite.</p>
    </aside>
  )
}
