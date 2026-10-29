# Izvješće probe izvora

Generirano: 2026-10-28T20:28:51 naredbom `python -m etl.probe`.
Sirovi odgovori su u `data/raw/<izvor>_probe/` (nisu u gitu).

| Izvor | URL | HTTP | Veličina | Nalaz | Status |
|---|---|---|---|---|---|
| CKAN dzs_popis | https://data.gov.hr/ckan/api/3/action/package_show?id=statistika-u-nizu-popis-stanovnistva-kucanstava-i-stanova-2021 | 200 | 7 | izdavač=Državni zavod za statistiku; licenca=Otvorena dozvola (OD); metadata_modified=2026-07-16T11:55:08.447686; resursi: Stanovništvo po naseljima [XLSX]; Stanovništvo po gradovima i općinama [XLSX]; Stanovništvo po županijama [XLSX]; Stanovništvo - Republika Hrvatska [XLSX]; Stanovništvo - najveći gradovi, općine i naselja [XLSX]; Stanovništvo - zbirni pregledi [XLSX]; Podaci iz prošlih popisa [XLSX] | OK |
| CKAN dzs_stanovi | https://data.gov.hr/ckan/api/3/action/package_show?id=statistika-u-nizu-popis-stanovnistva-kucanstava-i-stanova-2021-stambene-jedinice | 200 | 3 | izdavač=Državni zavod za statistiku; licenca=Otvorena dozvola (OD); metadata_modified=2026-04-15T19:07:04.688217; resursi: Popis 2021. - stambene jedince po gradovima i općinama [XLSX]; Popis 2021. - stambene jedince po županijama [XLSX]; Popis 2021. - stambene jedinice - Republika Hrvatska [XLSX] | OK |
| CKAN dzs_gradovi | https://data.gov.hr/ckan/api/3/action/package_show?id=statistika-u-nizu-gradovi-u-statistici | 200 | 1 | izdavač=Državni zavod za statistiku; licenca=Otvorena dozvola (OD); metadata_modified=2026-04-15T19:07:56.811071; resursi: ? [xlsx ] | OK |
| CKAN dzs_turizam_niz | https://data.gov.hr/ckan/api/3/action/package_show?id=statistika-u-nizu-turizam | 200 | 2 | izdavač=Državni zavod za statistiku; licenca=None; metadata_modified=2026-04-15T19:07:55.247091; resursi: ? [xlsx ]; ? [xlsx ] | OK |
| CKAN hc_brojenje_2025 | https://data.gov.hr/ckan/api/3/action/package_show?id=brojenje-prometa-na-cestama-republike-hrvatske-godine-2025 | 200 | 1 | izdavač=Hrvatske ceste d.o.o.; licenca=Otvorena dozvola (OD); metadata_modified=2026-09-15T14:13:49.403908; resursi: Brojenje prometa na cestama Republike Hrvatske godine 2025. [csv, xsl] | OK |
| CKAN hc_brojenje_2024 | https://data.gov.hr/ckan/api/3/action/package_show?id=brojenje-prometa-na-cestama-republike-hrvatske-godine-2024 | 200 | 1 | izdavač=Hrvatske ceste d.o.o.; licenca=Otvorena dozvola (OD); metadata_modified=2026-09-15T14:13:02.320858; resursi: Brojenje prometa na cestama Republike Hrvatske godine 2024. [ZIP] | OK |
| CKAN dgu_au | https://data.gov.hr/ckan/api/3/action/package_show?id=upravne-jedinice-inspire | 200 | 3 | izdavač=Državna geodetska uprava; licenca=Otvorena dozvola (OD); metadata_modified=2026-10-22T06:48:05.491626; resursi: DGU usluga preuzimanja - ATOM INSPIRE [atom]; Upravne jedinice – WMS INSPIRE (anonimni korisnici) [web map service (wms)]; Upravne jedinice – WMS INSPIRE (registrirani korisnici) [web map service (wms)] | OK |
| CKAN dgu_rgi | https://data.gov.hr/ckan/api/3/action/package_show?id=registar-geografskih-imena | 200 | 1 | izdavač=Državna geodetska uprava; licenca=Otvorena dozvola (OD); metadata_modified=2026-10-22T06:52:44.706110; resursi: Registar geografskih imena - WFS [WFS] | OK |
| CKAN dgu_rgi_inspire | https://data.gov.hr/ckan/api/3/action/package_show?id=registar-geografskih-imena-inspire | 200 | 3 | izdavač=Državna geodetska uprava; licenca=Otvorena dozvola (OD); metadata_modified=2026-04-15T19:03:13.274485; resursi: Registar geografskih imena - ATOM INSPIRE [atom]; Registar geografskih imena - WFS INSPIRE [WFS]; Registar geografskih imena - WMS INSPIRE [WMS] | OK |
| CKAN hc_wms | https://data.gov.hr/ckan/api/3/action/package_show?id=mrea-javnih-cesta-rh-wms | - | - | HTTPError: 404 Client Error: NOT FOUND for url: https://data.gov.hr/ckan/api/3/action/package_show?id=mrea-javnih-cesta-rh-wms | GREŠKA |
| HC brojenje 2025 (ZIP) | https://data.gov.hr/ckan/dataset/77fe88a7-5566-48b1-9062-b6061aec3c5c/resource/6a36cb35-329c-4408-ac4a-1d61b2e93e94/download/brojenje-promenta-2025.zip | 200 | 556776 | ZIP: 2 datoteka: ['csv 2025.zip', 'xls 2025.zip'] \| csv 2025.zip: 102516 B (preskočeno) \| xls 2025.zip: 516255 B (preskočeno) | OK |
| dzs_naselja | https://podaci.dzs.hr/media/rqybclnx/popis_2021-stanovnistvo_po_naseljima.xlsx | 200 | 3058869 | list 'Sadrzaj-Contents' (14, 3); list 'Znakovi-Symbols' (9, 3); list '1.' (22010, 29); 'Šibensko-kninska' u '1.' (redak 16205, ukupno 660); 'Murter' u '1.' (redak 16637, ukupno 9); 'Zlarin' u '1.' (redak 16490, ukupno 3); 'Prvić' u '1.' (redak 16514, ukupno 6); 'Krapanj' u '1.' (redak 16448, ukupno 3); '65' u '1.' (redak 7, ukupno 872); list '2.' (62, 26); '65' u '2.' (redak 7, ukupno 22); list 'Metodol obj-Notes on methodolo' (35, 3) | OK |
| dzs_jls | https://podaci.dzs.hr/media/td3jvrbu/popis_2021-stanovnistvo_po_gradovima_opcinama.xlsx | 200 | 18279747 | list 'Sadrzaj-Contents' (52, 3); list 'Kratice-Abbreviations' (29, 3); list '1.' (602, 65); 'Šibensko-kninska' u '1.' (redak 384, ukupno 21); 'Tisno' u '1.' (redak 402, ukupno 1); list '2.' (607, 31); 'Šibensko-kninska' u '2.' (redak 384, ukupno 21); 'Tisno' u '2.' (redak 402, ukupno 1); list '3.' (602, 17); 'Šibensko-kninska' u '3.' (redak 384, ukupno 21); 'Tisno' u '3.' (redak 402, ukupno 1); list '4.' (602, 59); 'Šibensko-kninska' u '4.' (redak 384, ukupno 21); 'Tisno' u '4.' (redak 402, ukupno 1); list '5.' (2384, 64); 'Šibensko-kninska' u '5.' (redak 1512, ukupno 84); 'Tisno' u '5.' (redak 1584, ukupno 4); list '6.' (1790, 21); 'Šibensko-kninska' u '6.' (redak 1136, ukupno 63); 'Tisno' u '6.' (redak 1190, ukupno 3); list '7.' (606, 15); 'Šibensko-kninska' u '7.' (redak 384, ukupno 21); 'Tisno' u '7.' (redak 402, ukupno 1); list '8.' (24965, 20); 'Šibensko-kninska' u '8.' (redak 1580 | OK |
| dzs_stanovi | https://podaci.dzs.hr/media/ryynjuzk/popis-2021-stambene-jedinice-po-gradovima-i-opcinama.xlsx | 200 | 477084 | list 'Sadrzaj-Contents' (18, 3); list 'Kratice-Abbreviations' (17, 3); list '1.' (1196, 13); 'odmor' u '1.' (redak 7, ukupno 1); 'Tisno' u '1.' (redak 796, ukupno 2); 'Šibensko-kninska' u '1.' (redak 760, ukupno 42); list '2.' (609, 17); 'Tisno' u '2.' (redak 402, ukupno 1); 'Šibensko-kninska' u '2.' (redak 384, ukupno 21); list '3.' (1196, 21); 'Tisno' u '3.' (redak 796, ukupno 2); 'Šibensko-kninska' u '3.' (redak 760, ukupno 42); list '4.' (1196, 21); 'Tisno' u '4.' (redak 796, ukupno 2); 'Šibensko-kninska' u '4.' (redak 760, ukupno 42); list 'Metodol obj-Notes on methodolo' (99, 3); 'odmor' u 'Metodol obj-Notes on methodolo' (redak 26, ukupno 3) | OK |
| dzs_gradovi | https://podaci.dzs.hr/media/bz5hplcj/gradovi-u-statistici.xlsx | 200 | 3258710 | list 'Sadrzaj-Contents' (100, 3); list 'Kratice-Abbreviations' (18, 3); list 'Tab-1.' (565, 25); 'Tisno' u 'Tab-1.' (redak 386, ukupno 1); list 'Tab-2.' (571, 80); 'Tisno' u 'Tab-2.' (redak 385, ukupno 1); list 'Tab-3.' (573, 125); 'Tisno' u 'Tab-3.' (redak 387, ukupno 1); list 'Tab-4.' (569, 20); 'Tisno' u 'Tab-4.' (redak 385, ukupno 1); list 'Tab-5.' (564, 50); 'Tisno' u 'Tab-5.' (redak 385, ukupno 1); list 'Tab-6.' (566, 64); 'Tisno' u 'Tab-6.' (redak 387, ukupno 1); 'noćenj' u 'Tab-6.' (redak 6, ukupno 1); 'dolas' u 'Tab-6.' (redak 6, ukupno 1); 'turist' u 'Tab-6.' (redak 6, ukupno 1); list 'Tab-7.' (571, 50); 'Tisno' u 'Tab-7.' (redak 387, ukupno 1); list 'Tab-8.' (564, 50); 'Tisno' u 'Tab-8.' (redak 385, ukupno 1); list 'Tab-9.' (564, 50); 'Tisno' u 'Tab-9.' (redak 385, ukupno 1); list 'Tab-10.' (564, 50); 'Tisno' u 'Tab-10.' (redak 385, ukupno 1); list 'Tab-11.' (564, 96); 'Tisno' | OK |
| DZS Turizam u 2025. | https://podaci.dzs.hr/2026/en/122435 | 200 | 2365896 | poveznice na datoteke: 0; xlsx=0; pdf=0; [] | OK |
| HC WFS GetCapabilities | https://geoportal.hrvatske-ceste.hr/inspire/tn-ro/wfs?service=WFS&request=GetCapabilities | 200 | 97028 | tipovi=['hc_inspire_tn-ro:Road', 'hc_inspire_tn-ro:RoadLink', 'hc_inspire_tn-ro:RoadLinkSequence', 'hc_inspire_tn-ro:RoadNode']; CRS=['http://www.opengis.net/def/crs/EPSG/0/3035', 'http://www.opengis.net/def/crs/EPSG/0/3765', 'http://www.opengis.net/def/crs/EPSG/0/4258']; formati=['application/gml+xml; version=3.2', 'gml32', 'text/xml; subtype=gml/3.2'] | OK |
| HC WFS DescribeFeatureType hc_inspire_tn-ro:RoadLink | https://geoportal.hrvatske-ceste.hr/inspire/tn-ro/wfs?service=WFS&version=2.0.0&request=DescribeFeatureType&typeNames=hc_inspire_tn-ro%3ARoadLink | 200 | 1074 | elementi: [] | OK |
| HC WFS GetFeature (Tisno, count=5) | https://geoportal.hrvatske-ceste.hr/inspire/tn-ro/wfs?service=WFS&version=2.0.0&request=GetFeature&typeNames=hc_inspire_tn-ro%3ARoadLink&count=5&bbox=43.79%2C15.62%2C43.81%2C15.66%2Curn%3Aogc%3Adef%3A | 200 | 25555 | RoadLink elemenata: 0; početak: '<?xml version="1.0" encoding="UTF-8"?><wfs:FeatureCollection xmlns:wfs="http://www.opengis.net/wfs/2.0" xmlns:xs="http://www.w3.org/2001/XMLSchema" xmlns:gml="http://www.opengis.net/gml/3.2" xmlns:gn="http://inspire.ec.europa.eu/schemas/gn/4.0" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" x' | GREŠKA |
| HC WFS GetFeature Road (Tisno) | https://geoportal.hrvatske-ceste.hr/inspire/tn-ro/wfs?service=WFS&version=2.0.0&request=GetFeature&typeNames=hc_inspire_tn-ro%3ARoad&count=3&bbox=43.79%2C15.62%2C43.81%2C15.66%2Curn%3Aogc%3Adef%3Acrs% | 200 | 53176 | početak: '<?xml version="1.0" encoding="UTF-8"?><wfs:FeatureCollection xmlns:wfs="http://www.opengis.net/wfs/2.0" xmlns:xs="http://www.w3.org/2001/XMLSchema" xmlns:gml="http://www.opengis.net/gml/3.2" xmlns:gn=' | OK |
| HAC WFS GetCapabilities | https://geoportal.hac.hr/inspire/tn-ro/wfs?service=WFS&request=GetCapabilities&version=2.0.0 | 200 | 100071 | tipovi=['tn-ro:FormOfWay', 'tn-ro:Road', 'tn-ro:RoadLink', 'tn-ro:RoadLinkSequence', 'tn-ro:RoadNode']; CRS=['http://www.opengis.net/def/crs/EPSG/0/3035', 'http://www.opengis.net/def/crs/EPSG/0/3765', 'http://www.opengis.net/def/crs/EPSG/0/4258']; formati=['GML2', 'SHAPE-ZIP', 'application/gml+xml; version=3.2', 'application/json', 'gml3', 'gml32', 'json', 'text/xml; subtype=gml/2.1.2', 'text/xml; subtype=gml/3.1.1', 'text/xml; subtype=gml/3.2'] | OK |
| DGU RGI WFS GetCapabilities | https://rgi.dgu.hr/geoserver/wfshr/wfs?service=WFS&request=GetCapabilities&version=2.0.0 | 200 | 97180 | tipovi=['wfshr:nippimenovanomjesto']; CRS=['urn:ogc:def:crs:EPSG::3765']; formati=['GML2', 'SHAPE-ZIP', 'application/gml+xml; version=3.2', 'application/json', 'gml3', 'gml32', 'json', 'text/xml; subtype=gml/2.1.2', 'text/xml; subtype=gml/3.1.1', 'text/xml; subtype=gml/3.2'] | OK |
| DGU RGI GetFeature wfshr:nippimenovanomjesto | https://rgi.dgu.hr/geoserver/wfshr/wfs?service=WFS&version=2.0.0&request=GetFeature&typeNames=wfshr%3Anippimenovanomjesto&count=5&outputFormat=application%2Fjson&bbox=43.76%2C15.55%2C43.86%2C15.7%2Cur | 200 | 1805 | 5 objekata; svojstva: {'identifikator': 'HRRGIM98317', 'vrstaobiljezja': 'otočić, školj, škoj, školjić, škojić', 'geografskoime': 'Mimonjak', 'jezik': 'Hrvatski', 'status': 'službeno'} | OK |
| DGU Upravne jedinice ATOM | https://geoportal.dgu.hr/services/atom/au/xml | 200 | 2149 | poveznica: 5; ['https://geoportal.dgu.hr/services/atom/au/xml', 'https://geoportal.dgu.hr/services/atom/au/en.xml', 'https://geoportal.dgu.hr/services/atom/xml', 'https://geoportal.dgu.hr/services/atom/INSPIRE_Administrative_Units_(AU).zip'] | OK |
| EFFIS WMS GetCapabilities | https://maps.effis.emergency.copernicus.eu/effis?service=WMS&request=GetCapabilities&version=1.3.0 | 200 | 105131 | slojeva: 130; ecmwf*: []; TIME(ecmwf007.fwi): nema | OK |
| EFFIS GetFeatureInfo FWI 2026-10-28 (text/plain) | https://maps.effis.emergency.copernicus.eu/effis?service=WMS&version=1.1.1&request=GetFeatureInfo&layers=ecmwf007.fwi&query_layers=ecmwf007.fwi&srs=EPSG%3A4326&bbox=15.09%2C43.32%2C16.09%2C44.32&width | 200 | 459 | <?xml version='1.0' encoding="UTF-8" standalone="no" ?> ⏎ <!DOCTYPE ServiceExceptionReport SYSTEM "http://schemas.opengis.net/wms/1.1.1/exception_1_1_1.dtd"> ⏎ <ServiceExceptionReport version="1.1.1"> ⏎ <ServiceException code="LayerNotDefined"> ⏎ msWMSLoadGetMapParams(): WMS server error. Invalid layer(s) given in the LAYERS parameter. A layer might be disabled for this request. Check wms/ows_enable_reque | OK |
| EFFIS GetFeatureInfo FWI 2026-10-28 (application/json) | https://maps.effis.emergency.copernicus.eu/effis?service=WMS&version=1.1.1&request=GetFeatureInfo&layers=ecmwf007.fwi&query_layers=ecmwf007.fwi&srs=EPSG%3A4326&bbox=15.09%2C43.32%2C16.09%2C44.32&width | 200 | 459 | <?xml version='1.0' encoding="UTF-8" standalone="no" ?> ⏎ <!DOCTYPE ServiceExceptionReport SYSTEM "http://schemas.opengis.net/wms/1.1.1/exception_1_1_1.dtd"> ⏎ <ServiceExceptionReport version="1.1.1"> ⏎ <ServiceException code="LayerNotDefined"> ⏎ msWMSLoadGetMapParams(): WMS server error. Invalid layer(s) given in the LAYERS parameter. A layer might be disabled for this request. Check wms/ows_enable_reque | OK |
| EFFIS GetFeatureInfo FWI 2026-10-28 (text/html) | https://maps.effis.emergency.copernicus.eu/effis?service=WMS&version=1.1.1&request=GetFeatureInfo&layers=ecmwf007.fwi&query_layers=ecmwf007.fwi&srs=EPSG%3A4326&bbox=15.09%2C43.32%2C16.09%2C44.32&width | 200 | 459 | <?xml version='1.0' encoding="UTF-8" standalone="no" ?> ⏎ <!DOCTYPE ServiceExceptionReport SYSTEM "http://schemas.opengis.net/wms/1.1.1/exception_1_1_1.dtd"> ⏎ <ServiceExceptionReport version="1.1.1"> ⏎ <ServiceException code="LayerNotDefined"> ⏎ msWMSLoadGetMapParams(): WMS server error. Invalid layer(s) given in the LAYERS parameter. A layer might be disabled for this request. Check wms/ows_enable_reque | OK |
| EFFIS GetFeatureInfo FWI 2026-08-13 (text/plain) | https://maps.effis.emergency.copernicus.eu/effis?service=WMS&version=1.1.1&request=GetFeatureInfo&layers=ecmwf007.fwi&query_layers=ecmwf007.fwi&srs=EPSG%3A4326&bbox=15.09%2C43.32%2C16.09%2C44.32&width | 200 | 459 | <?xml version='1.0' encoding="UTF-8" standalone="no" ?> ⏎ <!DOCTYPE ServiceExceptionReport SYSTEM "http://schemas.opengis.net/wms/1.1.1/exception_1_1_1.dtd"> ⏎ <ServiceExceptionReport version="1.1.1"> ⏎ <ServiceException code="LayerNotDefined"> ⏎ msWMSLoadGetMapParams(): WMS server error. Invalid layer(s) given in the LAYERS parameter. A layer might be disabled for this request. Check wms/ows_enable_reque | OK |
| EFFIS GetFeatureInfo FWI 2026-08-13 (application/json) | https://maps.effis.emergency.copernicus.eu/effis?service=WMS&version=1.1.1&request=GetFeatureInfo&layers=ecmwf007.fwi&query_layers=ecmwf007.fwi&srs=EPSG%3A4326&bbox=15.09%2C43.32%2C16.09%2C44.32&width | 200 | 459 | <?xml version='1.0' encoding="UTF-8" standalone="no" ?> ⏎ <!DOCTYPE ServiceExceptionReport SYSTEM "http://schemas.opengis.net/wms/1.1.1/exception_1_1_1.dtd"> ⏎ <ServiceExceptionReport version="1.1.1"> ⏎ <ServiceException code="LayerNotDefined"> ⏎ msWMSLoadGetMapParams(): WMS server error. Invalid layer(s) given in the LAYERS parameter. A layer might be disabled for this request. Check wms/ows_enable_reque | OK |
| EFFIS GetFeatureInfo FWI 2026-08-13 (text/html) | https://maps.effis.emergency.copernicus.eu/effis?service=WMS&version=1.1.1&request=GetFeatureInfo&layers=ecmwf007.fwi&query_layers=ecmwf007.fwi&srs=EPSG%3A4326&bbox=15.09%2C43.32%2C16.09%2C44.32&width | 200 | 459 | <?xml version='1.0' encoding="UTF-8" standalone="no" ?> ⏎ <!DOCTYPE ServiceExceptionReport SYSTEM "http://schemas.opengis.net/wms/1.1.1/exception_1_1_1.dtd"> ⏎ <ServiceExceptionReport version="1.1.1"> ⏎ <ServiceException code="LayerNotDefined"> ⏎ msWMSLoadGetMapParams(): WMS server error. Invalid layer(s) given in the LAYERS parameter. A layer might be disabled for this request. Check wms/ows_enable_reque | OK |
| EFFIS GetMap image/tiff | https://maps.effis.emergency.copernicus.eu/effis?service=WMS&version=1.1.1&request=GetMap&layers=ecmwf007.fwi&srs=EPSG%3A4326&bbox=15.4%2C43.4%2C16.6%2C44.3&width=120&height=90&format=image%2Ftiff&tim | 200 | 459 | Content-Type=application/vnd.ogc.se_xml; charset=UTF-8; nije raster: '<?xml version=\'1.0\' encoding="UTF-8" standalone="no" ?>\n<!DOCTYPE ServiceExceptionReport SYSTEM "http://schemas.opengis.net/wms/1.1.1/exception_1_1_1.' | OK |
| EFFIS GetMap image/geotiff | https://maps.effis.emergency.copernicus.eu/effis?service=WMS&version=1.1.1&request=GetMap&layers=ecmwf007.fwi&srs=EPSG%3A4326&bbox=15.4%2C43.4%2C16.6%2C44.3&width=120&height=90&format=image%2Fgeotiff& | 200 | 373 | Content-Type=application/vnd.ogc.se_xml; charset=UTF-8; nije raster: '<?xml version=\'1.0\' encoding="UTF-8" standalone="no" ?>\n<!DOCTYPE ServiceExceptionReport SYSTEM "http://schemas.opengis.net/wms/1.1.1/exception_1_1_1.' | OK |
| EFFIS GetLegendGraphic FWI | https://maps.effis.emergency.copernicus.eu/effis?service=WMS&version=1.1.1&request=GetLegendGraphic&layer=ecmwf007.fwi&format=image%2Fpng | 200 | 455 | Content-Type=application/vnd.ogc.se_xml; charset=UTF-8 (razrede pročitati sa slike) | OK |
| EFFIS BA WFS (application/json) | https://maps.effis.emergency.copernicus.eu/effis | - | - | HTTPSConnectionPool(host='maps.effis.emergency.copernicus.eu', port=443): Max retries exceeded with url: /effis?service=WFS&version=1.1.0&request=GetFeature&typename=ms%3Amodis.ba.poly&bbox=15.4%2C43.4%2C16.6%2C44.3%2CEPSG%3A4326&maxfeatures=2000&outputformat=application%2Fjson (Caused by ResponseError('too many 502 error responses')) | GREŠKA |
| EFFIS BA WFS bbox ŠKŽ (geojson) | https://maps.effis.emergency.copernicus.eu/effis?service=WFS&version=1.1.0&request=GetFeature&typename=ms%3Amodis.ba.poly&bbox=15.4%2C43.4%2C16.6%2C44.3%2CEPSG%3A4326&maxfeatures=2000&outputformat=geo | 200 | 75 | objekata≈0; početak: '{\n"type": "FeatureCollection",\n"name": "modis.ba.poly",\n"features": [\n\n]\n}\n' | GREŠKA |
| EFFIS BA WFS bbox ŠKŽ (GML) | https://maps.effis.emergency.copernicus.eu/effis?service=WFS&version=1.1.0&request=GetFeature&typename=ms%3Amodis.ba.poly&bbox=15.4%2C43.4%2C16.6%2C44.3%2CEPSG%3A4326&maxfeatures=2000 | 200 | 724 | objekata≈0; početak: '<?xml version=\'1.0\' encoding="UTF-8" ?>\n<wfs:FeatureCollection\n   xmlns:ms="http://mapserver.gis.umn.edu/mapserver"\n   xmlns:gml="http://www.opengis.net/gml"\n   xmlns:wfs="http://www.opengis.net/wfs"\n   xmlns:ogc="http://www.opengis.net/ogc"\n   xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"\n ' | GREŠKA |
| WorldCover HEAD N42E015 | https://esa-worldcover.s3.eu-central-1.amazonaws.com/v200/2021/map/ESA_WorldCover_10m_2021_v200_N42E015_Map.tif | 200 | 54463449 | Content-Type=binary/octet-stream, Last-Modified=Wed, 26 Oct 2022 12:53:34 GMT | OK |
| WorldCover HEAD N42E012 | https://esa-worldcover.s3.eu-central-1.amazonaws.com/v200/2021/map/ESA_WorldCover_10m_2021_v200_N42E012_Map.tif | 200 | 64880418 | Content-Type=binary/octet-stream, Last-Modified=Wed, 26 Oct 2022 12:51:57 GMT | OK |
| WorldCover HEAD N45E015 | https://esa-worldcover.s3.eu-central-1.amazonaws.com/v200/2021/map/ESA_WorldCover_10m_2021_v200_N45E015_Map.tif | 200 | 88855733 | Content-Type=binary/octet-stream, Last-Modified=Wed, 26 Oct 2022 12:54:42 GMT | OK |
| GISCO NUTS3 2021 | https://gisco-services.ec.europa.eu/distribution/v2/nuts/geojson/NUTS_RG_01M_2021_4326_LEVL_3.geojson | 200 | 28176705 | HR regije: [('HR064', 'Krapinsko-zagorska županija'), ('HR024', 'Brodsko-posavska županija'), ('HR022', 'Virovitičko-podravska županija'), ('HR023', 'Požeško-slavonska županija'), ('HR037', 'Dubrovačko-neretvanska županija'), ('HR033', 'Zadarska županija'), ('HR065', 'Zagrebačka županija'), ('HR062', 'Varaždinska županija'), ('HR036', 'Istarska županija'), ('HR027', 'Karlovačka županija'), ('HR028', 'Sisačko-moslavačka županija'), ('HR025', 'Osječko-baranjska županija'), ('HR031', 'Primorsko-goranska županija'), ('HR026', 'Vukovarsko-srijemska županija'), ('HR035', 'Splitsko-dalmatinska županija'), ('HR034', 'Šibensko-kninska županija'), ('HR063', 'Koprivničko-križevačka županija'), ('HR061', 'Međimurska županija'), ('HR021', 'Bjelovarsko-bilogorska županija'), ('HR032', 'Ličko-senjska županija'), ('HR050', 'Grad Zagreb')] | OK |
| OSM (OSMnx) Murter–Tisno | Overpass API via OSMnx | 200 | 3472 čvorova | bridova=4040, mostova grafa=1540; Tisno: most osm=[25219856, 146627895, 335778167] ime=Istočna gomilica ref=D121 highway=primary bridge=movable → most grafa=True; Murter↔kopno bez mostova grafa povezani=False (False → Murter je E1) | OK |

## Detalji

### HC brojenje 2025 – sadržaj ZIP-a

```

```

### dzs_naselja – popis_2021-stanovnistvo_po_naseljima.xlsx

```
--- list 'Sadrzaj-Contents' (14, 3)
                                          0   1                                        2
0                                       NaN NaN                                      NaN
1   POPIS STANOVNIŠTVA, KUĆANSTAVA I STA... NaN                                      NaN
2   CENSUS OF POPULATION, HOUSEHOLDS AND... NaN                                      NaN
3   Molimo korisnike da pri korištenju p... NaN                                      NaN
4   Users are kindly requested to state ... NaN                                      NaN
5                                       NaN NaN                                      NaN
6                                       NaN NaN                                  ZNAKOVI
7                                       NaN NaN                                  SYMBOLS
8                                    Tab. 1 NaN  STANOVNIŠTVO PREMA STAROSTI I SPOLU ...
9                                       NaN NaN  POPULATION BY AGE AND SEX, BY SETTLE...
10                                  Tab. 2. NaN  STANOVNIŠTVO PREMA STAROSTI I SPOLU ...
11                                      NaN NaN  POPULATION BY AGE AND SEX, BY DISTRI...
12                                      NaN NaN                  METODOLOŠKA OBJAŠNJENJA
13                                      NaN NaN                     NOTES ON METHODOLOGY
--- list 'Znakovi-Symbols' (9, 3)
                                         0   1             2
0                                      NaN NaN           NaN
1  Molimo korisnike da pri korištenju p... NaN           NaN
2  Users are kindly requested to state ... NaN           NaN
3                                  ZNAKOVI NaN           NaN
4                                  SYMBOLS NaN           NaN
5                                      NaN NaN           NaN
6                                        - NaN   nema pojave
7                                      NaN NaN           NaN
8                                        - NaN  no occurence
--- list '1.' (22010, 29)
                                         0                            1                    2                           3                                  4                     5     6    7              8                                        9       10       11  ...       17       18       19       20       21       22       23       24       25       26       27                      28
0                                        1.                          NaN                  NaN                         NaN                                NaN                   NaN   NaN  NaN            NaN                                      NaN     NaN      NaN  ...      NaN      NaN      NaN      NaN      NaN      NaN      NaN      NaN      NaN      NaN      NaN                     NaN
1   STANOVNIŠTVO PREMA STAROSTI I SPOLU ...                          NaN                  NaN                         NaN                                NaN                   NaN   NaN  NaN            NaN                                      NaN     NaN      NaN  ...      NaN      NaN      NaN      NaN      NaN      NaN      NaN      NaN      NaN      NaN      NaN                     NaN
2   POPULATION BY AGE AND SEX, BY SETTLE...                          NaN                  NaN                         NaN                                NaN                   NaN   NaN  NaN            NaN                                      NaN     NaN      NaN  ...      NaN      NaN      NaN      NaN      NaN      NaN      NaN      NaN      NaN      NaN      NaN                     NaN
3   Molimo korisnike da pri korištenju p...                          NaN                  NaN                         NaN                                NaN                   NaN   NaN  NaN            NaN                                      NaN     NaN      NaN  ...      NaN      NaN      NaN      NaN      NaN      NaN      NaN      NaN      NaN      NaN      NaN                     NaN
4   Users are kindly requested to state ...                          NaN                  NaN                         NaN                                NaN                   NaN   NaN  NaN            NaN                                      NaN     NaN      NaN  ...      NaN      NaN      NaN      NaN      NaN      NaN      NaN      NaN      NaN      NaN      NaN                     NaN
5                                       NaN                          NaN                  NaN                         NaN                                NaN                   NaN   NaN  NaN            NaN                                      NaN     NaN      NaN  ...      NaN      NaN      NaN      NaN      NaN      NaN      NaN      NaN      NaN      NaN      NaN                     NaN
6                                       NaN                          NaN                  NaN                         NaN                                NaN                   NaN   NaN  NaN            NaN  Starost                  \nAge      ...     NaN      NaN  ...      NaN      NaN      NaN      NaN      NaN      NaN      NaN      NaN      NaN      NaN      NaN                     NaN
7                                  Županija  Jedinica lokalne samouprave            County of  Local self-government unit  Grad/općina  \nTown/Municipality   Naselje\nSettlement   Spol  Sex  Ukupno\nTotal                                    0 – 4   5 – 9  10 – 14  ...  40 – 44  45 – 49  50 – 54  55 – 59  60 – 64  65 – 69  70 – 74  75 – 79  80 – 84  85 – 89  90 – 94  95 i više\n95 and over
8                        Republika Hrvatska                          NaN  Republic of Croatia                         NaN                                NaN                   NaN   sv.  All        3871833                                   175535  181445   195436  ...   267349   260146   260056   279504   288351   279106   228612   146855   122719    67249    21019                    3679
9                        Republika Hrvatska      
```

### dzs_jls – popis_2021-stanovnistvo_po_gradovima_opcinama.xlsx

```
--- list 'Sadrzaj-Contents' (52, 3)
                                          0   1                                        2
0                                       NaN NaN                                      NaN
1   POPIS STANOVNIŠTVA, KUĆANSTAVA I STA... NaN                                      NaN
2   CENSUS OF POPULATION, HOUSEHOLDS AND... NaN                                      NaN
3   Molimo korisnike da pri korištenju p... NaN                                      NaN
4   Users are kindly requested to state ... NaN                                      NaN
5                                       NaN NaN                                      NaN
6                                       NaN NaN                        KRATICE I ZNAKOVI
7                                       NaN NaN                ABBREVIATIONS AND SYMBOLS
8                                   Tab. 1. NaN  STANOVNIŠTVO PREMA NARODNOSTI PO GRA...
9                                       NaN NaN  POPULATION BY ETHNICITY, BY TOWNS/MU...
10                                  Tab. 2. NaN  STANOVNIŠTVO PREMA VJERI PO GRADOVIM...
11                                      NaN NaN  POPULATION BY RELIGION, BY TOWNS/MUN...
12                                  Tab. 3. NaN  STANOVNIŠTVO PREMA DRŽAVLJANSTVU PO ...
13                                      NaN NaN  POPULATION BY CITIZENSHIP, BY TOWNS/...
14                                  Tab. 4. NaN  STANOVNIŠTVO PREMA MATERINSKOM JEZIK...
--- list 'Kratice-Abbreviations' (29, 3)
                                          0   1                                        2
0                                       NaN NaN                                      NaN
1   Molimo korisnike da pri korištenju p... NaN                                      NaN
2   Users are kindly requested to state ... NaN                                      NaN
3                                   KRATICE NaN                                      NaN
4                             ABBREVIATIONS NaN                                      NaN
5                                       NaN NaN                                      NaN
6                                        EZ NaN                       Europska zajednica
7                                         m NaN                                 muškarci
8                                        NN NaN                           Narodne novine
9                                        SL NaN             Službeni list Europske unije
10                                      sv. NaN                                    svega
11                                        z NaN  podatak zbog povjerljivosti nije obj...
12                                        ž NaN                                     žene
13                                      NaN NaN                                      NaN
14                                       EC NaN                       European Community
--- list '1.' (602, 65)
                                         0                            1                    2                           3                                4              5                    6               7                     8                   9                            10                         11  ...                53                      54                                       55                                       56                                       57                                       58                                59                                   60                                   61                                      62                  63                        64
0                                        1.                          NaN                  NaN                         NaN                              NaN            NaN                  NaN             NaN                   NaN                 NaN                          NaN                        NaN  ...               NaN                     NaN                                      NaN                                      NaN                                      NaN                                      NaN                               NaN                                  NaN                                  NaN                                     NaN                 NaN                       NaN
1   STANOVNIŠTVO PREMA NARODNOSTI PO GRA...                          NaN                  NaN                         NaN                              NaN            NaN                  NaN             NaN                   NaN                 NaN                          NaN                        NaN  ...               NaN                     NaN                                      NaN                                      NaN                                      NaN                                      NaN                               NaN                                  NaN                                  NaN                                     NaN                 NaN                       NaN
2   POPULATION BY ETHNICITY, BY TOWNS/MU...                          NaN                  NaN                         NaN                              NaN            NaN                  NaN             NaN                   NaN                 NaN                          NaN                        NaN  ...               NaN                     NaN                                      NaN                                      NaN                                      NaN                                      NaN                               NaN                                  NaN                                  NaN                                     NaN                 NaN                       NaN
3   Molimo korisnike da pri korištenju p...                          NaN                  NaN                         NaN                              NaN            NaN                  NaN             NaN     
```

### dzs_stanovi – popis-2021-stambene-jedinice-po-gradovima-i-opcinama.xlsx

```
--- list 'Sadrzaj-Contents' (18, 3)
                                          0   1                                        2
0                                       NaN NaN                                      NaN
1   POPIS STANOVNIŠTVA, KUĆANSTAVA I STA... NaN                                      NaN
2   CENSUS OF POPULATION, HOUSEHOLDS AND... NaN                                      NaN
3   Molimo korisnike da pri korištenju p... NaN                                      NaN
4   Users are kindly requested to state ... NaN                                      NaN
5                                       NaN NaN                                      NaN
6                                       NaN NaN                        KRATICE I ZNAKOVI
7                                       NaN NaN                ABBREVIATIONS AND SYMBOLS
8                                   Tab. 1. NaN  STANOVI PREMA NAČINU KORIŠTENJA PO G...
9                                       NaN NaN  DWELLINGS BY OCCUPANCY STATUS, BY TO...
10                                  Tab. 2. NaN  STAMBENE JEDINICE PREMA BROJU KUĆANS...
11                                      NaN NaN  HOUSING UNITS BY NUMBER OF HOUSEHOLD...
12                                  Tab. 3. NaN  NASTANJENI STANOVI PREMA BROJU SOBA ...
13                                      NaN NaN  OCCUPIED DWELLINGS BY NUMBER OF ROOM...
14                                  Tab. 4. NaN  NASTANJENI STANOVI PREMA POMOĆNIM PR...
--- list 'Kratice-Abbreviations' (17, 3)
                                          0   1               2
0                                       NaN NaN             NaN
1   Molimo korisnike da pri korištenju p... NaN             NaN
2   Users are kindly requested to state ... NaN             NaN
3                                   KRATICE NaN             NaN
4                             ABBREVIATIONS NaN             NaN
5                                       NaN NaN             NaN
6                                        m2 NaN  četvorni metar
7                                       NaN NaN             NaN
8                                        m2 NaN    square metre
9                                       NaN NaN             NaN
10                                      NaN NaN             NaN
11                                  ZNAKOVI NaN             NaN
12                                  SYMBOLS NaN             NaN
13                                      NaN NaN             NaN
14                                        - NaN     nema pojave
--- list '1.' (1196, 13)
                                         0                            1                    2                           3                                4                                  5              6                                        7                     8                                        9                                        10                      11                                       12
0                                        1.                          NaN                  NaN                         NaN                              NaN                                NaN            NaN                                      NaN                   NaN                                      NaN                                      NaN                     NaN                                      NaN
1   STANOVI PREMA NAČINU KORIŠTENJA PO G...                          NaN                  NaN                         NaN                              NaN                                NaN            NaN                                      NaN                   NaN                                      NaN                                      NaN                     NaN                                      NaN
2   DWELLINGS BY OCCUPANCY STATUS, BY TO...                          NaN                  NaN                         NaN                              NaN                                NaN            NaN                                      NaN                   NaN                                      NaN                                      NaN                     NaN                                      NaN
3   Molimo korisnike da pri korištenju p...                          NaN                  NaN                         NaN                              NaN                                NaN            NaN                                      NaN                   NaN                                      NaN                                      NaN                     NaN                                      NaN
4   Users are kindly requested to state ...                          NaN                  NaN                         NaN                              NaN                                NaN            NaN                                      NaN                   NaN                                      NaN                                      NaN                     NaN                                      NaN
5                                       NaN                          NaN                  NaN                         NaN                              NaN                                NaN            NaN                                      NaN                   NaN                                      NaN                                      NaN                     NaN                                      NaN
6                                       NaN                          NaN                  NaN                         NaN                              NaN                                NaN  Ukupno\nTotal  Stanovi za stalno stanovanje\nDwelli...                   NaN                                      NaN  Stanovi koji se koriste povremeno\nD...                     NaN  Stanovi u kojima se samo obavljala d...
7                                  Županija  Jedinica lokalne samouprave            County of  Local self-government unit  Grad/op
```

### dzs_gradovi – gradovi-u-statistici.xlsx

```
--- list 'Sadrzaj-Contents' (100, 3)
                                          0   1                                        2
0                                       NaN NaN                                      NaN
1                      GRADOVI U STATISTICI NaN                                      NaN
2                       TOWNS IN STATISTICS NaN                                      NaN
3   Molimo korisnike da pri korištenju p... NaN                                      NaN
4   Users are kindly requested to state ... NaN                                      NaN
5                                       NaN NaN                                      NaN
6                                       NaN NaN                                  KRATICE
7                                       NaN NaN                            ABBREVIATIONS
8                                       NaN NaN                                      NaN
9                                    Tab-1. NaN  STANOVNIŠTVO – POPIS 2011. I POPIS 2...
10                                      NaN NaN  POPULATION – 2011 CENSUS AND 2021 CE...
11                                      NaN NaN                                      NaN
12                                   Tab-2. NaN  STANOVNIŠTVO – PROCJENA I PRIRODNO K...
13                                      NaN NaN  POPULATION – ESTIMATE AND NATURAL CH...
14                                      NaN NaN                                      NaN
--- list 'Kratice-Abbreviations' (18, 3)
                                          0   1                                        2
0                                       NaN NaN                                      NaN
1   Molimo korisnike da pri korištenju p... NaN                                      NaN
2   Users are kindly requested to state ... NaN                                      NaN
3                                   KRATICE NaN                                      NaN
4                             ABBREVIATIONS NaN                                      NaN
5                                       NaN NaN                                      NaN
6                                         z NaN  podatak zbog povjerljivosti nije obj...
7                                       NaN NaN                                      NaN
8                                         z NaN  data is not published for confidenti...
9                                       NaN NaN                                      NaN
10                                  ZNAKOVI NaN                                      NaN
11                                  SYMBOLS NaN                                      NaN
12                                      NaN NaN                                      NaN
13                                        ‐ NaN                              nema pojave
14                                        … NaN                 ne raspolaže se podatkom
--- list 'Tab-1.' (565, 25)
                                         0          1                                     2                                  3       4         5      6        7     8              9          10           11         12         13             14                     15                   16                  17         18                                 19      20        21     22       23    24
0                                    Tab-1.        NaN                                   NaN                                NaN     NaN       NaN    NaN      NaN   NaN            NaN        NaN          NaN        NaN        NaN            NaN                    NaN                  NaN                 NaN        NaN                                NaN     NaN       NaN    NaN      NaN   NaN
1   STANOVNIŠTVO – POPIS 2011. I POPIS 2...        NaN                                   NaN                                NaN     NaN       NaN    NaN      NaN   NaN            NaN        NaN          NaN        NaN        NaN            NaN                    NaN                  NaN                 NaN        NaN                                NaN     NaN       NaN    NaN      NaN   NaN
2   POPULATION – 2011 CENSUS AND 2021 CE...        NaN                                   NaN                                NaN     NaN       NaN    NaN      NaN   NaN            NaN        NaN          NaN        NaN        NaN            NaN                    NaN                  NaN                 NaN        NaN                                NaN     NaN       NaN    NaN      NaN   NaN
3   Molimo korisnike da pri korištenju p...        NaN                                   NaN                                NaN     NaN       NaN    NaN      NaN   NaN            NaN        NaN          NaN        NaN        NaN            NaN                    NaN                  NaN                 NaN        NaN                                NaN     NaN       NaN    NaN      NaN   NaN
4   Users are kindly requested to state ...        NaN                                   NaN                                NaN     NaN       NaN    NaN      NaN   NaN            NaN        NaN          NaN        NaN        NaN            NaN                    NaN                  NaN                 NaN        NaN                                NaN     NaN       NaN    NaN      NaN   NaN
5                                       NaN        NaN                                   NaN                   Broj stanovnika,    Spol       NaN    NaN  Starost   NaN     Aktivnost         NaN          NaN        NaN        NaN   Obrazovanje                     NaN                  NaN                 NaN        NaN                   Broj stanovnika,    Spol       NaN    NaN  Starost   NaN
6                                       NaN        NaN                                   NaN                        Popis 2011.     Sex       NaN    NaN      Age   NaN      Activity         NaN          NaN        NaN        NaN     Education                     NaN                  NaN 
```

### DZS Turizam u 2025. – poveznice na datoteke

```

```

### HC WFS capabilities (početak)

```
<?xml version="1.0" encoding="UTF-8"?><wfs:WFS_Capabilities version="2.0.0" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xmlns="http://www.opengis.net/wfs/2.0" xmlns:wfs="http://www.opengis.net/wfs/2.0" xmlns:ows="http://www.opengis.net/ows/1.1" xmlns:gml="http://www.opengis.net/gml/3.2" xmlns:fes="http://www.opengis.net/fes/2.0" xmlns:xlink="http://www.w3.org/1999/xlink" xmlns:xs="http://www.w3.org/2001/XMLSchema" xsi:schemaLocation="http://www.opengis.net/wfs/2.0 http://schemas.opengis.net/wfs/2.0/wfs.xsd http://inspire.ec.europa.eu/schemas/inspire_dls/1.0 https://inspire.ec.europa.eu/schemas/inspire_dls/1.0/inspire_dls.xsd" xmlns:xml="http://www.w3.org/XML/1998/namespace" xmlns:inspire_dls="http://inspire.ec.europa.eu/schemas/inspire_dls/1.0" xmlns:inspire_common="http://inspire.ec.europa.eu/schemas/common/1.0" xmlns:hc_inspire_tn-ro="http://inspire.ec.europa.eu/schemas/tn-ro/4.0" updateSequence="19486"><ows:ServiceIdentification><ows:Title>INSPIRE WFS Baze podataka javnih cesta RH</ows:Title><ows:Abstract>Web servisi za preuzimanje Baze podataka javnih cesta Republike Hrvatske sukladno Zakonu o NIPP-u i INSPIRE smjernicama. Baza podataka javnih cesta Republike Hrvatske sadrži sve javne ceste na teritoriju Republike Hrvatske, sukladno važećem Zakonu o cestama i Odluci o razvrstavanju javnih cesta. Podaci o položaju javnih cesta dani su u HTRS96/TM referentnom sustavu.</ows:Abstract><ows:Keywords><ows:Keyword>WFS</ows:Keyword><ows:Keyword>GEOSERVER</ows:Keyword></ows:Keywords><ows:ServiceType>WFS</ows:ServiceType><ows:ServiceTypeVersion>2.0.0</ows:ServiceTypeVersion><ows:Fees/><ows:AccessConstraints/></ows:ServiceIdentification><ows:ServiceProvider><ows:ProviderName>Hrvatske ceste d.o.o.</ows:ProviderName><ows:ServiceContact><ows:IndividualName>Goran Jurakić, mag. ing. geod. et geoinf.</ows:IndividualName><ows:PositionName/><ows:ContactInfo><ows:Phone><ows:Voice>+385 1 2366 119</ows:Voice><ows:Facsimile/></ows:Phone><ows:Address><ows:DeliveryPoint/><ows:City>Zagreb</ows:City><ows:AdministrativeArea/><ows:PostalCode>10000</ows:PostalCode><ows:Country>Hrvatska</ows:Country><ows:ElectronicMailAddress>goran.jurakic@hrvatske-ceste.hr</ows:ElectronicMailAddress></ows:Address></ows:ContactInfo></ows:ServiceContact></ows:ServiceProvider><ows:OperationsMetadata><ows:Operation name="GetCapabilities"><ows:DCP><ows:HTTP><ows:Get xlink:href="https://geoportal.hrvatske-ceste.hr/inspire/tn-ro/wfs"/><ows:Post xlink:href="https://geoportal.hrvatske-ceste.hr/inspire/tn-ro/wfs"/></ows:HTTP></ows:DCP><ows:Parameter name="AcceptVersions"><ows:AllowedValues><ows:Value>1.0.0</ows:Value><ows:Value>1.1.0</ows:Value><ows:Value>2.0.0</ows:Value></ows:AllowedValues></ows:Parameter><ows:Parameter name="AcceptFormats"><ows:AllowedValues><ows:Value>text/xml</ows:Value></ows:AllowedValues></ows:Parameter><ows:Parameter name="Sections"><ows:AllowedValues><ows:Value>ServiceIdentification</ows:Value><ows:Value>ServiceProvider</ows:Value><ows:Value>OperationsMetadata</ows:Value><ows:Value>FeatureTypeList</ows:Value><ows:Value>Filter_Capabilities</ows:Value></ows:AllowedValues></ows:Parameter></ows:Operation><ows:Operation name="DescribeFeatureType"><ows:DCP><ows:HTTP><ows:Get xlink:href="https://geoportal.hrvatske-ceste.hr/inspire/tn-ro/wfs"/><ows:Post xlink:href="https://geoportal.hrvatske-ceste.hr/inspire/tn-ro/wfs"/></ows:HTTP></ows:DCP><ows:Parameter name="outputFormat"><ows:AllowedValues><ows:Value>application/gml+xml; version=3.2</ows:Value></ows:AllowedValues></ows:Parameter></ows:Operation><ows:Operation name="GetFeature"><ows:DCP><ows:HTTP><ows:Get xlink:href="https://geoportal.hrvatske-ceste.hr/inspire/tn-ro/wfs"/><ows:Post xlink:href="https://geoportal.hrvatske-ceste.hr/inspire/tn-ro/wfs"/></ows:HTTP></ows:DCP><ows:Parameter name="resultType"><ows:AllowedValues><ows:Value>results</ows:Value><ows:Value>hits</ows:Value></ows:AllowedValues></ows:Parameter><ows:Parameter name="outputFormat"><ows:AllowedValues><ows:Value>application/gml+xml; ver
```

### HC WFS GetFeature Tisno

```
<?xml version="1.0" encoding="UTF-8"?><wfs:FeatureCollection xmlns:wfs="http://www.opengis.net/wfs/2.0" xmlns:xs="http://www.w3.org/2001/XMLSchema" xmlns:gml="http://www.opengis.net/gml/3.2" xmlns:gn="http://inspire.ec.europa.eu/schemas/gn/4.0" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xmlns:gco="http://www.isotc211.org/2005/gco" xmlns:hc_inspire_net="http://inspire.ec.europa.eu/schemas/net/4.0" xmlns:tn="http://inspire.ec.europa.eu/schemas/tn/4.0" xmlns:hc_inspire_tn-ro="http://inspire.ec.europa.eu/schemas/tn-ro/4.0" xmlns:gmd="http://www.isotc211.org/2005/gmd" xmlns:xlink="http://www.w3.org/1999/xlink" xmlns:base="http://inspire.ec.europa.eu/schemas/base/3.3" numberMatched="3" numberReturned="3" timeStamp="2026-10-28T19:26:28.913Z" xsi:schemaLocation="http://inspire.ec.europa.eu/schemas/net/4.0 https://inspire.ec.europa.eu/schemas/net/4.0/Network.xsd http://www.opengis.net/wfs/2.0 http://schemas.opengis.net/wfs/2.0/wfs.xsd http://inspire.ec.europa.eu/schemas/tn-ro/4.0 https://inspire.ec.europa.eu/schemas/tn-ro/4.0/RoadTransportNetwork.xsd http://www.opengis.net/gml/3.2 http://schemas.opengis.net/gml/3.2.1/gml.xsd"><wfs:member><hc_inspire_tn-ro:RoadLink gml:id="RoadLink.1049"><hc_inspire_net:beginLifespanVersion>2020-07-02T22:00:00Z</hc_inspire_net:beginLifespanVersion><hc_inspire_net:inspireId><base:Identifier><base:localId>rl.1049</base:localId><base:namespace>HR.HC.BPJCRH</base:namespace></base:Identifier></hc_inspire_net:inspireId><hc_inspire_net:inNetwork xlink:href="https://geoportal.hrvatske-ceste.hr/inspire/net/wfs?service=wfs&amp;version=2.0.0&amp;request=getFeature&amp;storedQuery_Id=urn:ogc:def:query:OGC-WFS::GetFeatureById&amp;ID=Network.2"/><hc_inspire_net:centrelineGeometry><gml:LineString gml:id="geom.rl.1049" srsName="http://www.opengis.net/def/crs/EPSG/0/3765"><gml:posList>430118.41 4850346.51 430125.67 4850348.19 430133.49 4850350.6 430138.31 4850352.43 430145.56 4850355.31 430153.64 4850359.23 430161.05 4850363.56 430166.65 4850367.27 430177.44 4850375.94 430184.21 4850381.65 430189.4 4850386.84 430194.79 4850393.18 430199.45 4850399.21 430202.51 4850403.97 430206.01 4850410.85 430208.97 4850418.57 430211.4 4850425.55 430213.3 4850432.53 430215.1 4850440.89 430216.16 4850448.82 430216.58 4850455.8 430216.27 4850469.34 430214.38 4850496.63 430209.6 4850562.33 430204.85 4850625.58 430202.73 4850654.99 430195.75 4850744.48 430194.27 4850767.96 430194.27 4850779.39 430195.01 4850787.96 430196.39 4850796 430199.03 4850806.15 430202.42 4850816.62 430207.49 4850828.36 430213.63 4850841.27 430226.64 4850866.66 430237.43 4850888.24 430243.57 4850901.56 430247.69 4850911.61 430251.82 4850923.25 430254.99 4850933.93 430257.21 4850943.45 430258.48 4850951.39 430262.29 4850974.98 430268.21 4851012.32 430272.76 4851038.87 430275.62 4851051.56 430278.69 4851062.67 430282.5 4851073.46 430285.88 4851081.81 430290.54 4851091.97 430295.4 4851101.49 430302.28 4851113.97 430308.62 4851123.7 430314.87 4851131.85 430326.29 4851145.49 430341.84 4851162.63 430361.2 4851183.89 430379.29 4851203.78 430391.66 4851216.26 430410.81 4851234.14 430426.36 4851247.57 430445.08 4851262.7 430465.08 4851277.72 430481.79 4851289.14 430504.32 4851303.32 430522.52 4851314 430537.11 4851321.93 430559.86 4851333.25 430575.2 4851340.66 430592.86 4851348.91 430606.4 4851355.15 430615.71 4851358.85 430625.65 4851362.55 430635.7 4851365.41 430645.96 4851367.73 430656.65 4851369.53 430669.34 4851371.44 430690.39 4851374.4 430712.82 4851377.57 430736.3 4851381.27 430750.79 4851383.6 430762.01 4851385.4 430773.01 4851386.98 430777.98 4851387.3 430785.59 4851387.51 430789.83 4851386.98 430793.53 4851386.03 430810.88 4851380.95 430849.59 4851369.21 430869.06 4851362.65 430876.57 4851359.9 430886.4 4851356.2 430893.81 4851353.66 430898.99 4851353.03 430903.22 4851353.45 430906.29 4851354.3 430908.93 4851355.78 430911.9 4851358.21 430913.91 4851361.07 430917.29 4851367.62 430922.47 4851377.57 430932.21 4851396.4 430936.12 4851403.06 430938.55 4851405.7 430943.21 4851408.88 430946.59 4851410.36 430949.87 4851410.78 430953.36 4851410.89 430960.13 4851409.94 430995.89 4851405.18 431020 4851402.11 431054.29 4851399.36 431084.31 4851397.21 431092.5 4851396.59 431102.45 4851395.77 431111.99 4851394.95 431121.11 4851394.26 431127.38 4851393.59 431130.13 4851393.3 431138.87 4851392.63 431147.82 4851391.61 431149.71 4851391.45 431157.04 4851390.8 431165.66 4851390.89 431173.7 4851391.31 431181.21 4851392.48 431189.57 4851394.59 431199.2 4851397.66 431214.64 4851402.95 431241.09 4851413.32 431261.7 4851421.32 431274.83 4851426.01 431281.28 4851427.7 431287 4851428.87 431292.39 4851429.5 431297.79 4851430.03 431308.47 4851430.56 431328.89 4851431.19 431341.68 4851432.14 431348.77 4851432.88 431356.39 4851434.05 431365.38 4851436.16 431374.58 4851438.49 431384.1 4851441.45 431394.58 4851445.26 431403.36 4851448.96 431409.7 4851452.03 431415.41 4851455.84 431420.6 4851459.96 431425.78 4851464.83 431432.87 4851472.55 431441.01 4851482.49 431
```

### HC WFS GetFeature Road Tisno

```
<?xml version="1.0" encoding="UTF-8"?><wfs:FeatureCollection xmlns:wfs="http://www.opengis.net/wfs/2.0" xmlns:xs="http://www.w3.org/2001/XMLSchema" xmlns:gml="http://www.opengis.net/gml/3.2" xmlns:gn="http://inspire.ec.europa.eu/schemas/gn/4.0" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xmlns:gco="http://www.isotc211.org/2005/gco" xmlns:hc_inspire_net="http://inspire.ec.europa.eu/schemas/net/4.0" xmlns:tn="http://inspire.ec.europa.eu/schemas/tn/4.0" xmlns:hc_inspire_tn-ro="http://inspire.ec.europa.eu/schemas/tn-ro/4.0" xmlns:gmd="http://www.isotc211.org/2005/gmd" xmlns:xlink="http://www.w3.org/1999/xlink" xmlns:base="http://inspire.ec.europa.eu/schemas/base/3.3" next="https://geoportal.hrvatske-ceste.hr/inspire/tn-ro/wfs?REQUEST=GetFeature&amp;BBOX=43.79%2C15.62%2C43.81%2C15.66%2Curn%3Aogc%3Adef%3Acrs%3AEPSG%3A%3A4326&amp;VERSION=2.0.0&amp;TYPENAMES=hc_inspire_tn-ro%3ARoad&amp;COUNT=3&amp;SERVICE=WFS&amp;STARTINDEX=3" numberMatched="7" numberReturned="3" timeStamp="2026-10-28T19:26:29.861Z" xsi:schemaLocation="http://inspire.ec.europa.eu/schemas/net/4.0 https://inspire.ec.europa.eu/schemas/net/4.0/Network.xsd http://www.opengis.net/wfs/2.0 http://schemas.opengis.net/wfs/2.0/wfs.xsd http://inspire.ec.europa.eu/schemas/tn-ro/4.0 https://inspire.ec.europa.eu/schemas/tn-ro/4.0/RoadTransportNetwork.xsd http://www.opengis.net/gml/3.2 http://schemas.opengis.net/gml/3.2.1/gml.xsd"><wfs:member><hc_inspire_tn-ro:Road gml:id="Road.1"><hc_inspire_net:beginLifespanVersion>2019-12-31T23:00:00Z</hc_inspire_net:beginLifespanVersion><hc_inspire_net:inspireId><base:Identifier><base:localId>r.1</base:localId><base:namespace>HR.HC.BPJCRH</base:namespace></base:Identifier></hc_inspire_net:inspireId><hc_inspire_net:inNetwork xlink:href="https://geoportal.hrvatske-ceste.hr/inspire/net/wfs?service=wfs&amp;version=2.0.0&amp;request=getFeature&amp;storedQuery_Id=urn:ogc:def:query:OGC-WFS::GetFeatureById&amp;ID=Network.2"/><hc_inspire_net:link xlink:href="https://geoportal.hrvatske-ceste.hr/inspire/tn-ro/wfs?service=wfs&amp;version=2.0.0&amp;request=getFeature&amp;storedQuery_Id=urn:ogc:def:query:OGC-WFS::GetFeatureById&amp;ID=RoadLinkSequence.1-0001"/><hc_inspire_net:link xlink:href="https://geoportal.hrvatske-ceste.hr/inspire/tn-ro/wfs?service=wfs&amp;version=2.0.0&amp;request=getFeature&amp;storedQuery_Id=urn:ogc:def:query:OGC-WFS::GetFeatureById&amp;ID=RoadLinkSequence.1-0002"/><hc_inspire_net:link xlink:href="https://geoportal.hrvatske-ceste.hr/inspire/tn-ro/wfs?service=wfs&amp;version=2.0.0&amp;request=getFeature&amp;storedQuery_Id=urn:ogc:def:query:OGC-WFS::GetFeatureById&amp;ID=RoadLinkSequence.1-0003"/><hc_inspire_net:link xlink:href="https://geoportal.hrvatske-ceste.hr/inspire/tn-ro/wfs?service=wfs&amp;version=2.0.0&amp;request=getFeature&amp;storedQuery_Id=urn:ogc:def:query:OGC-WFS::GetFeatureById&amp;ID=RoadLinkSequence.1-0004"/><hc_inspire_net:link xlink:href="https://geoportal.hrvatske-ceste.hr/inspire/tn-ro/wfs?service=wfs&amp;version=2.0.0&amp;request=getFeature&amp;storedQuery_Id=urn:ogc:def:query:OGC-WFS::GetFeatureById&amp;ID=RoadLinkSequence.1-0005"/><hc_inspire_net:link xlink:href="https://geoportal.hrvatske-ceste.hr/inspire/tn-ro/wfs?service=wfs&amp;version=2.0.0&amp;request=getFeature&amp;storedQuery_Id=urn:ogc:def:query:OGC-WFS::GetFeatureById&amp;ID=RoadLinkSequence.1-0006"/><hc_inspire_net:link xlink:href="https://geoportal.hrvatske-ceste.hr/inspire/tn-ro/wfs?service=wfs&amp;version=2.0.0&amp;request=getFeature&amp;storedQuery_Id=urn:ogc:def:query:OGC-WFS::GetFeatureById&amp;ID=RoadLinkSequence.1-0007"/><hc_inspire_net:link xlink:href="https://geoportal.hrvatske-ceste.hr/inspire/tn-ro/wfs?service=wfs&amp;version=2.0.0&amp;request=getFeature&amp;storedQuery_Id=urn:ogc:def:query:OGC-WFS::GetFeatureById&amp;ID=RoadLinkSequence.1-0008"/><hc_inspire_net:link xlink:href="https://geoportal.hrvatske-ceste.hr/inspire/tn-ro/wfs?service=wfs&amp;version=2.0.0&amp;request=getFeature&amp;storedQuery_Id=urn:ogc:def:query:OGC-WFS::G
```

### DGU AU ATOM

```
<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<feed xmlns="http://www.w3.org/2005/Atom" xmlns:georss="http://www.georss.org/georss" xml:lang="hr">
    <title>Upravne jedinice</title>
    <subtitle>Izvor koji uključuje podatke o sljedećim prostornim jedinicama: država, županije, gradovi i općine, naselja, statistički i popisni krugovi.</subtitle>
    <link href="http://inspire.ec.europa.eu/featureconcept/AdministrativeUnit" rel="describedby" type="text/html"/>
    <link href="https://geoportal.dgu.hr/services/atom/au/xml" rel="self" type="application/atom+xml" hreflang="hr" title="Ovaj dokument"/>
    <link href="https://geoportal.dgu.hr/services/atom/au/en.xml" rel="alternate" type="application/atom+xml" hreflang="en" title="Ovaj dokument na engleskom jeziku"/>
    <link href="https://geoportal.dgu.hr/services/atom/xml" rel="up" type="application/atom+xml" hreflang="hr" title="Dokument usluge preuzimanja"/>
    <id>https://geoportal.dgu.hr/services/atom/au/xml</id>
    <rights>ograničenje javnog pristupa prema članku 13 stavku 1 točki (e) INSPIRE Direktive</rights>
    <updated>2026-10-26T05:33:53.000000+01:00</updated>
    <author>
        <name>Državna geodetska uprava</name>
        <email>irena.magdic@dgu.hr</email>
    </author>
    <entry>
        <title>Upravne jedinice u INSPIRE GML 3.2.1 formatu u ETRS89/LAEA projekciji u komprimiranoj zip datoteci</title>
        <link href="https://geoportal.dgu.hr/services/atom/INSPIRE_Administrative_Units_(AU).zip" rel="alternate" type="application/x-gmz" hreflang="hr" title="Upravne jedinice na području cijele Republike Hrvatske u INSPIRE GML 3.2.1 formatu u ETRS89/LAEA projekciji u komprimiranoj zip datoteci. Sadržaj skupa podataka je na hrvatskom jeziku." length="219327549"/>
        <id>https://geoportal.dgu.hr/services/atom/INSPIRE_Administrative_Units_(AU).zip</id>
        <updated>2026-10-25T06:36:01.000000+01:00</updated>
        <polygon>42.3982 13.2858 46.5321 13.2858 46.5321 19.6392 42.3982 19.6392 42.3982 13.2858</polygon>
        <category term="http://www.opengis.net/def/crs/EPSG/0/3035" label="ETRS89/LAEA"/>
    </entry>
</feed>
```

### EFFIS FWI sloj u capabilities

```

```

### OSM Tisno mostovi

```
most osm=[25219856, 146627895, 335778167] ime=Istočna gomilica ref=D121 highway=primary bridge=movable → most grafa=True
```
