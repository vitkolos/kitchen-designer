# Kitchen Designer
## Záměr

Řešíme problém automatizovaného návrhu kuchyní, konkrétně rozmístění skříněk, spotřebičů a dalších kuchyňských prvků na lince vzhledem k zadanému interiéru, požadavkům zákazníka a dalším omezujícím podmínkám. Tento problém formulujeme jako instanci matematického programování a následně hledáme optimální / co nejlepší řešení pomocí existujících řešičů.

## Podmínky získání zápočtu

Pro získání zápočtu musí student:

1. Formalizovat matematický model problému v základní podobě. Základní podobou se myslí:
   
   a. Alespoň 5 z následujících 11 prvků a omezujících podmínek: minimální vybavenost kuchyně, správné rozměry skříněk, rozměry místnosti, rozmístění instalací, preference zákazníka, předvolby designéra, pracovní trojúhelník, vizuální atraktivita dělení, vzájemné vztahy skříněk, speciální požadavky na umístění, rohové skříňky
   b. Kuchyň je tvaru I (v reálu se řeší složitější tvary jako je L, U a další)
   
2. Implementovat základní model tak, aby byl řešitelný existujícím řešičem (např. v knihovně `pyomo`, `nevergrad`, nebo obdobných)
3. Prokázat funkčnost modelu formulací několika instancí a jejich vyřešením.
4. Napsat krátký text (1-2 strany), který nastíní, jak by bylo potřeba model rozšířit, aby byl použitelný v praxi, a co by předcházelo a následovalo již implementované fázi (myšleno kde se vezme instance pro řešič, a jak se řešení zpracuje a prezentuje zákazníkovi). Stejně tak popsat zdroj a propojení s reálnou databází dílů atd.
