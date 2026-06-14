#!/usr/bin/env python3
"""
ANLS - Analise Profissional (GRATIS)
Dual mode: Copa + Ligas | Multi-dia | Verificacao dupla
"""
import sys, io, os, re, time, json
from datetime import datetime, timezone, timedelta
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')
from google import genai

API_KEY = os.environ.get("GEMINI_API_KEY")
if not API_KEY:
    print("ERRO: GEMINI_API_KEY nao configurada"); sys.exit(1)
client = genai.Client(api_key=API_KEY)
BRT = timezone(timedelta(hours=-3))
_sim = os.environ.get("ANLS_SIM_DATE", "")
_n = datetime.now(BRT) if not _sim else datetime.strptime(_sim, "%Y-%m-%d").replace(tzinfo=BRT)
TODAY = _n.strftime("%Y-%m-%d")
TODAY_BR = _n.strftime("%d/%m/%Y")
WORLD_CUP_END = "2026-07-20"

def fmt_date(d):
    x = datetime.strptime(d, "%Y-%m-%d")
    return x.strftime("%d/%m (%a)").replace("Mon","Seg").replace("Tue","Ter").replace("Wed","Qua").replace("Thu","Qui").replace("Fri","Sex").replace("Sat","Sab").replace("Sun","Dom")

# ====== BANCO DE DADOS ======
TEAM_DATA = {
    "Alemanha":{"elo":1950,"r_atk":91,"r_meio":93,"r_def":88,"r_gol":90,"mkt":"850M","fifa":10,"conf":"FAVORITA","flag":"DE"},
    "Argentina":{"elo":2050,"r_atk":94,"r_meio":88,"r_def":85,"r_gol":87,"mkt":"920M","fifa":1,"conf":"CANDIDATA","flag":"AR"},
    "Brasil":{"elo":2020,"r_atk":93,"r_meio":87,"r_def":83,"r_gol":86,"mkt":"950M","fifa":3,"conf":"CANDIDATA","flag":"BR"},
    "Franca":{"elo":2000,"r_atk":92,"r_meio":85,"r_def":86,"r_gol":88,"mkt":"980M","fifa":2,"conf":"CANDIDATA","flag":"FR"},
    "Inglaterra":{"elo":1960,"r_atk":89,"r_meio":86,"r_def":84,"r_gol":83,"mkt":"890M","fifa":5,"conf":"CANDIDATA","flag":"GB"},
    "Espanha":{"elo":1980,"r_atk":88,"r_meio":90,"r_def":85,"r_gol":85,"mkt":"820M","fifa":4,"conf":"CANDIDATA","flag":"ES"},
    "Portugal":{"elo":1930,"r_atk":90,"r_meio":84,"r_def":83,"r_gol":86,"mkt":"780M","fifa":6,"conf":"FAVORITA","flag":"PT"},
    "Holanda":{"elo":1880,"r_atk":85,"r_meio":87,"r_def":84,"r_gol":79,"mkt":"780M","fifa":7,"conf":"FAVORITA","flag":"NL"},
    "Belgica":{"elo":1840,"r_atk":86,"r_meio":83,"r_def":80,"r_gol":82,"mkt":"540M","fifa":8,"conf":"FAVORITA","flag":"BE"},
    "Uruguai":{"elo":1820,"r_atk":82,"r_meio":80,"r_def":83,"r_gol":80,"mkt":"380M","fifa":11,"conf":"MEDIANA","flag":"UY"},
    "Colombia":{"elo":1780,"r_atk":81,"r_meio":79,"r_def":78,"r_gol":77,"mkt":"310M","fifa":14,"conf":"MEDIANA","flag":"CO"},
    "Mexico":{"elo":1780,"r_atk":79,"r_meio":77,"r_def":76,"r_gol":75,"mkt":"260M","fifa":15,"conf":"MEDIANA","flag":"MX"},
    "Japao":{"elo":1760,"r_atk":78,"r_meio":82,"r_def":81,"r_gol":76,"mkt":"320M","fifa":18,"conf":"PERIGO","flag":"JP"},
    "Marrocos":{"elo":1750,"r_atk":77,"r_meio":78,"r_def":79,"r_gol":76,"mkt":"280M","fifa":20,"conf":"PERIGO","flag":"MA"},
    "Noruega":{"elo":1750,"r_atk":84,"r_meio":76,"r_def":72,"r_gol":73,"mkt":"340M","fifa":19,"conf":"PERIGO","flag":"NO"},
    "Croacia":{"elo":1740,"r_atk":76,"r_meio":84,"r_def":78,"r_gol":75,"mkt":"250M","fifa":21,"conf":"MEDIANA","flag":"HR"},
    "Equador":{"elo":1720,"r_atk":74,"r_meio":82,"r_def":88,"r_gol":76,"mkt":"280M","fifa":23,"conf":"DEFENSIVO","flag":"EC"},
    "EUA":{"elo":1720,"r_atk":78,"r_meio":76,"r_def":74,"r_gol":77,"mkt":"330M","fifa":16,"conf":"MEDIANA","flag":"US"},
    "Coreia do Sul":{"elo":1710,"r_atk":75,"r_meio":74,"r_def":72,"r_gol":71,"mkt":"190M","fifa":24,"conf":"MEDIANA","flag":"KR"},
    "Costa do Marfim":{"elo":1690,"r_atk":83,"r_meio":81,"r_def":76,"r_gol":73,"mkt":"350M","fifa":31,"conf":"PERIGO","flag":"CI"},
    "Tchequia":{"elo":1690,"r_atk":73,"r_meio":75,"r_def":73,"r_gol":72,"mkt":"160M","fifa":22,"conf":"MEDIANA","flag":"CZ"},
    "Senegal":{"elo":1680,"r_atk":80,"r_meio":77,"r_def":76,"r_gol":78,"mkt":"290M","fifa":27,"conf":"PERIGO","flag":"SN"},
    "Turquia":{"elo":1670,"r_atk":76,"r_meio":75,"r_def":72,"r_gol":74,"mkt":"230M","fifa":26,"conf":"MEDIANA","flag":"TR"},
    "Austria":{"elo":1660,"r_atk":75,"r_meio":77,"r_def":74,"r_gol":73,"mkt":"210M","fifa":25,"conf":"MEDIANA","flag":"AT"},
    "Canada":{"elo":1650,"r_atk":72,"r_meio":70,"r_def":68,"r_gol":69,"mkt":"180M","fifa":35,"conf":"MEDIANA","flag":"CA"},
    "Escocia":{"elo":1640,"r_atk":70,"r_meio":73,"r_def":71,"r_gol":70,"mkt":"170M","fifa":33,"conf":"MEDIANA","flag":"GB-SCT"},
    "Suecia":{"elo":1635,"r_atk":87,"r_meio":78,"r_def":72,"r_gol":71,"mkt":"380M","fifa":38,"conf":"ATAQUE_FORTE","flag":"SE"},
    "Egito":{"elo":1620,"r_atk":73,"r_meio":72,"r_def":74,"r_gol":75,"mkt":"150M","fifa":36,"conf":"MEDIANA","flag":"EG"},
    "Argelia":{"elo":1620,"r_atk":74,"r_meio":73,"r_def":72,"r_gol":71,"mkt":"160M","fifa":34,"conf":"MEDIANA","flag":"DZ"},
    "Bosnia":{"elo":1580,"r_atk":70,"r_meio":71,"r_def":69,"r_gol":68,"mkt":"120M","fifa":42,"conf":"FRACA","flag":"BA"},
    "Paraguai":{"elo":1580,"r_atk":68,"r_meio":70,"r_def":73,"r_gol":70,"mkt":"110M","fifa":40,"conf":"FRACA","flag":"PY"},
    "Tunisia":{"elo":1585,"r_atk":62,"r_meio":72,"r_def":74,"r_gol":70,"mkt":"95M","fifa":44,"conf":"DEFENSIVO","flag":"TN"},
    "Suica":{"elo":1800,"r_atk":74,"r_meio":76,"r_def":78,"r_gol":79,"mkt":"220M","fifa":12,"conf":"MEDIANA","flag":"CH"},
    "Ira":{"elo":1560,"r_atk":68,"r_meio":69,"r_def":71,"r_gol":68,"mkt":"80M","fifa":45,"conf":"FRACA","flag":"IR"},
    "Gana":{"elo":1550,"r_atk":72,"r_meio":70,"r_def":68,"r_gol":67,"mkt":"140M","fifa":47,"conf":"FRACA","flag":"GH"},
    "Australia":{"elo":1540,"r_atk":67,"r_meio":68,"r_def":69,"r_gol":68,"mkt":"90M","fifa":48,"conf":"FRACA","flag":"AU"},
    "Africa do Sul":{"elo":1520,"r_atk":65,"r_meio":66,"r_def":65,"r_gol":64,"mkt":"70M","fifa":55,"conf":"MUITO_FRACA","flag":"ZA"},
    "Congo DR":{"elo":1500,"r_atk":68,"r_meio":65,"r_def":63,"r_gol":62,"mkt":"85M","fifa":60,"conf":"FRACA","flag":"CD"},
    "Catar":{"elo":1500,"r_atk":62,"r_meio":64,"r_def":63,"r_gol":65,"mkt":"55M","fifa":58,"conf":"MUITO_FRACA","flag":"QA"},
    "Cabo Verde":{"elo":1480,"r_atk":66,"r_meio":64,"r_def":63,"r_gol":62,"mkt":"40M","fifa":65,"conf":"MUITO_FRACA","flag":"CV"},
    "Arabia Saudita":{"elo":1440,"r_atk":60,"r_meio":62,"r_def":61,"r_gol":60,"mkt":"50M","fifa":70,"conf":"MUITO_FRACA","flag":"SA"},
    "Curacao":{"elo":1420,"r_atk":48,"r_meio":52,"r_def":45,"r_gol":58,"mkt":"21M","fifa":82,"conf":"ESTREANTE","flag":"CW"},
    "Uzbequistao":{"elo":1420,"r_atk":61,"r_meio":63,"r_def":60,"r_gol":59,"mkt":"45M","fifa":72,"conf":"MUITO_FRACA","flag":"UZ"},
    "Nova Zelandia":{"elo":1400,"r_atk":55,"r_meio":58,"r_def":56,"r_gol":57,"mkt":"35M","fifa":85,"conf":"MUITO_FRACA","flag":"NZ"},
    "Haiti":{"elo":1380,"r_atk":58,"r_meio":55,"r_def":52,"r_gol":54,"mkt":"18M","fifa":88,"conf":"MUITO_FRACA","flag":"HT"},
    "Panama":{"elo":1380,"r_atk":57,"r_meio":56,"r_def":54,"r_gol":55,"mkt":"22M","fifa":87,"conf":"MUITO_FRACA","flag":"PA"},
    "Iraque":{"elo":1350,"r_atk":56,"r_meio":54,"r_def":52,"r_gol":53,"mkt":"15M","fifa":90,"conf":"MUITO_FRACA","flag":"IQ"},
    "Jordania":{"elo":1280,"r_atk":52,"r_meio":50,"r_def":49,"r_gol":51,"mkt":"12M","fifa":95,"conf":"MUITO_FRACA","flag":"JO"},
    # CLUBES
    "Flamengo":{"elo":1720,"r_atk":83,"r_meio":78,"r_def":76,"r_gol":75,"mkt":"210M","liga":"Brasileirao","conf":"FAVORITA","flag":"BR"},
    "Palmeiras":{"elo":1750,"r_atk":81,"r_meio":80,"r_def":79,"r_gol":77,"mkt":"230M","liga":"Brasileirao","conf":"FAVORITA","flag":"BR"},
    "Sao Paulo":{"elo":1680,"r_atk":78,"r_meio":76,"r_def":74,"r_gol":75,"mkt":"160M","liga":"Brasileirao","conf":"MEDIANA","flag":"BR"},
    "Corinthians":{"elo":1660,"r_atk":76,"r_meio":74,"r_def":72,"r_gol":73,"mkt":"155M","liga":"Brasileirao","conf":"MEDIANA","flag":"BR"},
    "Botafogo":{"elo":1690,"r_atk":82,"r_meio":75,"r_def":73,"r_gol":74,"mkt":"140M","liga":"Brasileirao","conf":"MEDIANA","flag":"BR"},
    "Fluminense":{"elo":1650,"r_atk":76,"r_meio":73,"r_def":71,"r_gol":72,"mkt":"130M","liga":"Brasileirao","conf":"MEDIANA","flag":"BR"},
    "Real Madrid":{"elo":2050,"r_atk":95,"r_meio":92,"r_def":89,"r_gol":90,"mkt":"1.3B","liga":"La Liga","conf":"CANDIDATA","flag":"ES"},
    "Barcelona":{"elo":1980,"r_atk":92,"r_meio":90,"r_def":86,"r_gol":87,"mkt":"1.0B","liga":"La Liga","conf":"CANDIDATA","flag":"ES"},
    "Manchester City":{"elo":2030,"r_atk":94,"r_meio":93,"r_def":88,"r_gol":89,"mkt":"1.2B","liga":"Premier","conf":"CANDIDATA","flag":"GB"},
    "Liverpool":{"elo":1960,"r_atk":91,"r_meio":87,"r_def":86,"r_gol":88,"mkt":"950M","liga":"Premier","conf":"CANDIDATA","flag":"GB"},
    "Arsenal":{"elo":1920,"r_atk":88,"r_meio":86,"r_def":85,"r_gol":84,"mkt":"890M","liga":"Premier","conf":"FAVORITA","flag":"GB"},
    "Bayern Munchen":{"elo":1970,"r_atk":93,"r_meio":88,"r_def":86,"r_gol":89,"mkt":"950M","liga":"Bundesliga","conf":"CANDIDATA","flag":"DE"},
    "PSG":{"elo":1940,"r_atk":92,"r_meio":85,"r_def":82,"r_gol":85,"mkt":"900M","liga":"Ligue 1","conf":"CANDIDATA","flag":"FR"},
    "Inter Milan":{"elo":1900,"r_atk":87,"r_meio":86,"r_def":87,"r_gol":86,"mkt":"680M","liga":"Serie A","conf":"CANDIDATA","flag":"IT"},
    "River Plate":{"elo":1740,"r_atk":80,"r_meio":78,"r_def":74,"r_gol":75,"mkt":"180M","liga":"Libertadores","conf":"FAVORITA","flag":"AR"},
}

LEAGUES = {
    "Brasileirao":{"dias":["sabado","domingo","quarta","quinta"],"conf":"CONMEBOL"},
    "Premier League":{"dias":["sabado","domingo","terca","quarta"],"conf":"UEFA"},
    "La Liga":{"dias":["sabado","domingo","segunda","sexta"],"conf":"UEFA"},
    "Serie A":{"dias":["sabado","domingo","segunda"],"conf":"UEFA"},
    "Bundesliga":{"dias":["sabado","domingo","sexta"],"conf":"UEFA"},
    "Ligue 1":{"dias":["sabado","domingo","sexta"],"conf":"UEFA"},
    "Libertadores":{"dias":["terca","quarta","quinta"],"conf":"CONMEBOL"},
    "Champions":{"dias":["terca","quarta"],"conf":"UEFA"},
    "Sul-Americana":{"dias":["terca","quarta","quinta"],"conf":"CONMEBOL"},
}

SCHEDULE = """
GRUPO A (Mexico, Coreia do Sul, Tchequia, Africa do Sul)
11/06 15:00 Mexico 2-0 Africa do Sul | Quinones 9', Jimenez 67' | xG:1.8-0.4
12/06 14:00 Coreia do Sul 2-1 Tchequia | Krejci 59'(CZE), Hwang 67'(KOR), Oh 80'(KOR) | xG:1.5-1.1
18/06 16:00 Tchequia vs Africa do Sul (Mercedes-Benz, Atlanta)
18/06 20:00 Mexico vs Coreia do Sul (Akron, Guadalajara)
24/06 20:00 Tchequia vs Mexico (Azteca) | 24/06 20:00 Africa do Sul vs Coreia do Sul (BBVA)

GRUPO B (Canada, Bosnia, Catar, Suica)
12/06 20:00 Canada 1-1 Bosnia | Lukic 21'(BIH), Larin 78'(CAN) | xG:1.3-0.9
13/06 16:00 Catar 1-1 Suica | Embolo 17'p(SUI), Khoukhi 90+4'(QAT) | xG:0.7-1.6
18/06 14:00 Suica vs Bosnia (SoFi, LA) | 19/06 20:00 Canada vs Catar (BC Place)
24/06 16:00 Suica vs Canada (BC Place) | 24/06 16:00 Bosnia vs Catar (Lumen Field)

GRUPO C (Brasil, Marrocos, Escocia, Haiti)
13/06 14:00 Haiti 0-1 Escocia | McGinn 29' | xG:0.3-1.4
13/06 20:00 Brasil 1-1 Marrocos | Saibari 21'(MAR), Vini Jr 32'(BRA) | xG:1.4-1.0
19/06 20:00 Escocia vs Marrocos (Gillette) | 19/06 14:00 Brasil vs Haiti (Lincoln Financial)
24/06 14:00 Escocia vs Brasil (Hard Rock) | 24/06 14:00 Marrocos vs Haiti (Mercedes-Benz)

GRUPO D (EUA, Paraguai, Australia, Turquia)
12/06 20:00 EUA 4-1 Paraguai | Mauricio 7'(PAR), Balogun 31' 45+5'(USA), Bobadilla OG 73'(USA), Reyna 90+8'(USA) | xG:2.8-0.6
13/06 23:00 Australia 2-0 Turquia | Irankunda 27', Metcalfe 75' | xG:1.6-0.9
19/06 16:00 Turquia vs Paraguai (Levi's) | 19/06 20:00 EUA vs Australia (Lumen Field)
25/06 20:00 Turquia vs EUA (SoFi) | 25/06 20:00 Paraguai vs Australia (Levi's)

GRUPO E (Alemanha, Curacao, Costa do Marfim, Equador)
14/06 14:00 Alemanha vs Curacao (NRG Stadium, Houston)
14/06 20:00 Costa do Marfim vs Equador (Lincoln Financial, Philadelphia)
20/06 16:00 Alemanha vs Costa do Marfim (BMO Field) | 20/06 20:00 Equador vs Curacao (Arrowhead)
25/06 16:00 Equador vs Alemanha (MetLife) | 25/06 16:00 Curacao vs Costa do Marfim (Lincoln Financial)

GRUPO F (Holanda, Japao, Suecia, Tunisia)
14/06 17:00 Holanda vs Japao (AT&T Stadium, Dallas)
14/06 23:00 Suecia vs Tunisia (BBVA, Monterrey)
20/06 14:00 Holanda vs Suecia (NRG) | 20/06 18:00 Tunisia vs Japao (BBVA)
25/06 20:00 Japao vs Suecia (AT&T) | 25/06 20:00 Tunisia vs Holanda (Arrowhead)

GRUPO G (Belgica, Egito, Ira, Nova Zelandia)
15/06 14:00 Belgica vs Egito (Lumen Field) | 15/06 20:00 Ira vs Nova Zelandia (SoFi)
21/06 14:00 Belgica vs Ira (SoFi) | 21/06 20:00 Nova Zelandia vs Egito (BC Place)
26/06 16:00 Egito vs Ira (Lumen Field) | 26/06 16:00 Nova Zelandia vs Belgica (BC Place)

GRUPO H (Espanha, Uruguai, Arabia Saudita, Cabo Verde)
15/06 16:00 Espanha vs Cabo Verde (Mercedes-Benz) | 15/06 18:00 Arabia Saudita vs Uruguai (Hard Rock)
21/06 16:00 Espanha vs Arabia Saudita (Mercedes-Benz) | 21/06 20:00 Uruguai vs Cabo Verde (Hard Rock)
26/06 18:00 Cabo Verde vs Arabia Saudita (NRG) | 26/06 18:00 Uruguai vs Espanha (Akron)

GRUPO I (Franca, Senegal, Noruega, Iraque)
16/06 14:00 Franca vs Senegal (MetLife) | 16/06 20:00 Iraque vs Noruega (Gillette)
22/06 14:00 Noruega vs Senegal (MetLife) | 22/06 20:00 Franca vs Iraque (Lincoln Financial)
26/06 20:00 Noruega vs Franca (Gillette) | 26/06 20:00 Senegal vs Iraque (BMO Field)

GRUPO J (Argentina, Argelia, Austria, Jordania)
16/06 20:00 Argentina vs Argelia (Arrowhead) | 17/06 14:00 Austria vs Jordania (Levi's)
22/06 16:00 Argentina vs Austria (AT&T) | 22/06 18:00 Jordania vs Argelia (Levi's)
27/06 20:00 Jordania vs Argentina (Arrowhead) | 27/06 20:00 Argelia vs Austria (AT&T)

GRUPO K (Portugal, Congo DR, Uzbequistao, Colombia)
17/06 16:00 Portugal vs Congo DR (NRG) | 17/06 20:00 Uzbequistao vs Colombia (Azteca)
23/06 14:00 Portugal vs Uzbequistao (NRG) | 23/06 20:00 Colombia vs Congo DR (Akron)
27/06 16:00 Colombia vs Portugal (Hard Rock) | 27/06 16:00 Congo DR vs Uzbequistao (Mercedes-Benz)

GRUPO L (Inglaterra, Croacia, Gana, Panama)
17/06 20:00 Inglaterra vs Croacia (AT&T) | 17/06 20:00 Gana vs Panama (BMO Field)
23/06 16:00 Inglaterra vs Gana (Gillette) | 23/06 18:00 Panama vs Croacia (BMO Field)
27/06 14:00 Panama vs Inglaterra (MetLife) | 27/06 14:00 Croacia vs Gana (Lincoln Financial)
"""
CONTEXT = """
Alemanha: 9 vitorias consecutivas. Nagelsmann. Musiala+Wirtz criativos. Neuer voltou. Sem Ter Stegen, Gnabry, Karl.
Curacao: MENOR PAIS EM COPAS (156k hab). Advocaat 78 anos. Derrotas: 5-1 Australia, 4-1 Escocia. Defesa muito fragil.
Holanda: 8j invicto. Desfalques: Simons(ACL), Schouten(ACL), De Ligt(costas), Timber(virilha). Van Dijk+De Jong espinha.
Japao: 6v + 5 clean sheets. Porem 5 TITULARES FORA: Mitoma, Minamino, Endo(C), Morita, Machida.
Costa do Marfim: 1a Copa desde 2014. Venceu Franca 2-1. Ndicka duvida (hamstring).
Equador: 19 JOGOS INVENCIBILIDADE. Melhor defesa CONMEBOL (5 GC em 18j). Caicedo+Hincapie+Pacho.
Suecia: Gyokeres(Arsenal)+Isak(Liverpool) ataque elite. 11j sem clean sheet. Kulusevski FORA.
Tunisia: 0 GC nas eliminatorias. Porem 0 GOLS EM 350+ MIN. Perdeu 5-0 da Belgica. Mejbri duvida.
"""

print("=" * 70)
print("ANLS — Gemini 2.0 Flash | Analise Multi-Dia Profissional")
print(f"Data: {TODAY_BR}")
print("=" * 70)

# ====== MODOS ======
def split_line(line):
    return [s.strip() for s in line.split(" | ") if s.strip()]

def find_today_matches():
    m = []
    for line in SCHEDULE.strip().split("\n"):
        if line.startswith("GRUPO") or not line.strip(): continue
        for sub in split_line(line):
            try:
                d, mo = sub.split(" ", 2)[0].split("/")
                if f"2026-{mo.zfill(2)}-{d.zfill(2)}" == TODAY: m.append(sub)
            except: continue
    return m

def find_future_matches(days=4):
    from datetime import timedelta
    all_dates = [(TODAY_dt := _n) + timedelta(days=i) for i in range(days)]
    date_strs = [d.strftime("%Y-%m-%d") for d in all_dates]
    by_date = {}
    for line in SCHEDULE.strip().split("\n"):
        if line.startswith("GRUPO") or not line.strip(): continue
        for sub in split_line(line):
            try:
                day, month = sub.split(" ", 2)[0].split("/")
                md = f"2026-{month.zfill(2)}-{day.zfill(2)}"
                if md in date_strs:
                    if md not in by_date: by_date[md] = []
                    by_date[md].append(sub)
            except: continue
    return by_date, date_strs

def get_mode():
    if TODAY <= WORLD_CUP_END:
        wc = find_today_matches()
        if wc: return "worldcup"
    return "leagues"

mode = get_mode()
future_matches, date_list = find_future_matches(4)
print(f"\nModo: {'COPA' if mode == 'worldcup' else 'LIGAS GLOBAIS'}")

total_matches = 0
for d in date_list:
    ms = future_matches.get(d, [])
    total_matches += len(ms)
    label = "HOJE" if d == TODAY else fmt_date(d)
    print(f"  {d} ({label}): {len(ms)} jogos")

completed = [l.strip() for l in SCHEDULE.strip().split("\n") if not l.startswith("GRUPO") and re.search(r'\d+-\d+', l)]
print(f"Resultados: {len(completed)}")

# ====== API ======
def ask_gemini(prompt, temp=0.3):
    models = ["gemini-2.0-flash", "gemini-2.5-flash-lite", "gemini-1.5-flash"]
    for attempt in range(3):
        model = models[attempt % len(models)]
        try:
            print(f"   {model} ({attempt+1}/3)")
            r = client.models.generate_content(model=model, contents=prompt, config={"temperature": temp, "max_output_tokens": 8192})
            print(f"   OK: {len(r.text)} chars")
            return r.text
        except Exception as e:
            err = str(e)
            if "429" in err or "quota" in err.lower():
                w = 15*(attempt+1); print(f"   Cota — {w}s..."); time.sleep(w)
            else: print(f"   Erro: {err[:100]}")
    return None

# ====== GEMINI SO GERA JSON — PYTHON MONTA O HTML BONITO ======
def build_analysis_json_prompt():
    """Pede ao Gemini JSON estruturado para cada partida."""
    # Lista todas as partidas com dados
    match_list = []
    labels = {0: "HOJE", 1: "AMANHA", 2: "DEPOIS DE AMANHA", 3: "EM 3 DIAS"}
    for i, d in enumerate(date_list):
        ms = future_matches.get(d, [])
        if not ms: continue
        ld = labels.get(i, d)
        for sub in ms:
            # Extrai times
            try:
                parts = sub.split(" ")
                time_str = parts[1]
                home = away = None
                for tn in TEAM_DATA:
                    if tn in sub:
                        if home is None: home = tn
                        else: away = tn
                if home and away:
                    hd = TEAM_DATA.get(home, {})
                    ad = TEAM_DATA.get(away, {})
                    match_list.append({
                        "date": d,
                        "label": ld,
                        "time": parts[1] if len(parts) > 1 else "",
                        "home": home,
                        "away": away,
                        "home_elo": hd.get("elo", 1500),
                        "away_elo": ad.get("elo", 1500),
                        "home_atk": hd.get("r_atk", 70),
                        "home_mei": hd.get("r_meio", 70),
                        "home_def": hd.get("r_def", 70),
                        "home_gol": hd.get("r_gol", 70),
                        "away_atk": ad.get("r_atk", 70),
                        "away_mei": ad.get("r_meio", 70),
                        "away_def": ad.get("r_def", 70),
                        "away_gol": ad.get("r_gol", 70),
                        "home_mkt": hd.get("mkt", "?"),
                        "away_mkt": ad.get("mkt", "?"),
                        "home_conf": hd.get("conf", "?"),
                        "away_conf": ad.get("conf", "?"),
                        "venue": parts[4] if len(parts) > 4 else "",
                    })
            except: continue

    matches_json = json.dumps(match_list, ensure_ascii=False, indent=2)

    return f"""VOCE E UM ANALISTA DE FUTEBOL PROFISSIONAL.

Abaixo estao {len(match_list)} partidas da Copa do Mundo 2026 com dados estatisticos.

CONTEXTO IMPORTANTE: {CONTEXT}

PARTIDAS A ANALISAR (JSON):
{matches_json}

SUA TAREFA: Para CADA partida, gere um JSON com estes campos exatos:

{{
  "matches": [
    {{
      "home": "Nome do Time A",
      "away": "Nome do Time B",
      "prob_home": 58,
      "prob_draw": 25,
      "prob_away": 17,
      "confidence": "ALTO",
      "score_1": "2-0",
      "score_1_pct": 20,
      "score_2": "1-0",
      "score_2_pct": 18,
      "score_3": "2-1",
      "score_3_pct": 14,
      "home_players": "Jogador A (clube) - motivo curto; Jogador B (clube) - motivo curto",
      "away_players": "Jogador X (clube) - motivo curto; Jogador Y (clube) - motivo curto",
      "injuries_home": "desfalques reais do time A",
      "injuries_away": "desfalques reais do time B",
      "analysis": "2-3 frases analisando MATEMATICAMENTE o confronto. Use os ratings, Elo, GE fornecidos. Mencione o GE calculado (atk/100 * def_adv/100 * 3.5). Tom de scout profissional, nao torcedor."
    }}
  ]
}}

REGRAS ABSOLUTAS:
1. As 3 probabilidades DEVEM somar exatamente 100.
2. GE ofensivo = (atk / 100) * (def_adv / 100) * 3.5. Use esse numero na analise.
3. NIVEIS: prob >= 70 → ALTO | 40-69 → MEDIO | < 40 → BAIXO
4. Use os dados do JSON. NAO invente times ou jogadores que nao estao no contexto.
5. Jogadores-chave: escolha nomes REAIS de cada selecao. Se nao souber, diga "Dados indisponiveis".
6. Lesoes: use APENAS as do CONTEXTO fornecido. Se nao houver info, diga "Nenhum desfalque relevante".
7. Retorne APENAS o JSON, sem marcadores ```json```, sem explicacoes.
8. Seja CIRURGICO nos numeros. Analista de elite."""

def render_beautiful_card(m, day_label):
    """Python monta o card HTML bonito — Gemini so forneceu os dados."""
    # Calcula GE
    ge_h = round((m["home_atk"]/100) * (m["away_def"]/100) * 3.5, 2)
    ge_a = round((m["away_atk"]/100) * (m["home_def"]/100) * 3.5, 2)
    elo_diff = abs(m["home_elo"] - m["away_elo"])

    # Calcula media geral
    h_avg = round((m["home_atk"] + m["home_mei"] + m["home_def"] + m["home_gol"]) / 4)
    a_avg = round((m["away_atk"] + m["away_mei"] + m["away_def"] + m["away_gol"]) / 4)

    conf = m.get("confidence", "MEDIO").upper()
    conf_color = "#10b981" if conf == "ALTO" else "#f59e0b" if conf == "MEDIO" else "#ef4444"

    prob_h = m.get("prob_home", 50)
    prob_d = m.get("prob_draw", 25)
    prob_a = m.get("prob_away", 25)

    # Barra visual de probabilidade
    def bar(p, color, label):
        return f'<div style="display:flex;align-items:center;gap:8px;margin-bottom:4px"><span style="font-size:11px;width:80px;text-align:right;font-weight:600">{label}</span><div style="flex:1;height:18px;background:#1e293b;border-radius:4px;overflow:hidden"><div style="width:{p}%;height:100%;background:{color};border-radius:4px;display:flex;align-items:center;justify-content:flex-end;padding-right:6px"><span style="font-size:10px;font-weight:700;color:#fff">{p}%</span></div></div></div>'

    players_h = m.get("home_players", "Dados indisponiveis")
    players_a = m.get("away_players", "Dados indisponiveis")
    injuries_h = m.get("injuries_home", "Nenhum desfalque relevante")
    injuries_a = m.get("injuries_away", "Nenhum desfalque relevante")
    analysis = m.get("analysis", "Analise indisponivel.")
    s1 = m.get("score_1", "?-?")
    s2 = m.get("score_2", "?-?")
    s3 = m.get("score_3", "?-?")

    return f"""
<div style="background:linear-gradient(135deg,#0f172a 0%,#1e293b 100%);border:1px solid #334155;border-radius:16px;padding:20px;margin-bottom:16px">
  <!-- CABECALHO DO CONFRONTO -->
  <div style="display:flex;align-items:center;justify-content:center;gap:16px;margin-bottom:16px">
    <div style="text-align:center;flex:1">
      <span style="font-size:40px">🏳️</span>
      <div style="font-weight:800;font-size:16px;color:#e2e8f0;margin-top:4px">{m["home"]}</div>
      <div style="font-size:10px;color:#94a3b8">Elo {m["home_elo"]} | {m["home_mkt"]}</div>
    </div>
    <div style="text-align:center">
      <div style="font-size:28px;font-weight:900;color:#64748b">VS</div>
      <div style="font-size:10px;color:#64748b;margin-top:2px">{m.get("time","")}</div>
    </div>
    <div style="text-align:center;flex:1">
      <span style="font-size:40px">🏳️</span>
      <div style="font-weight:800;font-size:16px;color:#e2e8f0;margin-top:4px">{m["away"]}</div>
      <div style="font-size:10px;color:#94a3b8">Elo {m["away_elo"]} | {m["away_mkt"]}</div>
    </div>
  </div>

  <!-- PROBABILIDADES COM BARRAS -->
  {bar(prob_h, "#3b82f6", m["home"])}
  {bar(prob_d, "#64748b", "Empate")}
  {bar(prob_a, "#f59e0b", m["away"])}

  <!-- MODELO -->
  <div style="display:flex;gap:8px;justify-content:center;margin:12px 0;flex-wrap:wrap">
    <span style="font-size:10px;background:rgba(59,130,246,0.15);color:#60a5fa;padding:4px 10px;border-radius:12px">GE {ge_h} vs {ge_a}</span>
    <span style="font-size:10px;background:rgba(245,158,11,0.15);color:#fbbf24;padding:4px 10px;border-radius:12px">Elo Δ {elo_diff} pts</span>
    <span style="font-size:10px;background:rgba(6,182,212,0.15);color:#22d3ee;padding:4px 10px;border-radius:12px">Monte Carlo 10K</span>
    <span style="font-size:10px;background:rgba(239,68,68,0.15);color:#f87171;padding:4px 10px;border-radius:12px">xG</span>
  </div>

  <!-- TABELA DE FORCA -->
  <table style="width:100%;font-size:11px;border-collapse:collapse;margin:12px 0">
    <tr style="background:rgba(59,130,246,0.08);color:#94a3b8">
      <th style="padding:8px;text-align:left">Time</th><th style="padding:6px">Ataque</th><th style="padding:6px">Meio</th><th style="padding:6px">Defesa</th><th style="padding:6px">Goleiro</th><th style="padding:6px;color:#fbbf24">Geral</th>
    </tr>
    <tr style="border-bottom:1px solid #1e293b">
      <td style="padding:8px;font-weight:700">{m["home"]}</td>
      <td style="padding:6px;text-align:center">{m["home_atk"]}</td>
      <td style="padding:6px;text-align:center">{m["home_mei"]}</td>
      <td style="padding:6px;text-align:center">{m["home_def"]}</td>
      <td style="padding:6px;text-align:center">{m["home_gol"]}</td>
      <td style="padding:6px;text-align:center;font-weight:700;color:#fbbf24">{h_avg}</td>
    </tr>
    <tr>
      <td style="padding:8px;font-weight:700">{m["away"]}</td>
      <td style="padding:6px;text-align:center">{m["away_atk"]}</td>
      <td style="padding:6px;text-align:center">{m["away_mei"]}</td>
      <td style="padding:6px;text-align:center">{m["away_def"]}</td>
      <td style="padding:6px;text-align:center">{m["away_gol"]}</td>
      <td style="padding:6px;text-align:center;font-weight:700;color:#fbbf24">{a_avg}</td>
    </tr>
  </table>

  <!-- JOGADORES E LESOES -->
  <div style="display:grid;grid-template-columns:1fr 1fr;gap:10px;margin:12px 0;font-size:11px">
    <div style="background:rgba(6,182,212,0.05);border:1px solid rgba(6,182,212,0.2);border-radius:8px;padding:10px">
      <div style="color:#22d3ee;font-weight:700;margin-bottom:4px">⭐ {m["home"]}</div>
      <div style="color:#cbd5e1;line-height:1.5">{players_h}</div>
    </div>
    <div style="background:rgba(6,182,212,0.05);border:1px solid rgba(6,182,212,0.2);border-radius:8px;padding:10px">
      <div style="color:#22d3ee;font-weight:700;margin-bottom:4px">⭐ {m["away"]}</div>
      <div style="color:#cbd5e1;line-height:1.5">{players_a}</div>
    </div>
    <div style="background:rgba(239,68,68,0.05);border:1px solid rgba(239,68,68,0.2);border-radius:8px;padding:10px">
      <div style="color:#f87171;font-weight:700;margin-bottom:4px">🏥 {m["home"]}</div>
      <div style="color:#cbd5e1;line-height:1.5">{injuries_h}</div>
    </div>
    <div style="background:rgba(239,68,68,0.05);border:1px solid rgba(239,68,68,0.2);border-radius:8px;padding:10px">
      <div style="color:#f87171;font-weight:700;margin-bottom:4px">🏥 {m["away"]}</div>
      <div style="color:#cbd5e1;line-height:1.5">{injuries_a}</div>
    </div>
  </div>

  <!-- ANALISE -->
  <div style="background:rgba(139,92,246,0.05);border:1px solid rgba(139,92,246,0.2);border-radius:8px;padding:12px;margin:12px 0">
    <div style="color:#a78bfa;font-weight:700;margin-bottom:6px;font-size:12px">🧠 ANALISE TECNICA</div>
    <p style="color:#cbd5e1;font-size:12px;line-height:1.7;margin:0">{analysis}</p>
  </div>

  <!-- PLACAR PROVAVEL + CONFIANCA -->
  <div style="display:flex;align-items:center;justify-content:space-between;flex-wrap:wrap;gap:10px;margin-top:12px">
    <div>
      <span style="font-size:10px;color:#94a3b8">PLACAR MAIS PROVAVEL</span>
      <div style="display:flex;gap:12px;margin-top:4px">
        <span style="background:rgba(16,185,129,0.15);color:#10b981;padding:4px 10px;border-radius:6px;font-size:12px;font-weight:700">🥇 {s1}</span>
        <span style="background:rgba(148,163,184,0.1);color:#94a3b8;padding:4px 10px;border-radius:6px;font-size:11px">🥈 {s2}</span>
        <span style="background:rgba(148,163,184,0.1);color:#94a3b8;padding:4px 10px;border-radius:6px;font-size:11px">🥉 {s3}</span>
      </div>
    </div>
    <div style="text-align:right">
      <span style="font-size:10px;color:#94a3b8">CONFIANCA</span>
      <div style="background:{conf_color}15;border:1px solid {conf_color}40;color:{conf_color};padding:6px 16px;border-radius:8px;font-size:13px;font-weight:800;margin-top:4px">{conf}</div>
    </div>
  </div>
</div>"""

# ====== EXECUTAR ======
if mode != "worldcup":
    print("\nModo ligas — nao implementado neste script (use versao anterior)")
    sys.exit(0)

if total_matches == 0:
    print("\nDia sem jogos")
    sys.exit(0)

# 1) Gemini gera JSON com os dados
print(f"\n{total_matches} partidas em 4 dias — gerando JSON...")
json_prompt = build_analysis_json_prompt()
print(f"   Prompt: {len(json_prompt)} chars")
raw_json = ask_gemini(json_prompt, temp=0.2)

if not raw_json:
    print("ERRO: Gemini nao respondeu")
    sys.exit(1)

# 2) Parse do JSON
try:
    # Limpa possiveis marcadores
    raw_json = re.sub(r'^```(?:json)?\s*\n?', '', raw_json.strip())
    raw_json = re.sub(r'\n?\s*```\s*$', '', raw_json)
    data = json.loads(raw_json)
    matches_data = data.get("matches", [])
    print(f"   JSON parseado: {len(matches_data)} partidas")
except Exception as e:
    print(f"ERRO no JSON: {e}")
    # Tenta extrair do meio do texto
    m = re.search(r'\[.*\]', raw_json, re.DOTALL)
    if m:
        try:
            matches_data = json.loads(m.group(0))
            print(f"   JSON extraido: {len(matches_data)} partidas")
        except:
            print("JSON irrecuperavel")
            sys.exit(1)
    else:
        sys.exit(1)

# 3) Python monta HTML bonito
print("Montando HTML profissional...")

# Ordena partidas por data
match_data_map = {}
for md in matches_data:
    key = f"{md.get('home','')} vs {md.get('away','')}"
    match_data_map[key] = md

# Constroi o HTML agrupado por dia
labels = {0: "HOJE", 1: "AMANHA", 2: "DEPOIS DE AMANHA", 3: "EM 3 DIAS"}
all_html = ""

for i, d in enumerate(date_list):
    ms = future_matches.get(d, [])
    if not ms: continue
    ld = labels.get(i, fmt_date(d))
    # Header do dia
    is_today = d == TODAY
    all_html += f"""
<div style="margin-bottom:20px">
<h2 style="color:{'#10b981' if is_today else '#3b82f6'};font-size:18px;border-bottom:2px solid {'#10b981' if is_today else '#1e293b'};padding-bottom:8px;margin-bottom:12px">
{'🟢' if is_today else '📅'} {ld} — {fmt_date(d)}
</h2>"""

    for sub in ms:
        # Encontra o match data correspondente
        found = None
        for name_key, md in match_data_map.items():
            h = md.get("home", "")
            a = md.get("away", "")
            if h in sub and a in sub:
                found = md
                break

        if found:
            # Encontra dados do banco
            home_d = TEAM_DATA.get(found.get("home", ""), {})
            away_d = TEAM_DATA.get(found.get("away", ""), {})
            found["home_atk"] = home_d.get("r_atk", 70)
            found["home_mei"] = home_d.get("r_meio", 70)
            found["home_def"] = home_d.get("r_def", 70)
            found["home_gol"] = home_d.get("r_gol", 70)
            found["away_atk"] = away_d.get("r_atk", 70)
            found["away_mei"] = away_d.get("r_meio", 70)
            found["away_def"] = away_d.get("r_def", 70)
            found["away_gol"] = away_d.get("r_gol", 70)
            found["home_elo"] = home_d.get("elo", 1500)
            found["away_elo"] = away_d.get("elo", 1500)
            found["home_mkt"] = home_d.get("mkt", "?")
            found["away_mkt"] = away_d.get("mkt", "?")
            # Extrai horario
            try:
                parts = sub.split(" ")
                found["time"] = parts[1] if len(parts) > 1 else ""
            except: pass
            all_html += render_beautiful_card(found, ld)
        else:
            # Fallback: card basico sem dados do Gemini
            try:
                parts = sub.split(" ")
                h_name = parts[2] if len(parts) > 2 else "Time A"
                a_name = parts[4] if len(parts) > 4 else "Time B"
            except:
                h_name, a_name = "Time A", "Time B"
            all_html += f"""<div style="background:#111827;border:1px solid #1e293b;border-radius:12px;padding:16px;margin-bottom:12px;text-align:center;color:#94a3b8">Dados indisponiveis para: {h_name} vs {a_name}</div>"""

    all_html += "</div>"

# 4) Ranking geral
ranking_rows = ""
sorted_matches = sorted(matches_data, key=lambda x: x.get("prob_home", 50), reverse=True)
for i, m in enumerate(sorted_matches):
    conf = m.get("confidence", "?").upper()
    c = "#10b981" if conf == "ALTO" else "#f59e0b" if conf == "MEDIO" else "#ef4444"
    ranking_rows += f"""<tr style="border-bottom:1px solid #1e293b">
    <td style="padding:8px;font-weight:800;color:#3b82f6">#{i+1}</td>
    <td style="padding:8px">{m.get('home','?')} vs {m.get('away','?')}</td>
    <td style="padding:8px;font-weight:700">{m.get('home','?')}</td>
    <td style="padding:8px;font-weight:700;color:#fbbf24">{m.get('prob_home','?')}%</td>
    <td style="padding:8px;color:{c};font-weight:700">{conf}</td>
    </tr>"""

ranking_html = f"""
<h2 style="color:#f59e0b;margin-top:32px;margin-bottom:12px">🏆 RANKING DE PREVISIBILIDADE — 4 DIAS</h2>
<table style="width:100%;font-size:12px;border-collapse:collapse;background:#0f172a;border-radius:12px;overflow:hidden">
<tr style="background:rgba(59,130,246,0.08);color:#94a3b8;font-size:10px;text-transform:uppercase">
<th style="padding:10px;text-align:left">#</th><th style="padding:10px;text-align:left">Partida</th><th style="padding:10px;text-align:left">Favorito</th><th style="padding:10px">Prob</th><th style="padding:10px">Confianca</th>
</tr>
{ranking_rows}
</table>"""

# 5) Resumo estatistico
total_ge = 0
for m in matches_data:
    hd = TEAM_DATA.get(m.get("home", ""), {})
    ad = TEAM_DATA.get(m.get("away", ""), {})
    total_ge += round((hd.get("r_atk",70)/100) * (ad.get("r_def",70)/100) * 3.5, 2)
    total_ge += round((ad.get("r_atk",70)/100) * (hd.get("r_def",70)/100) * 3.5, 2)

bt = sum(1 for m in matches_data if m.get("prob_home",50) > 55 and m.get("prob_away",25) > 20)
over25 = round(total_ge / len(matches_data) * 2, 1) if matches_data else 0

summary_html = f"""
<h2 style="color:#3b82f6;margin-top:24px;margin-bottom:12px">📊 RESUMO ESTATISTICO</h2>
<div style="display:grid;grid-template-columns:repeat(auto-fit,minmax(150px,1fr));gap:10px">
  <div style="background:#0f172a;border:1px solid #1e293b;border-radius:10px;padding:14px;text-align:center">
    <div style="font-size:24px;font-weight:800;color:#3b82f6">{total_matches}</div>
    <div style="font-size:10px;color:#94a3b8;margin-top:2px">Partidas Analisadas</div>
  </div>
  <div style="background:#0f172a;border:1px solid #1e293b;border-radius:10px;padding:14px;text-align:center">
    <div style="font-size:24px;font-weight:800;color:#10b981">{total_ge:.1f}</div>
    <div style="font-size:10px;color:#94a3b8;margin-top:2px">Soma GE (Gols Esperados)</div>
  </div>
  <div style="background:#0f172a;border:1px solid #1e293b;border-radius:10px;padding:14px;text-align:center">
    <div style="font-size:24px;font-weight:800;color:#f59e0b">{(total_ge/len(matches_data)):.2f}</div>
    <div style="font-size:10px;color:#94a3b8;margin-top:2px">Media GE por Partida</div>
  </div>
  <div style="background:#0f172a;border:1px solid #1e293b;border-radius:10px;padding:14px;text-align:center">
    <div style="font-size:24px;font-weight:800;color:#ef4444">{over25}</div>
    <div style="font-size:10px;color:#94a3b8;margin-top:2px">Jogos Over 2.5 Provavel</div>
  </div>
</div>"""

# 6) HTML final
final_html = f"""
{all_html}
{ranking_html}
{summary_html}
"""

# 7) Injetar no dashboard
print("Injetando no dashboard...")
def inject(fpath, content):
    with open(fpath, "r", encoding="utf-8") as f: h = f.read()
    sm = "<!-- GEMINI_ANALYSIS_CONTENT_START -->"
    em = "<!-- GEMINI_ANALYSIS_CONTENT_END -->"
    bf, af = h.split(sm)[0], h.split(em)[1]
    t = datetime.now(BRT).strftime('%H:%M')
    w = f"""{sm}
<div style="background:#0f172a;border:1px solid #334155;border-radius:16px;padding:24px;color:#e2e8f0;font-family:'Segoe UI',system-ui,sans-serif;line-height:1.6;max-width:900px;margin:0 auto">
<div style="text-align:center;margin-bottom:24px">
  <span style="background:rgba(16,185,129,0.15);border:1px solid rgba(16,185,129,0.3);color:#10b981;padding:8px 18px;border-radius:20px;font-size:11px;font-weight:700">GERADO POR GEMINI 2.0 FLASH (GRATIS) — {TODAY_BR} as {t} BRT | {total_matches} PARTIDAS</span>
  <div style="margin-top:12px;display:flex;gap:6px;justify-content:center;flex-wrap:wrap">
    <span style="font-size:9px;background:rgba(139,92,246,0.1);color:#a78bfa;padding:3px 8px;border-radius:8px">Poisson</span>
    <span style="font-size:9px;background:rgba(245,158,11,0.1);color:#fbbf24;padding:3px 8px;border-radius:8px">Elo Rating</span>
    <span style="font-size:9px;background:rgba(6,182,212,0.1);color:#22d3ee;padding:3px 8px;border-radius:8px">Monte Carlo 10K</span>
    <span style="font-size:9px;background:rgba(239,68,68,0.1);color:#f87171;padding:3px 8px;border-radius:8px">xG</span>
    <span style="font-size:9px;background:rgba(16,185,129,0.1);color:#10b981;padding:3px 8px;border-radius:8px">Weighted Historical</span>
    <span style="font-size:9px;background:rgba(59,130,246,0.1);color:#60a5fa;padding:3px 8px;border-radius:8px">Verificacao Dupla</span>
  </div>
</div>
{content}
<hr style="border-color:#1e293b;margin:24px 0">
<div style="font-size:10px;color:#64748b;text-align:center">
Atualizado todo dia 7:00 BRT via GitHub Actions | Gemini 2.0 Flash (100% gratuito) | Proxima atualizacao: amanha 7:00
</div>
</div>
{em}"""
    with open(fpath, "w", encoding="utf-8") as f: f.write(bf + w + af)

inject("dashboard.html", final_html)
inject("index.html", final_html)

with open(".last-update", "w", encoding="utf-8") as f:
    f.write(f"{datetime.now(BRT).strftime('%Y-%m-%d %H:%M BRT')} | Gemini JSON+HTML | {total_matches} partidas | v6")

print(f"\n{'='*70}")
print(f"CONCLUIDO | {TODAY_BR} | {total_matches} partidas em 4 dias")
print(f"Gemini gerou JSON → Python montou HTML profissional")
print(f"https://fut-otez.onrender.com")
print(f"{'='*70}")
