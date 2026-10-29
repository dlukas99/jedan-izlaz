import { useId, useMemo, useRef, useState } from 'react'
import type { Naselje } from './types'
import { BOJA_PRIORITETA, zaPretragu } from './format'

interface Props {
  naselja: Naselje[]
  onOdaberi: (id: string) => void
}

/** Tražilica naselja (ARIA combobox): tipkaš dio imena, strelicama biraš, Enter otvara naselje.
 *  Pretraga ne gleda kvačice („icevo“ nađe Ićevo), a traži i po općini/gradu. */
export default function Trazilica({ naselja, onOdaberi }: Props) {
  const [upit, setUpit] = useState('')
  const [otvoreno, setOtvoreno] = useState(false)
  const [aktivno, setAktivno] = useState(0)
  const ulaz = useRef<HTMLInputElement>(null)
  const idListe = useId()

  const indeks = useMemo(() => naselja.map((n) => ({ n, k: zaPretragu(n.naziv), j: zaPretragu(n.jls) })), [naselja])
  const rezultati = useMemo(() => {
    const q = zaPretragu(upit.trim())
    if (!q) return []
    // Prvo naselja kojima ime počinje upitom, zatim ona koja ga sadrže, pa podudaranja po općini.
    const ocjena = (x: (typeof indeks)[number]) =>
      x.k.startsWith(q) ? 0 : x.k.includes(q) ? 1 : x.j.includes(q) ? 2 : 9
    return indeks.map((x) => ({ ...x, o: ocjena(x) })).filter((x) => x.o < 9)
      .sort((a, b) => a.o - b.o || a.n.naziv.localeCompare(b.n.naziv, 'hr')).slice(0, 8).map((x) => x.n)
  }, [upit, indeks])

  const odaberi = (n: Naselje) => {
    onOdaberi(n.id)
    setUpit('')
    setOtvoreno(false)
    ulaz.current?.blur()
  }

  return (
    <div className="trazilica">
      <label htmlFor={`${idListe}-ulaz`} className="sr-only">Pronađi naselje</label>
      <span className="trazilica-ikona" aria-hidden="true">⌕</span>
      <input
        id={`${idListe}-ulaz`} ref={ulaz} type="search" autoComplete="off" spellCheck={false}
        placeholder="Upiši naselje, npr. Murter"
        role="combobox" aria-expanded={otvoreno && rezultati.length > 0} aria-controls={idListe}
        aria-autocomplete="list"
        aria-activedescendant={otvoreno && rezultati[aktivno] ? `${idListe}-${rezultati[aktivno].id}` : undefined}
        value={upit}
        onChange={(e) => { setUpit(e.target.value); setOtvoreno(true); setAktivno(0) }}
        onFocus={() => setOtvoreno(true)}
        onBlur={() => setTimeout(() => setOtvoreno(false), 150)}
        onKeyDown={(e) => {
          if (e.key === 'ArrowDown') { e.preventDefault(); setAktivno((a) => Math.min(a + 1, rezultati.length - 1)) }
          else if (e.key === 'ArrowUp') { e.preventDefault(); setAktivno((a) => Math.max(a - 1, 0)) }
          else if (e.key === 'Enter' && rezultati[aktivno]) { e.preventDefault(); odaberi(rezultati[aktivno]) }
          else if (e.key === 'Escape') { setUpit(''); setOtvoreno(false) }
        }}
      />
      {otvoreno && upit.trim() !== '' && (
        <ul id={idListe} role="listbox" className="trazilica-lista" aria-label="Pronađena naselja">
          {rezultati.length === 0 && <li className="trazilica-nema" role="presentation">Nema takvog naselja u županiji</li>}
          {rezultati.map((n, i) => {
            const b = BOJA_PRIORITETA[n.prioritet]
            return (
              <li key={n.id} id={`${idListe}-${n.id}`} role="option" aria-selected={i === aktivno}
                className={i === aktivno ? 'aktivno' : ''}
                onMouseDown={(e) => { e.preventDefault(); odaberi(n) }} onMouseEnter={() => setAktivno(i)}>
                <span className="znak" style={{ background: b.bg, color: b.fg }} aria-hidden="true">
                  {n.prioritet === '-' ? '–' : n.prioritet}</span>
                <span className="trazilica-ime"><strong>{n.naziv}</strong> <span>{n.jls}</span></span>
                <span className="trazilica-klasa">{n.klasa_izlaza === 'E0' ? 'samo morem'
                  : n.izlazi_e >= 6 ? '6+ izlaza' : `${n.izlazi_e} ${n.izlazi_e === 1 ? 'izlaz' : 'izlaza'}`}</span>
              </li>
            )
          })}
        </ul>
      )}
    </div>
  )
}
