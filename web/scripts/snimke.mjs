// Snimke zaslona za dokumentaciju i provjeru UI-ja: node scripts/snimke.mjs <url> <izlazni-dir>
import { chromium } from 'playwright'
import { mkdirSync } from 'node:fs'

const url = process.argv[2] ?? 'http://localhost:4173/jedan-izlaz/'
const dir = process.argv[3] ?? '../docs/snimke'
mkdirSync(dir, { recursive: true })
// SwiftShader: headless Chromium inače nema WebGL pa MapLibre ne crta kartu.
const browser = await chromium.launch({ args: ['--use-angle=swiftshader', '--enable-unsafe-swiftshader', '--ignore-gpu-blocklist'] })
const greske = []
async function snimi(ime, hash, { sirina = 1440, visina = 900, cekaj = 3500, akcija } = {}) {
  const p = await browser.newPage({ viewport: { width: sirina, height: visina } })
  p.on('pageerror', (e) => greske.push(`${ime}: ${e.message}`))
  p.on('console', (m) => { if (m.type() === 'error') greske.push(`${ime}: ${m.text()}`) })
  await p.goto(url + hash, { waitUntil: 'networkidle' })
  if (akcija) await akcija(p)
  await p.waitForTimeout(cekaj)
  await p.screenshot({ path: `${dir}/${ime}.png` })
  await p.close()
}
await snimi('01-karta', '#karta')
await snimi('02-murter', '#karta/naselje/042501')
await snimi('03-zlarin', '#karta/naselje/073369')
await snimi('04-fwi-13-8', '#karta/naselje/022446', {
  akcija: async (p) => { await p.getByText('Slojevi na karti').click(); await p.getByLabel(/FWI 13\. 8\./).check() },
})
await snimi('09-trazilica', '#karta', { cekaj: 800, akcija: (p) => p.getByRole('combobox').fill('ice') })
await snimi('05-lista', '#lista', { cekaj: 800 })
await snimi('06-izvori', '#izvori', { cekaj: 800 })
await snimi('07-mobitel-murter', '#karta/naselje/042501', { sirina: 390, visina: 844 })
await snimi('08-mobitel-lista', '#lista', { sirina: 390, visina: 844, cekaj: 800 })
await browser.close()
console.log(greske.length ? 'GREŠKE:\n' + greske.join('\n') : 'Bez grešaka u konzoli.')
