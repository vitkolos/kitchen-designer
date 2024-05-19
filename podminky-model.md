# Formulace omezujících podmínek a matematického modelu

## Zjednodušení

- přesná výška skříněk není předmětem výpočtu
- hloubka skříněk je důležitá kvůli rohům – je to jenom vstupní parametr

## Názvosloví

- zóny
	- kuchyň se dělí na zóny podle účelu jednotlivých skříněk / částí kuchyně
	- základní tři zóny jsou skladování, mytí a vaření
	- dále je důležitá pracovní plocha – ta bývá obvykle mezi zónou mytí a vaření (ale kolem všech zón je potřeba mít nějakou odkládací plochu)
- výška skříněk
	- existují tři základní typy skříněk podle výšky a upevnění – vysoká, nízká a zavěšená
		- vysoké a nízké stojí na zemi, mají stejnou hloubku
		- zavěšené mají cca poloviční hloubku a visí nad pracovní plochou, jejich horní stěna je zarovnána s vysokými skříňkami
	- oblast s jedním typem skříněk pracovně označíme jako *pásmo*

## Omezující podmínky a parametry fitness funkce

- databáze skříněk
	- lze použít pouze skříňky z nabídky
	- každá kuchyň musí mít dřez, sporák, …
- vlastnosti prostoru
	- rozměry místnosti
	- kde jsou zdi (ne každá skřínka je hezká ze všech stran)
	- okna a dveře
		- odstup vysokého nábytku od oken má být alespoň 150 mm
		- od dveří aspoň 100 mm
	- překážky – topení, výklenky apod.
	- požadovaný tvar kuchyně (u kterých stěn mají skříňky stát)
- rozmístění instalací
	- odtah (ventilace), voda, plyn, elektřina
	- pozor: někdy dává smysl změnit instalace, pokud to přinese větší ergonomii
- preference zákazníka
	- více úložného prostoru, nebo pracovní plochy?
	- „aspoň jedna úložná skříňka musí být 80 cm široká“
	- které typy spotřebičů je potřeba zahrnout/vyloučit (myčka, lednička apod.)
	- pravák/levák – z toho vyplývá nejvhodnější pořadí zón
- předvolby designéra
	- na daném místě (v jeho okolí) má/nemá být konkrétní skříňka/zóna/pásmo
- pracovní trojúhelník (skladování, mytí, vaření)
	- obvod nejvýše 8 m
	- délka strany mezi 1,2 a 2,7 m
	- žádné překážky
- vizuální atraktivita dělení skříněk
	- svislé čáry (dělení zavěšených a nízkých skříněk) by na sebe měly navazovat
	- je vhodné, když šířky skříněk tvoří pravidelný vzor
		- několik skříněk vedle sebe má stejnou šířku
		- šířky skříněk se střídají – širší, užší, širší, užší
		- další vzory pravděpodobně nejsou obvyklé ani na ně není prostor
- dřez a sporák
	- ne v rohu, ne těsně u zdi
	- neměly by se *do nich* otevírat dveře
	- odkládací plocha vedle dřezu – šířka aspoň 250 mm, lépe 350 nebo 500 mm
		- pokud vedle dřezu není pracovní plocha, tak alespoň 600 mm
	- u sporáku bez vlastní odstavné plochy musí být plocha asopň 200 mm široká
	- pracovní plocha z obou stran sporáku i dřezu by neměla být menší než 400 mm
	- dřez a sporák by neměly být vedle sebe – ideální vzdálenost je 1200 mm
	- mezi plynovým sporákem a bokem potravinové skříně by mělo být minimálně 300 mm
	- sporák by neměl být blízko rohu pracovní desky
- pracovní plocha
	- typicky mezi sporákem a dřezem
	- šířka aspoň 950–1000 mm, v malých bytech pro 3 osoby lze i 650 mm
	- optimální šířka 1200 mm
- myčka nádobí
	- v blízkosti dřezu
	- nesmí za ní být žádné vývody
	- otevřená myčka nesmí bránit otevření dvířek
- pečicí trouba
	- v těsné blízkosti odkládací plocha
- lednice
	- musí být přístupná i těm, co právě nevaří
	- musí být dostupná při ukládání nákupu
	- nesmí být daleko od sporáku
- rohové skříňky
	- pokud se přidá jenom jedna skříňka, není kuchyň tvaru L efektivní (přidaná skříňka zablokuje roh), lepší je nechat kuchyň ve tvaru I
	- existuje více variant rohových skříněk

## Úsečkový model kuchyně

- pro jednoduchost se dají zanedbat hloubka a výška skříněk a do jisté míry i rozmístění částí kuchyně v prostoru
- budeme uvažovat jednotlivé části kuchyňské linky jako vzájemně související úsečky
	- skříňky jsou pak „obarvení“ jejich částí
- částem linky, kam lze umístit všechny tři typy skříněk (vysoké, nízké i zavěšené), budou odpovídat dvě úsečky – např. vysoké skříňky pak budou současně zabírat odpovídající část horní i dolní úsečky
- typicky budeme požadovat, aby žádná část úsečky nebyla bez skříněk a aby se skříňky nepřekrývaly
- na vztazích jednotlivých úseček bude záležet pouze v několika situacích
	- návaznost dělení nízkých a zavěšených skříněk
	- souvislost sporáku a digestoře
	- vysoké skříňky se nesmí „roztrhnout“
	- pracovní trojúhelník – tady záleží na konkrétním prostorovém uspořádání úseček
	- rohová skříňka – u kuchyní tvaru L
	- nezávislé otevírání více skříněk – typicky blízko rohu, např. v souvislosti s myčkou nádobí
- ne všechna rozmístění skříněk jsou platná a ne všechna jsou stejně dobrá
	- některé požadované vlastnosti popíšeme ostrými podmínkami, takže zakážeme řešení, která je nesplňují
	- definujeme fitness funkci, což bude zobrazení z množiny všech validních řešení do uspořádané množiny (pravděpodobně reálných čísel)
		- pravidla budou typicky dvojího druhu – globální (např. pro celkovou velikost pracovní plochy) a lokální (např. pro vzdálenost dřezu od myčky)
	- je možné oba přístupy kombinovat – ostré podmínky lze doplnit fitness pravidly
- cílem je, aby se libovolný požadavek na vlastnosti kuchyně popsat nějakým z těchto způsobů nebo jejich kombinací
	- úprava úseček
	- omezení množiny použitelných skříněk
	- globální ostré pravidlo
	- lokální ostré pravidlo
	- globální fitness pravidlo
	- lokální fitness pravidlo

## Vyjádření pomocí Pyomo

- základní přístup
	- každou úsečku rozdělíme na $n$ částí, kde $n$ bude vyplývat z délky konkrétní úsečky
	- pro každou úsečku chceme získat seznam dvojic (část, nábytek), který popíše výsledné rozmístění jednotlivých kusů nábytku na úsečce, a seznam délek jednotlivých částí úsečky
	- budeme mít jedno velké pole všech částí úseček
- potřebné vyjadřovací prostředky
	- jedna skříňka z databáze na několika místech najednou
		- lze řešit více instancemi jedné skříňky v databázi
	- rozměrové omezení pro šířku skříňky
		- asi stačí minimum a maximum (ty se můžou i rovnat)
		- v případě více možných šířek (např. 40, 60, 80) může pro každou šířku existovat nová instance v databázi
	- okrajové skříňky – pokud linka není ode zdi ke zdi, na kraji může stát jen skříňka k tomu určená
		- úsek bude označený jako krajní, bude vyžadovat umístění krajní skříňky (tzn. návrh, kde v úseku nebude žádná skříňka, nebude povolený)
	- umístění středů jednotlivých zón v kuchyni – kvůli vzdálenosti od instalací i kvůli rozměrům pracovního trojúhelníku
	- rozměry pracovní plochy či úložného prostoru
	- „aspoň jedna úložná skříňka musí být aspoň 80 cm široká“
	- požadavky na typy skříněk – např. kuchyň musí obsahovat dřez, sporák a ledničku
	- vzdálenost skříňky od středu zóny – minimalizace pro udržení kompaktnosti zón
	- nařízení/zákaz konkrétního typu skříňky v konkrétní oblasti
	- vizuální atraktivita dělení – návaznost svislých čar a pravidelné vzory
		- zatím se mi povedlo implementovat zvýhodnění stejně/podobně širokých skříněk vedle sebe (penalizuje se rozdíl šířky aktuální skříňky od té předchozí)
	- odkládací plocha o nějaké minimální šířce v okolí určitých typů skříněk (sporák, dřez)
	- šířka nejdelší souvislé pracovní desky
	- návaznost sporáku a digestoře, dále také obou „částí“ vysokých skříněk
	- rohová skříňka
