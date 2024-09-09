# Automatický plánovač kuchyní (základní verze)

| Vít Kološ, 2. ročník, IPP | letní semestr 2023/2024 | NPRG045 Ročníkový projekt |
| - | - | - |

## Anotace

Program navrhne možné rozložení skříněk a spotřebičů v kuchyni, přičemž vychází ze zadaného prostorového popisu kuchyně a databáze skříněk (respektive kuchyňských spotřebičů). Při návrhu kuchyně používá metody lineárního programování, model je interně popsán v nástroji Pyomo a k nalezení řešení se používá řešič Gurobi. Jedná se primárně o *proof of concept*, nikoli o finální verzi softwaru, kterou by mohl běžně použít koncový zákazník.

## Uživatelská dokumentace

### Použití programu

Automatizované plánování kuchyně sestává z několika fází:

1. Příprava vstupu: Součástí vstupních dat musejí být údaje o tom, kam v kuchyni je možné skříňky (a spotřebiče) rozmístit. Je nutné programu také předat databázi skříněk. Obvykle se hodí specifikovat, které typy spotřebičů je nutné v návrhu zahrnout.
2. Výpočet, jehož délka se obvykle pohybuje v řádu minut.
3. Získání výstupu: Výsledný návrh je kromě textového formátu dostupný rovněž prostřednictvím grafického rozhraní.
4. Případná úprava vstupních dat a opakování výpočtu.

### Spuštění z příkazové řádky

Před prvním spuštěním je nutné nainstalovat nezbytné balíčky pomocí `pip install -r requirements.txt`.

Program se spouští příkazem `python kitchendesigner`. Za ním následují dva nutné parametry: 1. umístění vstupního souboru, 2. umístění výstupního souboru. Ke vstupu i výstupu se používá formát JSON (viz níže).

Dále lze použít tyto volitelné parametry:

- `-m`, `--model` – takto lze specifikovat umístění souboru, do nějž se má vypsat vyřešený model (tedy interní sada proměnných, lineárních omezujících podmínek apod.)
- `-s`, `--solver` – místo Gurobi (`gurobi_direct`) je možné použít solvery `cbc` a `glpk`
- `--structure` – tento flag aktivuje výpis struktury interního modelu (závislosti mezi proměnnými, podmínkami atd.)

### Formát vstupu

Soubor formátu JSON se vstupními daty musí odpovídat schématu `kitchendesigner/input.schema.json`. Hlavní vstupní objekt může/musí mít následující atributy:

- `kitchen_parts` – (povinný) seznam částí kuchyňské linky, jedna část má tyto atributy:
	- `name` – název části (pro použití v dalších částech vstupu)
	- `is_top` – jedná se o horní (nebo spodní) část linky?
	- `position` – údaje pro přesnou lokalizaci části linky
		- `x`, `y` – souřadnice levého dolního rohu části (pozor: je nutné, aby se celý plán kuchyně pohyboval v určitých mezích, dolní mezí je nula, tedy žádná část kuchyně nesmí zasahovat mimo první kvadrant, horní mez se definuje v konstantách, viz níže)
		- `angle` – natočení části
		- `group_number` – číslo skupiny (jsou-li dvě části linky nad sebou, měly by být ve stejné skupině)
		- `group_offset` – odsazení od levého okraje skupiny (obvykle může být 0)
	- `width` – šířka části
	- `depth` – hloubka skříněk (není předmětem optimalizace)
	- `edge_left`, `edge_right` – stojí levý/pravý kraj části volně v prostoru? (pokud je kuchyňská linka ode zdi ke zdi, budou obě hodnoty `false`)
- `walls` – (volitelný) seznam objektů popisujících umístění zdí. Při použití `wall_distance` (viz níže) je důležité, aby byl tento seznam součástí vstupu. Každý prvek seznamu má atributy:
	- `group` – číslo skupiny, kterou zdi ohraničují
	- `left` – „offset“ levé zdi (v základním případě bude 0)
	- `right` – „offset“ pravé zdi
- `corners` – (volitelný) seznam rohů, musí být zadán, pokud je kuchyň tvaru L nebo U. Každý roh má tyto atributy:
	- `part1_name` – název první *části kuchyně*
	- `part1_left` – přiléhá první část do rohu levým koncem (tedy tím s nižším offsetem)?
	- `part2_name`, `part2_left` – obdobně pro druhou část (pozor: části kuchyně, které roh sdílejí, se musejí v daném rohu překrývat)
- `placement_rules` – (volitelný) seznam pravidel ovlivňujících (ne)umístění skříněk do návrhu, každé pravidlo má tyto atributy:
	- `rule_type` – může být `exclude` (specifikované skříňky se nemají v návrhu na daném místě objevit) nebo `include` (na daném místě se v návrhu musí objevit alespoň jedna skříňka ze specifikované skupiny)
	- `area` – může být `kitchen` (pravidlo se týká celého návrhu kuchyně), `group` (týká se skupiny částí kuchyně) nebo `group_section` (týká se pouze určitého úseku části kuchyně)
	- `attribute_name` a `attribute_value` dohromady popisují, jaké skupiny skříněk se pravidlo týká. Název atributu může být `name`, `type` nebo `zone` (viz `available_fixtures` níže).
	- `group`, `section_offset` a `section_width` dále upřesňují oblast platnosti pravidla (pro `area` rovnou `group` nebo `group_section`)
- `relation_rules` – (volitelný) seznam pravidel ovlivňujících vztahy mezi skříňkami a dalšími objekty v návrhu
	- `rule_type` – typ pravidla, může být:
		- `target` – chceme minimalizovat vzdálenost skříňky od určitého bodu
		- `min_distance` – vyžadujeme minimální vzdálenost skříňky od jiné specifikované skříňky
		- `wall_distance` – preferujeme, pokud má skříňka ode zdi alespoň zadanou vzdálenost
		- `min_worktop` – vyžadujeme, aby v bezprostřední blízkosti skříňky byla k dispozici pracovní plocha o zadané minimální šířce
		- `one_wide` – vyžadujeme, aby alespoň jedna skříňka daného typu byla aspoň takto široká
	- `fixture_type` – typ skříňky, jíž se pravidlo týká (pozor: pro jeden typ skříňky může existovat nejvýše jedno pravidlo daného typu)
	- `fixture_type2` – pro pravidlo `min_distance`
	- `length` – pro pravidla se vzdálenostmi a šířkami
	- `x`, `y` – pro pravidlo `target`
- `preferences` – (volitelný) objekt zachycující preference uživatele, má tyto vlastnosti:
	- `storage` – priorita, kterou má pro uživatele množství úložného prostoru (čísla větší než jedna slouží ke zvýšení priority, čísla mezi nulou a jedničkou ke snížení, záporné hodnoty vedou k minimalizaci množství úložného prostoru)
	- `worktop` – priorita, kterou má pro uživatele šířka pracovní plochy
- `constants` – (povinný) objekt s konstantami modelu, konstanty jsou tyto:
	- `min_fixture_width` – minimální povolená šířka skříňky
	- `max_fixture_width` – maximální povolená šířka skříňky
	- `max_canvas_size` – horní mez souřadnic v plánu kuchyně (viz výše)
	- `vertical_continuity_tolerance` – jak moc se od sebe můžou lišit polohy okrajů skříněk, aby na sebe vizuálně navazovaly
	- `width_same_tolerance` – jak moc se od sebe mohou lišit šířky sousedních skříněk, aby vypadaly stejně
	- `width_different_tolerance` – jak moc se od sebe musí lišit šířky sousedních skříněk, aby vypadaly rozdílně (jako úzká a široká vedle sebe)
	- `width_penult_similar_tolerance` – jak moc se od sebe mohou lišit šířky skříněk, aby vypadaly stejně (za předpokladu, že skříňky nejsou sousední, ale je mezi nimi ještě jedna další skříňka, která je rozdílně široká)
- `zones` – (povinný) seznam kuchyňských zón (např. vaření, mytí, skladování), každá zóna má tyto atributy:
	- `name` – název zóny
	- `is_optimized` – preferujeme, jsou-li skříňky dané zóny pohromadě?
	- `has_optimal_center` – chceme specifikovat, poblíž jakého bodu v kuchyni by se skříňky dané zóny měly nacházet? (to má smysl, jen když má `is_optimized` hodnotu `true`)
	- `optimal_center` – pomocí souřadnic `x`, `y` specifikujeme polohu optimálního středu zóny (pokud je `has_optimal_center` rovno `true`)
	- `color` – barva zóny pro účely nákresu plánu kuchyně
- `available_fixtures` – (povinný) seznam skříněk (a spotřebičů), každá skříňka může mít tyto atributy:
	- `name` – název skříňky
	- `type` – typ skříňky
	- `zone` – název zóny
	- `position_top` – má být skříňka umístěna v horní řadě?
	- `position_bottom` – má být skříňka umístěna v dolní řadě? (je-li skříňka vysoká, musí být `position_top` i `position_bottom` rovny `true`, pak skříňka zasahuje do obou řad v dané *skupině*)
	- `width_min` – minimální šířka skříňky
	- `width_max` – maximální šířka skříňky
	- `width_min2` a `width_max2` lze použít u rohových skříněk, pokud má skříňka v jedné části rohu jiné rozměry než v druhé
	- `storage` – množství úložného prostoru v konkrétní skříňce (typicky na stupnici od nuly do pěti)
	- `has_worktop` – je na skříňku možné umístit pracovní desku?
	- `allow_edge` – je možné skříňku umístit na kraj (stojící volně v prostoru)?
	- `is_corner` – jedná se o rohovou skříňku?
	- `allow_multiple` – je možné mít v jednom návrhu několik instancí (až 3) této skříňky?

### Formát výstupu

Soubor formátu JSON se výstupními daty odpovídá schématu `kitchendesigner/output.schema.json`. Hlavní výstupní objekt má atributy odpovídá jednotlivými částem kuchyně (jsou označeny jejich názvy). Každá část kuchyně obsahuje atribut `padding`, to je šířka volného prostoru od levého kraje dané části. Obsahuje rovněž atribut `fixtures`, to je seznam skříněk (a spotřebičů), které jsou v návrhu umístěny v dané části kuchyně. Pořadí umístění odpovídá pořadí v seznamu. Každý prvek seznamu má atribut `fixture`, tam je název dané skříňky, a atribut `width`, což je šířka dané skříňky v návrhu.

Vizuální výstup v grafickém rozhraní odpovídá pohledu shora, přičemž horní části kuchyňské linky jsou pro přehlednost posunuty – jejich reálnému umístění odpovídá šrafovaná oblast.

## Praktické použití programu v kuchyňském studiu

Designér nejprve na základě rozhovoru se zákazníkem a poskytnutého plánu kuchyně navrhne možný tvar kuchyně a s ním související rozmístění jednotlivých částí kuchyňské linky. Rovněž z databáze skříněk a spotřebičů vybere ty, které se v návrhu můžou objevit a určí, jaké typy spotřebičů se tam objevit musí. Případně pak sestaví seznam dalších pravidel, která se při automatizovaném návrhu mají použít.

Nyní lze vstupní data předat tomto programu a vyčkat, dokud nenalezne řešení. To pak designér může dále upravovat – ať už automatizovaně s pomocí programu (úpravami vstupních dat) nebo ručně v návrhovém nástroji. Dalšími fázemi návrhu jsou pak volba vybavení skříněk (rozmístění šuplíků apod.) a výběr stylu kuchyně (typicky podle preferencí zákazníka). Nakonec lze výsledek prezentovat zákazníkovi.

## Vlastnosti programu a prostor pro zlepšení

### Pracovní trojúhelník a rozmístění zón

Při návrhu kuchyně a hledání vhodného rozmístění skříněk se bere v úvahu tzv. pracovní trojúhelník, tedy vhodné rozmístění a vzájemné vzdálenosti zón (vaření, mytí, skladování). Rozhodl jsem se to přímo nezohledňovat v modelu, místo toho převádím zodpovědnost na designéra. Ten tedy může navrhnout rozmístění zón, ve vstupních datech se to označuje jako `optimal_center` (tedy optimální střed dané zóny).

Rozhodl jsem se, že umožňím shlukování skříněk (spotřebičů) stejné zóny i bez uvedení optimálního středu. Toho jsem docílil tak, že pro danou zónu počítám její reálný střed. Ve fitness funkci se pak zvýhodňuje menší vzdálenost skříněk dané zóny od jejího středu. Nezávisle na tom se zvýhodňuje malá vzdálenost reálného středu od optimálního středu zóny. To je však poměrně *výpočetně náročné*, tedy možným krokem ke zrychlení výpočtu by bylo zrušení tohoto mezikroku s výpočtem reálného středu zóny.

### Konstanty

Při formulaci modelu se používá několik konstant, které se týkají rozsahů proměnných a „tolerancí“ (při posuzování šířek, rozměrů apod.). Dále se v programu vyskytují konstanty týkající se počtu *klonů* u vícenásobných skříněk a zaokrouhlení při výpočtu goniometrických funkcí. Není zcela jasné, které konstanty by měl uživatel poskytnout na vstupu (v rámci objektu `constants`, nebo dokonce přímo v databázi skříněk) a které by měly být definovány interně v programu.

### Ošetření vstupu

Jelikož se jedná pouze o základní verzi programu, nekladl jsem zvláštní důraz na validaci vstupu (přestože se používá validace oproti JSON schématu).

U některých případů vstupu, který nelze přímo předat modelu, ale v principu není zcela chybný, by bylo možné uvažovat o jeho korekci pro účely modelu a následném převedení zpět pro účely výstupu (např. pokud by se části kuchyně nenacházely v požadovaném rozsahu souřadnic, bylo by je možné dvakrát přeškálovat – po načtení vstupu a před výpisem výstupu).

### Pomalé hledání řešení

Nalezení optimálního řešení někdy trvá i několik minut. Bylo by žádoucí tento čas snížit, jelikož proces automatizovaného návrhu obvykle sestává z několika iterací – na základě nalezeného řešení je potřeba upravit vstupní parametry a hledat nové řešení.

Jelikož nemám žádné hlubší vzdělání v oblasti lineárního programování, nedovedu snadno posoudit, zda jsem sestavil dostatečně efektivní model. Zdá se však, že řešení nejvíc zpomalují ty složky fitness funkce, které počítají se šířkou či vzdáleností, tím totiž vzniká mnoho *symetrií*.

Je třeba zmínit, že vzhledem k povaze úlohy není nutné vždy najít optimum, stačí i dostatečně dobré suboptimální řešení – tedy to by mohl být také způsob zrychlení programu, prostě bychom nečekali na nalezení optima. (S tím souvisí fakt, že užitečnější by bylo, pokud by program vrátil několik různých návrhů, než když vrátí jeden – byť je optimální. Tedy to je také námět pro další rozvoj.)

### Fitness funkce (objective)

Co se týče fitness funkce, je potřeba posoudit, zda sestává ze správných složek (např. nejsem zcela přesvědčen o tom, že je vhodné, aby se maximalizoval počet přítomných skříněk v návrhu). Dále by bylo dobré jednotlivé složky vyvážit (pronásobením různými koeficienty), aby byly výsledné návrhy co nejlepší. V tuto chvíli mi však není znám žádný přímočarý přístup k tomuto problému.

S překvapením jsem zjistil, že pokud změním pořadí sčítanců ve fitness funkci, program nalezne jiné optimum. Napadá mě vysvětlení, že oběma řešením přiřadí fitness funkce stejnou hodnotu, to však ještě budu muset prověřit.

Počítám s tím, že uživatel bude moct fitness funkci ovlivnit prostřednictvím `preferences`, momentálně se to týká jenom pracovní plochy a úložného prostoru. Tyto uživatelské koeficienty bych rád nastavil jako *mutable* parametry, aby se případné přepočítání modelu dalo provést rychleji (bude však nezbytné místo rozhraní `gurobi_direct` použít `gurobi_persistent`).

### Nedostatky současných řešení

Během testování modelu na reálných kuchyních jsem objevil dva základní nedostatky:

1. Umístění vysoké skříňky doprostřed řady nízkých skříněk je penalizováno pouze ztrátou pracovní plochy. Proto se v řešeních tento (obvykle nežádoucí) úkaz vyskytuje poměrně často. K nápravě problému by mohlo vést *odměnění* delších úseků skříněk stejné výšky nebo penalizace vysokých skříněk mezi dvěma nízkými. Pravděpodobně by však bylo nezbytné přidat příznak odlišující vysoké skříňky (nebo ledničky apod.) od „dvojic“ (např. sporáku a digestoře).
2. Pravidlo `target` nebylo v konkrétním případě (jednalo se o kuchyň popsanou v `data_output/medium.json`) dostatečně účinné.
