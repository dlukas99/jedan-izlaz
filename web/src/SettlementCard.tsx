import type { Fwi, Naselje, Scenarij, UskoGrlo } from './types'
import {
  BOJA_PRIORITETA, OPIS_IZVORA, OPIS_KLASE, OPIS_PRIORITETA, fmtBroj, fmtDatum, fmtDec, fmtRasponLjudi,
  fmtRasponSati, fmtSati,
} from './format'
import { POVIJESNI_DAN } from './data'

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

export default function SettlementCard({ n, ug, scenarij, fwiDanas, fwiPovijesni, onZatvori }: Props) {
  const boja = BOJA_PRIORITETA[n.prioritet]
  const fwi = (f: Fwi | null) => (f && f.vrijednosti[n.id] != null
    ? `${fmtDec(f.vrijednosti[n.id])} (${f.razredi[n.id]})` : 'nema podatka')
  const t = n.t_evak_h
  return (
    <aside className="kartica" aria-labelledby="kartica-naslov">
      <header className="kartica-zaglavlje">
        <div>
          <h2 id="kartica-naslov">{n.naziv}</h2>
          <p className="podnaslov">{n.jls} · {n.zupanija} županija</p>
        </div>
        <button className="zatvori" onClick={onZatvori} aria-label="Zatvori karticu naselja">×</button>
      </header>

      <div className="znacke">
        <span className="znacka" style={{ background: boja.bg, color: boja.fg }}>
          Prioritet {n.prioritet === '-' ? '–' : n.prioritet}
        </span>
        <span className={`znacka klasa klasa-${n.klasa_izlaza.replace('+', 'p')}`}>
          {n.klasa_izlaza} · {n.izlazi_e === 6 ? '6+' : n.izlazi_e} {n.izlazi_e === 1 ? 'izlaz' : 'izlaza'}
        </span>
      </div>
      <p className="opis-prioriteta">{OPIS_PRIORITETA[n.prioritet]}.{' '}
        {n.samo_putovi ? 'Nema vozive ceste – do naselja vode samo šumski/poljski putovi.' : `${OPIS_KLASE[n.klasa_izlaza]}.`}</p>

      <dl>
        <Redak naslov="Izlazni cestovni pravci" vrijednost={`${n.izlazi_e === 6 ? '6 ili više' : n.izlazi_e}`}
          izvor={['osm']}>
          <span className="objasnjenje">Broj neovisnih cestovnih putova (bez zajedničkog dijela) do mreže izvan županije
            ili autoceste — minimalni rez grafa, prag ≈ 6 prema Fong i sur., PNAS 2026.</span>
        </Redak>

        {n.klasa_izlaza === 'E0' && !n.samo_putovi && (
          <Redak naslov="Izlaz morem" vrijednost={n.trajektna_linija ?? 'brodska linija nije upisana'}
            izvor={n.trajektna_linija ? ['jadrolinija'] : undefined} />
        )}

        {ug && (
          <Redak naslov="Usko grlo" vrijednost={[ug.cesta_ref, ug.naziv].filter(Boolean).join(' – ') || 'cesta bez imena'}
            izvor={['osm']}>
            <span className="objasnjenje">
              {ug.broj_izlaza === 1 ? 'Jedini cestovni prolaz' : `${ug.broj_izlaza} ceste u minimalnom rezu`}
              {ug.pokretni_most ? '; pokretni most' : ug.most ? '; most' : ''}
              {ug.pokretni_most_iza && !ug.pokretni_most ? '; prije njega je još i pokretni most' : ''}.{' '}
              Iza njega: {ug.naselja_iza_nazivi.slice(0, 8).join(', ')}
              {ug.naselja_iza_nazivi.length > 8 ? ` i još ${ug.naselja_iza_nazivi.length - 8}` : ''}.
            </span>
          </Redak>
        )}

        <Redak naslov="Stalni stanovnici (2021.)" vrijednost={`${fmtBroj(n.stanovnici_2021)} (od toga 65+: ${fmtBroj(n.stanovnici_65plus)})`}
          izvor={['dzs_popis_naselja']} />
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
          <Redak naslov="Vrijeme evakuacije cestom" vrijednost={fmtRasponSati(t)}
            izvor={['dzs_turizam_2025', 'osm']}>
            <span className="objasnjenje">Odabrani ({NAZIV_SCENARIJA[scenarij]}) scenarij: <strong>{fmtSati(t[scenarij])}</strong>.
              Ljudi iza uskog grla ÷ osoba po vozilu ÷ kapacitet ({fmtBroj(ug?.kapacitet_voz_h[scenarij])} voz/h, jedna traka).</span>
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
            {' '}{n.h_pozari_udio != null ? `${fmtDec(n.h_pozari_udio * 100)} %` : '–'}.</span>
        </Redak>
        <Redak naslov="Indeks vremenske opasnosti (FWI)"
          vrijednost={`danas: ${fwi(fwiDanas)}; ${fmtDatum(POVIJESNI_DAN)}: ${fwi(fwiPovijesni)}`}
          izvor={['effis_fwi']} />
        {n.druga_cesta_km != null && (
          <Redak naslov="Kandidat za drugu cestu" vrijednost={`${fmtDec(n.druga_cesta_km)} km`} izvor={['osm']}>
            <span className="objasnjenje">Najkraći put do sigurne mreže mimo uskog grla, od toga
              {' '}{fmtDec((n.druga_cesta_udio_track ?? 0) * 100)} % po šumskim/poljskim putovima.
              <strong> Kandidat – prohodnost provjeriti na terenu.</strong></span>
          </Redak>
        )}
      </dl>

      {n.napomene.length > 0 && (
        <ul className="napomene">{n.napomene.map((x) => <li key={x}>{x}</li>)}</ul>
      )}
      <p className="odricanje-mali">Alat za planiranje, ne za uzbunjivanje. U opasnosti slijedite upute 112 i civilne zaštite.</p>
    </aside>
  )
}
