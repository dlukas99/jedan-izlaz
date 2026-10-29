import type { Kpi, Meta } from './types'
import { fmtBroj, fmtDatum as datum } from './format'

export default function SourcesPage({ meta, kpi }: { meta: Meta; kpi: Kpi | null }) {
  const s = meta.scenariji as Record<string, Record<string, number>>
  return (
    <section className="stranica" aria-labelledby="izvori-naslov">
      <h2 id="izvori-naslov">Izvori i metoda</h2>
      <p className="uvod">Podaci generirani {datum(meta.generirano)} (način: <code>{meta.nacin}</code>)
        {meta.zupanija ? `, pilot: ${meta.zupanija} županija` : ''}. Svi izvori su otvoreni podaci javnog sektora ili otvorene licence.</p>

      {kpi && (
        <div className="kpi">
          <div><strong>{fmtBroj(kpi.naselja_po_klasi.E0 ?? 0)}</strong><span>naselja bez cestovnog izlaza (E0)</span></div>
          <div><strong>{fmtBroj(kpi.naselja_po_klasi.E1 ?? 0)}</strong><span>naselja s jednim izlazom (E1)</span></div>
          <div><strong>{fmtBroj(kpi.ljudi_ljeti_u_naseljima_E1.opt)}–{fmtBroj(kpi.ljudi_ljeti_u_naseljima_E1.pes)}</strong>
            <span>ljudi ljeti u naseljima s jednim izlazom</span></div>
          <div><strong>{fmtBroj(kpi.naselja_po_prioritetu.A ?? 0)}</strong><span>naselja prioriteta A</span></div>
        </div>
      )}

      <h3>Skupovi podataka</h3>
      <div className="tablica-omot" tabIndex={0} role="region" aria-label="Tablica izvora">
        <table>
          <thead><tr><th scope="col">Skup</th><th scope="col">Izdavač</th><th scope="col">Licenca</th><th scope="col">Dohvaćeno</th></tr></thead>
          <tbody>
            {meta.izvori.map((z) => {
              const url = z.url_paketa ?? z.url
              return (
                <tr key={z.kljuc}>
                  <td>{url ? <a href={url} target="_blank" rel="noreferrer">{z.naziv}</a> : z.naziv}<br /><small>{z.navod}</small></td>
                  <td>{z.izdavac}</td><td>{z.licenca}</td><td>{datum(z.dohvaceno)}</td>
                </tr>
              )
            })}
          </tbody>
        </table>
      </div>

      <h3>Kako računamo</h3>
      <ol className="metoda">
        <li><strong>Cestovna mreža</strong> je graf vozivih cesta iz OpenStreetMapa za županiju i 15 km oko nje.
          Trajekti nisu dio grafa. <em>Sigurna mreža</em> su ceste izvan županije i autocesta — to znači „izvan županije
          ili na autocesti“, a ne „izvan dosega požara“.</li>
        <li><strong>Broj izlaza</strong> je broj cestovnih putova od jezgre naselja do sigurne mreže koji ne dijele nijednu
          dionicu (maksimalni tok = minimalni rez, Mengerov teorem), do 6. Prag od oko 6 izlaza slijedi
          Fong i sur., <em>PNAS</em> 2026. (342 smrtna slučaja u požarima u SAD-u). Minimalni rez je <em>usko grlo</em>.</li>
        <li><strong>Ljudi ljeti</strong> = stanovnici 2021. + stalne postelje JLS-a × popunjenost
          ({s.popunjenost_stalnih_postelja?.opt}/{s.popunjenost_stalnih_postelja?.sred}/{s.popunjenost_stalnih_postelja?.pes})
          × udio naselja + stanovi za odmor × osoba po stanu
          ({s.osoba_po_stanu_za_odmor?.opt}/{s.osoba_po_stanu_za_odmor?.sred}/{s.osoba_po_stanu_za_odmor?.pes}) × udio naselja.
          Nautički turizam i dnevni posjetitelji nisu uključeni.</li>
        <li><strong>Vrijeme evakuacije</strong> = ljudi iza uskog grla ÷ osoba po vozilu
          ({s.osoba_po_vozilu?.opt}/{s.osoba_po_vozilu?.sred}/{s.osoba_po_vozilu?.pes}) ÷ kapacitet jedne trake
          ({s.kapacitet_trake_voz_h?.opt}/{s.kapacitet_trake_voz_h?.sred}/{s.kapacitet_trake_voz_h?.pes} vozila/h,
          niže klase ceste × 0,6). Uvijek raspon optimistično–pesimistično.</li>
        <li><strong>Statička opasnost</strong> H = 0,6 × udio goriva (WorldCover: šuma, grmlje, trava) u krugu 2 km
          + 0,4 × podložnost požaru u krugu 5 km (normirano). Podložnost daje model strojnog učenja (gradient boosting)
          naučen na EFFIS opožarenim površinama 2000.–danas u 7 obalnih županija (mreža 250 m; prostorna
          provjera po blokovima od 10 km: ROC-AUC 0,78, bolji od logističke regresije 0,75). Razredi su tercili
          unutar županije.</li>
        <li><strong>Dnevna opasnost</strong>: EFFIS Fire Weather Index (sloj mf010.fwi), razredi iz EFFIS legende.
          Povijesni dan 13.8.2026. je dan požara kod Lokve Rogoznice.</li>
        <li><strong>Prioritet</strong> A: jedan ili nijedan izlaz, visoka opasnost i (izlaz morem ili evakuacija ≥ 1 h);
          B: jedan ili nijedan izlaz i (srednja opasnost ili evakuacija &gt; 3 h), ili 2–5 izlaza, visoka opasnost i &gt; 3 h;
          C: ostala naselja s manje od 6 izlaza.</li>
        <li><strong>Druga cesta</strong>: najkraći put do sigurne mreže mimo uskog grla, smije koristiti i šumske/poljske
          putove — kandidat, prohodnost treba provjeriti na terenu.</li>
      </ol>
      <p>Konstante s oznakom „pretpostavka“ i analiza osjetljivosti opisani su u
        {' '}<a href="https://github.com/dlukas99/jedan-izlaz/blob/main/docs/metodologija.md">docs/metodologija.md</a>.
        Kod je otvoren (EUPL-1.2): <a href="https://github.com/dlukas99/jedan-izlaz">github.com/dlukas99/jedan-izlaz</a>.
        Izvedeni podaci s OSM geometrijom: ODbL 1.0. Sadrži podatke Državne geodetske uprave.</p>
      <p><strong>{meta.odricanje}</strong></p>
    </section>
  )
}
