# Automatizovaný návrh členění kuchyně

## Návštěva kuchyňského studia

Zákazník, který přichází do kuchyňského studia, zná

- půdorys své kuchyně (tedy rozměry oblasti, kde by kuchyně / kuchyňská linka měla být),
- rozmístění zdí, oken a dveří,
- místa, kde je vyvedena voda a odpad a kde je odvětrání,
- maximální cenu, kterou je ochoten za kuchyň zaplatit.
- Může mít nějaké požadavky na velikost pracovní plochy a množství úložného prostoru.
- Možná má nějaké další představy např. o tvaru kuchyně nebo o velikosti sporáku, myčky…

Tvorba návrhu má několik fází:

1. volba tvaru kuchyně – zda bude kuchyň rovná nebo ve tvaru L či U, zda bude mít ostrůvek,
2. rozčlenění kuchyně na zóny – podle účelu (úložný prostor, mytí, příprava, vaření, …), někde budou vysoké skříňky, jinde nízké skříňky s pracovní deskou (nad nimi typicky bývají další skříňky nebo digestoř),
3. dělení zón na jednotlivé skříňky – tedy určení šířek jednotlivých skříněk,
4. volba vybavení skříněk – co bude uvnitř jaké skříňky, kde budou šuplíky apod.,
5. volba stylu kuchyně – výběr barev a materiálů podle vzorníku.

Zákazník mnohdy neví, co přesně chce. Do daného prostoru lze se typicky navrhnout více tvarů kuchyní – zákazník by těch návrhů rád viděl několik, aby se mohl rozhodnout (nakonec zvolí třeba podle ceny). Příprava jednoho návrhu ale designérovi zabere spoustu času.

Nejvíc času (snad třeba hodinu) designér obvykle stráví rozpočítáváním šířky skříněk. Jednak se totiž snaží dodržet základní návrhové principy (sporák by neměl být vedle ledničky), rovněž musí být v souladu s tvarem místnosti a umístěním ventilace / přívodu vody (to ale neurčuje umístění sporáku/dřezu pevně, jen jakousi oblast, kde by měl být). Dále ho omezují standardní rozměry spotřebičů, případně skříněk. Při tom všem chce vytvořit *pěkný* návrh, tedy se mimo jiné snaží o to, aby byly šířky skříněk nějak pravidelné – aby byly všechny stejné nebo aby se střídaly. Přičemž horní a dolní řada skříněk v tom nejsou nezávislé, ale musí se nějak rozumně doplňovat.

## Základní verze zadání

Primárním řešeným problémem jsou druhá a třetí fáze návrhu – tedy rozdělení na zóny a jejich dělení na skříňky. Tyhle dvě fáze jsou v podstatě nezávislé.

### Popis programu

#### Globální parametry

- abstraktní reprezentace skříněk
	- skříňky mají nějaké klíčové vlastnosti – jestli jsou vysoké/nízké (případně horní/dolní), jestli obsahují myčku/sporák/dřez apod., jestli můžou být v rohu nebo na kraji
	- skříňky mají omezenou šířku (buď výčtem hodnot, nebo intervalem)
	- skříňky mají (minimální) cenu, ta se počítá dynamicky podle šířky
	- naopak vzhled skříněk (materiál apod.) není důležitý

#### Vstup od zákazníka

- rozměry prostoru, pozice zdí
- umístění oken a dveří
- umístění instalací – voda, odpad, odvětrání, …
- tvar kuchyně (I, L, U, ostrůvek?)
- preference úložného prostoru nebo pracovní plochy
	- větší pracovní plocha obvykle implikuje menší úložný prostor (méně vysokých a více nízkých skříněk)
- maximální cena kuchyně
- případně další požadavky – velikost sporáku, myčky…

#### Výstup

- pokud lze požadavky splnit, algoritmus najde vizuálně nejpřijatelnější řešení z pohledu členění
	- může být vhodné postupně nabídnout více výsledků
- formát výstupu
	- strukturovaný textový formát (např. JSON)
	- kvůli možnosti snadného posouzení výsledků by byl vhodný jednoduchý vizualizátor, co by výsledek vykreslil (třeba jako statické SVG)
		- teoreticky lze použít již existující vizualizační nástroj
		- skříňky by mohly být barevně kódované podle účelu (respektive zóny)

### Technologie a praktické otázky

- na programovacím jazyku nezáleží
	- neočekává se, že by tam bylo tolik kódu, aby to nebylo možné v případě potřeby snadno přepsat
	- algoritmus pravděpodobně poběží na serveru
- je potřeba posoudit vhodné algoritmy a přístupy
	- k rozpočítávání šířky skříněk se genetický algoritmus možná nehodí
	- naopak geometrické řešiče by zde mohly dávat smysl
	- nejtěžší bude definovat fitness funkci, která bude zvýhodňovat vizuální vzory (pokud jde o šířky skříněk)
- licence řešiče není v experimentální fázi limitující
- kód bude zveřejněn pod vhodnou licencí (pravděpodobně MIT)
- role konzultanta se ujme Ing. Jiří Hon, Ph.D. ([Salusoft89 s.r.o.](http://www.salusoft89.cz/), [ORCID](https://orcid.org/0000-0002-3321-9629))
- Salusoft89 může zprostředkovat konzultace s designéry

### Stávající řešení a související články

Z toho, co víme (Salusoft89 spolupracuje s mnoha různými firmami), nikdo v Česku a Slovensku nepoužívá takovou automatizaci návrhu. Ani nevíme o tom, že by v Německu nebo ve Spojených státech používali něco sofistikovanějšího.

V *nábytkařině* se používají rigidní desktopové softwary (např. Carat, Cabinet Vision, imosCAD, …). Ty obvykle neumožňují integraci programů, které by automatizaci zajistily. Přitom však základním předpokladem pro zefektivnění celého procesu návrhu je možnost automatizované výstupy v každé z jeho jednotlivých fází jednoduše ručně korigovat a dotvářet. Salusoft89 vyvíjí vlastní webovou aplikaci pro 3D konstrukci nábytku, ve které by úprava automatizovaných výstupů měla být naopak snadná a rychlá.

Na internetu jsou dostupné různé plánovače kuchyní, ty však trpí zmíněnými neduhem, nelze v nich ovlivnit jednotlivé kroky procesu návrhu (typicky není možné vybrat rozmístění jednotlivých zón). Rovněž není jasné, nakolik jsou tyto nástroje integrovány do interních procesů jednotlivých firem, tedy zda přispívají k efektivitě výroby a prodeje nebo jde především o prostředky marketingu.

Automatizace návrhu kuchyně se dotýkají články [Automatic Rule-Based Kitchen Layout Design](https://scholar.google.com/scholar_lookup?title=Automatic+Rule-Based+Kitchen+Layout+Design&author=Pejic+P&author=Mikic+M&author=Milovanovic+J&publication+year=2019) a [Linear kitchen layout design via machine learning](https://www.cambridge.org/core/journals/ai-edam/article/linear-kitchen-layout-design-via-machine-learning/04FD1D9B1D72A4355EB7C3B3B2578F4F). Ani jeden z nich se nezabývá rozpočítáváním skříněk.

### Možnosti rozšíření

Program by mohl pokrýt všechny fáze návrhu kuchyně.

Program by do scény nakonec mohl umístit další prvky, které ke kuchyni patří – stůl, židle, obrázky, dekorace, hrnečky, … Tak by se návrh stal vizuálně atraktivnější.
