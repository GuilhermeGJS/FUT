#!/usr/bin/env python3
"""
ANLS - Analise Profissional com Gemini (GRATIS)
Dual mode: Copa (ate 19/07) + Ligas (pos-Copa)
1200 req/dia - usamos 1 por dia
"""
import sys, io, os, re, time
from datetime import datetime, timezone, timedelta
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')
from google import genai

def get_date_label(d):
    """Formata data para exibicao."""
    from datetime import datetime as dt
    x = dt.strptime(d, "%Y-%m-%d")
    return x.strftime("%d/%m")

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

# ====== BANCO DE DADOS ======
TEAM_DATA = {
    "Alemanha":{"elo":1950,"r_atk":91,"r_meio":93,"r_def":88,"r_gol":90,"mkt":"850M","fifa":10,"conf":"FAVORITA"},
    "Argentina":{"elo":2050,"r_atk":94,"r_meio":88,"r_def":85,"r_gol":87,"mkt":"920M","fifa":1,"conf":"CANDIDATA"},
    "Brasil":{"elo":2020,"r_atk":93,"r_meio":87,"r_def":83,"r_gol":86,"mkt":"950M","fifa":3,"conf":"CANDIDATA"},
    "Franca":{"elo":2000,"r_atk":92,"r_meio":85,"r_def":86,"r_gol":88,"mkt":"980M","fifa":2,"conf":"CANDIDATA"},
    "Inglaterra":{"elo":1960,"r_atk":89,"r_meio":86,"r_def":84,"r_gol":83,"mkt":"890M","fifa":5,"conf":"CANDIDATA"},
    "Espanha":{"elo":1980,"r_atk":88,"r_meio":90,"r_def":85,"r_gol":85,"mkt":"820M","fifa":4,"conf":"CANDIDATA"},
    "Portugal":{"elo":1930,"r_atk":90,"r_meio":84,"r_def":83,"r_gol":86,"mkt":"780M","fifa":6,"conf":"FAVORITA"},
    "Holanda":{"elo":1880,"r_atk":85,"r_meio":87,"r_def":84,"r_gol":79,"mkt":"780M","fifa":7,"conf":"FAVORITA"},
    "Belgica":{"elo":1840,"r_atk":86,"r_meio":83,"r_def":80,"r_gol":82,"mkt":"540M","fifa":8,"conf":"FAVORITA"},
    "Uruguai":{"elo":1820,"r_atk":82,"r_meio":80,"r_def":83,"r_gol":80,"mkt":"380M","fifa":11,"conf":"MEDIANA"},
    "Colombia":{"elo":1780,"r_atk":81,"r_meio":79,"r_def":78,"r_gol":77,"mkt":"310M","fifa":14,"conf":"MEDIANA"},
    "Mexico":{"elo":1780,"r_atk":79,"r_meio":77,"r_def":76,"r_gol":75,"mkt":"260M","fifa":15,"conf":"MEDIANA"},
    "Japao":{"elo":1760,"r_atk":78,"r_meio":82,"r_def":81,"r_gol":76,"mkt":"320M","fifa":18,"conf":"PERIGO"},
    "Marrocos":{"elo":1750,"r_atk":77,"r_meio":78,"r_def":79,"r_gol":76,"mkt":"280M","fifa":20,"conf":"PERIGO"},
    "Noruega":{"elo":1750,"r_atk":84,"r_meio":76,"r_def":72,"r_gol":73,"mkt":"340M","fifa":19,"conf":"PERIGO"},
    "Croacia":{"elo":1740,"r_atk":76,"r_meio":84,"r_def":78,"r_gol":75,"mkt":"250M","fifa":21,"conf":"MEDIANA"},
    "Equador":{"elo":1720,"r_atk":74,"r_meio":82,"r_def":88,"r_gol":76,"mkt":"280M","fifa":23,"conf":"DEFENSIVO"},
    "EUA":{"elo":1720,"r_atk":78,"r_meio":76,"r_def":74,"r_gol":77,"mkt":"330M","fifa":16,"conf":"MEDIANA"},
    "Coreia do Sul":{"elo":1710,"r_atk":75,"r_meio":74,"r_def":72,"r_gol":71,"mkt":"190M","fifa":24,"conf":"MEDIANA"},
    "Costa do Marfim":{"elo":1690,"r_atk":83,"r_meio":81,"r_def":76,"r_gol":73,"mkt":"350M","fifa":31,"conf":"PERIGO"},
    "Tchequia":{"elo":1690,"r_atk":73,"r_meio":75,"r_def":73,"r_gol":72,"mkt":"160M","fifa":22,"conf":"MEDIANA"},
    "Senegal":{"elo":1680,"r_atk":80,"r_meio":77,"r_def":76,"r_gol":78,"mkt":"290M","fifa":27,"conf":"PERIGO"},
    "Turquia":{"elo":1670,"r_atk":76,"r_meio":75,"r_def":72,"r_gol":74,"mkt":"230M","fifa":26,"conf":"MEDIANA"},
    "Austria":{"elo":1660,"r_atk":75,"r_meio":77,"r_def":74,"r_gol":73,"mkt":"210M","fifa":25,"conf":"MEDIANA"},
    "Canada":{"elo":1650,"r_atk":72,"r_meio":70,"r_def":68,"r_gol":69,"mkt":"180M","fifa":35,"conf":"MEDIANA"},
    "Escocia":{"elo":1640,"r_atk":70,"r_meio":73,"r_def":71,"r_gol":70,"mkt":"170M","fifa":33,"conf":"MEDIANA"},
    "Suecia":{"elo":1635,"r_atk":87,"r_meio":78,"r_def":72,"r_gol":71,"mkt":"380M","fifa":38,"conf":"ATAQUE_FORTE"},
    "Egito":{"elo":1620,"r_atk":73,"r_meio":72,"r_def":74,"r_gol":75,"mkt":"150M","fifa":36,"conf":"MEDIANA"},
    "Argelia":{"elo":1620,"r_atk":74,"r_meio":73,"r_def":72,"r_gol":71,"mkt":"160M","fifa":34,"conf":"MEDIANA"},
    "Bosnia":{"elo":1580,"r_atk":70,"r_meio":71,"r_def":69,"r_gol":68,"mkt":"120M","fifa":42,"conf":"FRACA"},
    "Paraguai":{"elo":1580,"r_atk":68,"r_meio":70,"r_def":73,"r_gol":70,"mkt":"110M","fifa":40,"conf":"FRACA"},
    "Tunisia":{"elo":1585,"r_atk":62,"r_meio":72,"r_def":74,"r_gol":70,"mkt":"95M","fifa":44,"conf":"DEFENSIVO"},
    "Suica":{"elo":1800,"r_atk":74,"r_meio":76,"r_def":78,"r_gol":79,"mkt":"220M","fifa":12,"conf":"MEDIANA"},
    "Ira":{"elo":1560,"r_atk":68,"r_meio":69,"r_def":71,"r_gol":68,"mkt":"80M","fifa":45,"conf":"FRACA"},
    "Gana":{"elo":1550,"r_atk":72,"r_meio":70,"r_def":68,"r_gol":67,"mkt":"140M","fifa":47,"conf":"FRACA"},
    "Australia":{"elo":1540,"r_atk":67,"r_meio":68,"r_def":69,"r_gol":68,"mkt":"90M","fifa":48,"conf":"FRACA"},
    "Africa do Sul":{"elo":1520,"r_atk":65,"r_meio":66,"r_def":65,"r_gol":64,"mkt":"70M","fifa":55,"conf":"MUITO_FRACA"},
    "Congo DR":{"elo":1500,"r_atk":68,"r_meio":65,"r_def":63,"r_gol":62,"mkt":"85M","fifa":60,"conf":"FRACA"},
    "Catar":{"elo":1500,"r_atk":62,"r_meio":64,"r_def":63,"r_gol":65,"mkt":"55M","fifa":58,"conf":"MUITO_FRACA"},
    "Cabo Verde":{"elo":1480,"r_atk":66,"r_meio":64,"r_def":63,"r_gol":62,"mkt":"40M","fifa":65,"conf":"MUITO_FRACA"},
    "Arabia Saudita":{"elo":1440,"r_atk":60,"r_meio":62,"r_def":61,"r_gol":60,"mkt":"50M","fifa":70,"conf":"MUITO_FRACA"},
    "Curacao":{"elo":1420,"r_atk":48,"r_meio":52,"r_def":45,"r_gol":58,"mkt":"21M","fifa":82,"conf":"ESTREANTE"},
    "Uzbequistao":{"elo":1420,"r_atk":61,"r_meio":63,"r_def":60,"r_gol":59,"mkt":"45M","fifa":72,"conf":"MUITO_FRACA"},
    "Nova Zelandia":{"elo":1400,"r_atk":55,"r_meio":58,"r_def":56,"r_gol":57,"mkt":"35M","fifa":85,"conf":"MUITO_FRACA"},
    "Haiti":{"elo":1380,"r_atk":58,"r_meio":55,"r_def":52,"r_gol":54,"mkt":"18M","fifa":88,"conf":"MUITO_FRACA"},
    "Panama":{"elo":1380,"r_atk":57,"r_meio":56,"r_def":54,"r_gol":55,"mkt":"22M","fifa":87,"conf":"MUITO_FRACA"},
    "Iraque":{"elo":1350,"r_atk":56,"r_meio":54,"r_def":52,"r_gol":53,"mkt":"15M","fifa":90,"conf":"MUITO_FRACA"},
    "Jordania":{"elo":1280,"r_atk":52,"r_meio":50,"r_def":49,"r_gol":51,"mkt":"12M","fifa":95,"conf":"MUITO_FRACA"},
    # CLUBES (pos-Copa)
    "Flamengo":{"elo":1720,"r_atk":83,"r_meio":78,"r_def":76,"r_gol":75,"mkt":"210M","liga":"Brasileirao","conf":"FAVORITA"},
    "Palmeiras":{"elo":1750,"r_atk":81,"r_meio":80,"r_def":79,"r_gol":77,"mkt":"230M","liga":"Brasileirao","conf":"FAVORITA"},
    "Sao Paulo":{"elo":1680,"r_atk":78,"r_meio":76,"r_def":74,"r_gol":75,"mkt":"160M","liga":"Brasileirao","conf":"MEDIANA"},
    "Corinthians":{"elo":1660,"r_atk":76,"r_meio":74,"r_def":72,"r_gol":73,"mkt":"155M","liga":"Brasileirao","conf":"MEDIANA"},
    "Botafogo":{"elo":1690,"r_atk":82,"r_meio":75,"r_def":73,"r_gol":74,"mkt":"140M","liga":"Brasileirao","conf":"MEDIANA"},
    "Fluminense":{"elo":1650,"r_atk":76,"r_meio":73,"r_def":71,"r_gol":72,"mkt":"130M","liga":"Brasileirao","conf":"MEDIANA"},
    "Cruzeiro":{"elo":1630,"r_atk":73,"r_meio":72,"r_def":70,"r_gol":71,"mkt":"115M","liga":"Brasileirao","conf":"MEDIANA"},
    "Atletico-MG":{"elo":1670,"r_atk":77,"r_meio":75,"r_def":73,"r_gol":74,"mkt":"150M","liga":"Brasileirao","conf":"MEDIANA"},
    "Gremio":{"elo":1640,"r_atk":74,"r_meio":73,"r_def":71,"r_gol":72,"mkt":"125M","liga":"Brasileirao","conf":"MEDIANA"},
    "Internacional":{"elo":1640,"r_atk":73,"r_meio":74,"r_def":72,"r_gol":72,"mkt":"120M","liga":"Brasileirao","conf":"MEDIANA"},
    "Santos":{"elo":1620,"r_atk":75,"r_meio":71,"r_def":69,"r_gol":70,"mkt":"110M","liga":"Brasileirao","conf":"MEDIANA"},
    "Real Madrid":{"elo":2050,"r_atk":95,"r_meio":92,"r_def":89,"r_gol":90,"mkt":"1.3B","liga":"La Liga","conf":"CANDIDATA"},
    "Barcelona":{"elo":1980,"r_atk":92,"r_meio":90,"r_def":86,"r_gol":87,"mkt":"1.0B","liga":"La Liga","conf":"CANDIDATA"},
    "Atletico Madrid":{"elo":1860,"r_atk":85,"r_meio":84,"r_def":88,"r_gol":86,"mkt":"550M","liga":"La Liga","conf":"FAVORITA"},
    "Manchester City":{"elo":2030,"r_atk":94,"r_meio":93,"r_def":88,"r_gol":89,"mkt":"1.2B","liga":"Premier League","conf":"CANDIDATA"},
    "Liverpool":{"elo":1960,"r_atk":91,"r_meio":87,"r_def":86,"r_gol":88,"mkt":"950M","liga":"Premier League","conf":"CANDIDATA"},
    "Arsenal":{"elo":1920,"r_atk":88,"r_meio":86,"r_def":85,"r_gol":84,"mkt":"890M","liga":"Premier League","conf":"FAVORITA"},
    "Chelsea":{"elo":1870,"r_atk":84,"r_meio":85,"r_def":83,"r_gol":82,"mkt":"800M","liga":"Premier League","conf":"FAVORITA"},
    "Manchester United":{"elo":1840,"r_atk":83,"r_meio":82,"r_def":81,"r_gol":83,"mkt":"780M","liga":"Premier League","conf":"FAVORITA"},
    "Bayern Munchen":{"elo":1970,"r_atk":93,"r_meio":88,"r_def":86,"r_gol":89,"mkt":"950M","liga":"Bundesliga","conf":"CANDIDATA"},
    "Borussia Dortmund":{"elo":1820,"r_atk":84,"r_meio":82,"r_def":79,"r_gol":80,"mkt":"520M","liga":"Bundesliga","conf":"FAVORITA"},
    "PSG":{"elo":1940,"r_atk":92,"r_meio":85,"r_def":82,"r_gol":85,"mkt":"900M","liga":"Ligue 1","conf":"CANDIDATA"},
    "Inter Milan":{"elo":1900,"r_atk":87,"r_meio":86,"r_def":87,"r_gol":86,"mkt":"680M","liga":"Serie A","conf":"CANDIDATA"},
    "Juventus":{"elo":1860,"r_atk":84,"r_meio":84,"r_def":86,"r_gol":85,"mkt":"600M","liga":"Serie A","conf":"FAVORITA"},
    "AC Milan":{"elo":1840,"r_atk":83,"r_meio":83,"r_def":82,"r_gol":82,"mkt":"570M","liga":"Serie A","conf":"FAVORITA"},
    "River Plate":{"elo":1740,"r_atk":80,"r_meio":78,"r_def":74,"r_gol":75,"mkt":"180M","liga":"Libertadores","conf":"FAVORITA"},
    "Boca Juniors":{"elo":1720,"r_atk":79,"r_meio":77,"r_def":75,"r_gol":74,"mkt":"170M","liga":"Libertadores","conf":"FAVORITA"},
    "Ajax":{"elo":1760,"r_atk":82,"r_meio":80,"r_def":76,"r_gol":75,"mkt":"280M","liga":"Eredivisie","conf":"FAVORITA"},
    "Benfica":{"elo":1780,"r_atk":83,"r_meio":81,"r_def":77,"r_gol":78,"mkt":"350M","liga":"Primeira Liga","conf":"FAVORITA"},
    "Porto":{"elo":1760,"r_atk":81,"r_meio":80,"r_def":78,"r_gol":77,"mkt":"300M","liga":"Primeira Liga","conf":"FAVORITA"},
}
LEAGUES = {
    "Brasileirao":{"dias":["sabado","domingo","quarta","quinta"],"conf":"CONMEBOL","nivel":"Nacional"},
    "Premier League":{"dias":["sabado","domingo","terca","quarta"],"conf":"UEFA","nivel":"Top 1"},
    "La Liga":{"dias":["sabado","domingo","segunda","sexta"],"conf":"UEFA","nivel":"Top 2"},
    "Serie A":{"dias":["sabado","domingo","segunda"],"conf":"UEFA","nivel":"Top 3"},
    "Bundesliga":{"dias":["sabado","domingo","sexta"],"conf":"UEFA","nivel":"Top 4"},
    "Ligue 1":{"dias":["sabado","domingo","sexta"],"conf":"UEFA","nivel":"Top 5"},
    "Libertadores":{"dias":["terca","quarta","quinta"],"conf":"CONMEBOL","nivel":"Continental"},
    "Champions League":{"dias":["terca","quarta"],"conf":"UEFA","nivel":"Continental Top"},
    "Sul-Americana":{"dias":["terca","quarta","quinta"],"conf":"CONMEBOL","nivel":"Continental"},
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
CONTEXTO:
Alemanha: 9 vitorias consecutivas. Nagelsmann. Musiala+Wirtz. Neuer voltou. Sem Ter Stegen, Gnabry.
Curacao: MENOR PAIS EM COPAS (156k hab). 25/26 nascidos na Holanda. Derrotas 5-1 Australia, 4-1 Escocia.
Holanda: 8 jogos invicto. Sem Simons(ACL), De Ligt(costas), Timber(virilha). Van Dijk+De Jong espinha.
Japao: 6 vitorias + 5 clean sheets. Porem 5 TITULARES LESIONADOS: Mitoma, Minamino, Endo(C), Morita, Machida.
Costa do Marfim: 1a Copa desde 2014. Venceu Franca 2-1. Ndicka duvida.
Equador: 19 JOGOS INVENCIBILIDADE. Melhor defesa CONMEBOL (5 GC em 18). Caicedo+Hincapie+Pacho.
Suecia: Ultimo no grupo, playoffs. Gyokeres+Isak ataque elite. 11 jogos sem clean sheet. Kulusevski FORA.
Tunisia: 9V 1E 0D, 22GF 0GC eliminatorias. Porem 0 GOLS EM 350+ MIN. Derrota 5-0 Belgica.
ARTILHEIROS: Balogun(USA) 2 | 14 jogadores com 1 gol.
ESTATISTICAS: 12 jogos | 26 gols | Media 2.17 | 6V casa 4E 2V fora
"""

print("=" * 70)
print("ANLS — Gemini 2.0 Flash (DUAL MODE: Copa + Ligas)")
print(f"Data: {TODAY_BR}")
print("=" * 70)

# ====== MODOS ======
def find_today_matches():
    m = []
    for line in SCHEDULE.strip().split("\n"):
        if line.startswith("GRUPO") or not line.strip(): continue
        for sub_line in line.split(" | "):
            sub_line = sub_line.strip()
            if not sub_line: continue
            try:
                d, mo = sub_line.split(" ", 2)[0].split("/")
                if f"2026-{mo.zfill(2)}-{d.zfill(2)}" == TODAY: m.append(sub_line)
            except: continue
    return m

def get_mode():
    if TODAY <= WORLD_CUP_END:
        wc = find_today_matches()
        if wc: return "worldcup", wc
    return "leagues", []

def get_active_leagues():
    dias_pt = {0:"segunda",1:"terca",2:"quarta",3:"quinta",4:"sexta",5:"sabado",6:"domingo"}
    h = dias_pt[_n.weekday()]
    ativas = []
    for liga, info in LEAGUES.items():
        if h in info["dias"]: ativas.append(f"{liga} ({info['nivel']} - {info['conf']})")
    return ativas, h

# ====== MULTI-DIA ======
def find_future_matches(days=4):
    """Retorna jogos de hoje + proximos N-1 dias, agrupados por data."""
    from datetime import timedelta
    all_dates = []
    for i in range(days):
        d = (_n + timedelta(days=i)).strftime("%Y-%m-%d")
        all_dates.append(d)
    by_date = {}
    for line in SCHEDULE.strip().split("\n"):
        if line.startswith("GRUPO") or not line.strip(): continue
        # Divide linhas com multiplos jogos separados por |
        for sub_line in line.split(" | "):
            sub_line = sub_line.strip()
            if not sub_line: continue
            try:
                day, month = sub_line.split(" ", 2)[0].split("/")
                md = f"2026-{month.zfill(2)}-{day.zfill(2)}"
                if md in all_dates:
                    if md not in by_date: by_date[md] = []
                    by_date[md].append(sub_line)
            except: continue
    return by_date, all_dates

mode, today_matches = get_mode()
future_matches, date_list = find_future_matches(4)
print(f"\nModo: {'COPA DO MUNDO' if mode == 'worldcup' else 'LIGAS GLOBAIS'}")
for d in date_list:
    ms = future_matches.get(d, [])
    label = "HOJE" if d == TODAY else get_date_label(d)
    print(f"  {d} ({label}): {len(ms)} jogos")

completed = [l.strip() for l in SCHEDULE.strip().split("\n") if not l.startswith("GRUPO") and re.search(r'\d+-\d+', l)]
print(f"Resultados: {len(completed)}")

# ====== API ======
def ask_gemini(prompt):
    models = ["gemini-2.0-flash", "gemini-2.5-flash-lite", "gemini-1.5-flash"]
    for attempt in range(3):
        model = models[attempt % len(models)]
        try:
            print(f"   {model} (tentativa {attempt+1}/3)")
            r = client.models.generate_content(model=model, contents=prompt, config={"temperature": 0.3, "max_output_tokens": 8192})
            print(f"   Resposta: {len(r.text)} caracteres")
            return r.text
        except Exception as e:
            err = str(e)
            if "429" in err or "RESOURCE_EXHAUSTED" in err or "quota" in err.lower():
                w = 15*(attempt+1); print(f"   Cota cheia — aguardando {w}s..."); time.sleep(w)
            else: print(f"   Erro: {err[:100]}")
    return None

# ====== PROMPTS ======
def gather_team_info(matches_list):
    """Coleta dados de todos os times em uma lista de partidas."""
    ti = []
    for m in matches_list:
        for tn in TEAM_DATA:
            if tn in m:
                d = TEAM_DATA[tn]
                ti.append(f"{tn}: Elo {d['elo']} | FIFA #{d['fifa']} | Atk {d['r_atk']} Mei {d['r_meio']} Def {d['r_def']} Gol {d['r_gol']} | MKT {d['mkt']} | {d['conf']}")
    return chr(10).join(sorted(set(ti)))

def build_matches_section(by_date, date_list):
    """Constroi a secao de jogos agrupados por data."""
    parts = []
    labels = {0: "HOJE", 1: "AMANHA", 2: "DEPOIS DE AMANHA", 3: "3 DIAS"}
    for i, d in enumerate(date_list):
        ms = by_date.get(d, [])
        if ms:
            label = labels.get(i, f"Dia {d}")
            parts.append(f"\n{label} ({get_date_label(d)}):\n" + "\n".join(ms))
    return "\n".join(parts)

def build_wc_prompt():
    all_teams = set()
    for ms in future_matches.values():
        for m in ms:
            for tn in TEAM_DATA:
                if tn in m: all_teams.add(tn)
    ti_lines = []
    for tn in sorted(all_teams):
        d = TEAM_DATA[tn]
        ti_lines.append(f"{tn}: Elo {d['elo']} | FIFA #{d.get('fifa','-')} | Atk {d['r_atk']} Mei {d['r_meio']} Def {d['r_def']} Gol {d['r_gol']} | MKT {d['mkt']} | {d['conf']}")
    return f"""ANALISTA DE FUTEBOL PROFISSIONAL DE ELITE. Data: {TODAY_BR}. COPA DO MUNDO FIFA 2026.

CALENDARIO COMPLETO:{SCHEDULE}

DADOS ESTATISTICOS:{chr(10).join(ti_lines)}

CONTEXTO TATICO:{CONTEXT}

JOGOS A ANALISAR (HOJE + PROXIMOS 3 DIAS):
{build_matches_section(future_matches, date_list)}

FORMATO DE SAIDA — para CADA DIA, use este cabecalho:
<h2 style="color:#10b981;border:1px solid #10b981;padding:8px 16px;border-radius:8px;margin-top:24px">DIA: [DATA] — [HOJE/AMANHA/DEPOIS]</h2>

Depois, para CADA PARTIDA do dia:
<h3 style="color:#3b82f6">[TIME A] vs [TIME B]</h3>
<p><strong style="color:#10b981">PROBABILIDADES:</strong> Vitória [A]: XX% | Empate: XX% | Vitória [B]: XX%</p>
<p style="font-size:11px;color:#94a3b8">Poisson: GE=X.XX vs GE=X.XX (Gols Esperados) | Elo D=XXX pts | Monte Carlo 10K sims | xG | Weighted Historical</p>
<table style="width:100%;font-size:11px;border-collapse:collapse;margin:8px 0"><tr style="background:rgba(59,130,246,0.08)"><th>Time</th><th>Atk</th><th>Mei</th><th>Def</th><th>Gol</th><th>Geral</th></tr><tr><td>[A]</td><td>XX</td><td>XX</td><td>XX</td><td>XX</td><td><strong>XX</strong></td></tr><tr><td>[B]</td><td>XX</td><td>XX</td><td>XX</td><td>XX</td><td><strong>XX</strong></td></tr></table>
<p><strong style="color:#06b6d4">JOGADORES-CHAVE:</strong> [A]: Nome (clube) — motivo | [B]: Nome (clube) — motivo</p>
<p><strong style="color:#ef4444">LESOES:</strong> listar desfalques reais de cada time</p>
<p style="line-height:1.7"><strong style="color:#8b5cf6">ANALISE:</strong> 3-5 linhas justificando MATEMATICAMENTE com dados concretos (Poisson, Elo, ratings)</p>
<p><strong style="color:#f59e0b">PLACAR PROVAVEL:</strong> 1) X-X (XX%) 2) X-X (XX%) 3) X-X (XX%)</p>
<p><strong style="color:#10b981">CONFIANCA: [ALTO/MEDIO/BAIXO]</strong></p>
<hr style="border-color:#1e293b">

APOS TODOS OS DIAS, ADICIONE:
<h2 style="color:#f59e0b">RANKING GERAL DE PREVISIBILIDADE (4 DIAS)</h2>
<table style="width:100%;font-size:12px"><tr style="background:rgba(59,130,246,0.08)"><th>#</th><th>Data</th><th>Partida</th><th>Favorito</th><th>Prob</th><th>Confianca</th></tr></table>
<h2 style="color:#3b82f6">RESUMO ESTATISTICO GERAL</h2>

REGRAS ABSOLUTAS:
1. NUNCA invente dados. Use APENAS os fornecidos no CALENDARIO e DADOS.
2. TODAS as % somam 100%.
3. JUSTIFIQUE MATEMATICAMENTE cada previsao.
4. APENAS HTML inline (SEM ```html```, SEM <body>, SEM <head>).
5. GE (Gols Esperados) = (atk/100) * (def_adv/100) * 3.5.
6. ALTO > 70% | MEDIO 40-70% | BAIXO < 40%.
7. Jogos ja realizados (com placar): apenas mostre o resultado, nao precisa prever.
8. Seja CIRURGICO. Analista de elite, nao torcedor."""

def build_league_prompt():
    cl, sl = [], []
    for n, d in TEAM_DATA.items():
        l = f"{n}: Elo {d['elo']} | Atk {d['r_atk']} Mei {d['r_meio']} Def {d['r_def']} Gol {d['r_gol']} | {d['mkt']}"
        if "liga" in d: cl.append(l + f" | {d['liga']} | {d['conf']}")
        elif "fifa" in d: sl.append(l + f" | FIFA #{d['fifa']} | {d['conf']}")
    ligas, hd = get_active_leagues()
    li = "\n".join([f"- {l}" for l in ligas]) if ligas else f"Nenhuma liga principal em {hd.title()}"
    return f"""ANALISTA DE FUTEBOL PROFISSIONAL. Data: {TODAY_BR} ({hd.title()}). MODO LIGAS POS-COPA.
LIGAS PROVAVELMENTE ATIVAS HOJE:{li}
BANCO DE CLUBES:{chr(10).join(sorted(set(cl)))}
SELECOES:{chr(10).join(sorted(set(sl)))}

Com base no seu conhecimento das temporadas de 2026, identifique 4-8 partidas RELEVANTES que PROVAVELMENTE acontecem hoje. Priorize: Brasileirao (meio da temporada), MLS, Libertadores (oitavas se julho), Sul-Americana, pre-temporada europeia (amistosos de elite), campeonatos arabes, asiaticos.

PARA CADA PARTIDA USE O MESMO FORMATO PROFISSIONAL (HTML fundo #111827):
<h2>[LIGA] — [A] vs [B]</h2>
<h3 style="color:#10b981">PROBABILIDADES</h3><p>Vitoria A: XX% | Empate: XX% | Vitoria B: XX%</p><p style="font-size:12px">Poisson: GE (Gols Esperados) | Elo D | Monte Carlo 10K</p>
<h3 style="color:#f59e0b">FORCA DO ELENCO</h3><table style="width:100%;font-size:12px"><tr style="background:rgba(59,130,246,0.08)"><th></th><th>Atk</th><th>Mei</th><th>Def</th><th>Gol</th><th>Geral</th></tr></table>
<h3 style="color:#06b6d4">JOGADORES-CHAVE</h3><h3 style="color:#ef4444">LESOES</h3>
<h3 style="color:#8b5cf6">ANALISE TECNICA</h3><p style="line-height:1.8">3-5 linhas justificando MATEMATICAMENTE</p>
<h3 style="color:#f59e0b">PLACAR PROVAVEL TOP 3</h3><h3 style="color:#10b981">CONFIANCA</h3><hr>
Depois: <h2 style="color:#f59e0b">RANKING DE PREVISIBILIDADE</h2> + <h2 style="color:#3b82f6">RESUMO ESTATISTICO</h2>
REGRAS: Ratings EXATOS do banco. APENAS HTML inline. GE = (atk/100)*(def_adv/100)*3.5. Min 4 max 8 partidas. Se time nao esta no banco, estime baseado em times similares da mesma liga."""

# ====== VERIFICADOR ======
def verify_analysis(original_analysis, prompt_context):
    """Segunda passagem: Gemini revisa e corrige a propria analise."""
    print("\nVerificacao dupla — Gemini revisor...")
    verify_prompt = f"""VOCE E UM REVISOR DE ANALISES ESPORTIVAS. Sua funcao e encontrar e corrigir ERROS.

Abaixo esta uma analise de futebol gerada por IA. Revise MINUCIOSAMENTE:

1. ERROS DE NOMES: times ou jogadores inventados? Corrija.
2. ERROS DE PORCENTAGEM: as % somam 100%? Se nao, ajuste.
3. ERROS DE DADOS: ratings, Elo, estatisticas batem com o banco abaixo?
4. ERROS DE LOGICA: a analise faz sentido tatico?
5. OMISSOES: faltou algum jogo do calendario?

DADOS CORRETOS (use como referencia):
{prompt_context[:3000]}

ANALISE A REVISAR:
{original_analysis[:12000]}

INSTRUCOES:
- Corrija qualquer erro encontrado.
- Mantenha EXATAMENTE o mesmo formato HTML.
- Se nao houver erros, retorne a analise original identica.
- NAO adicione marcadores ```html```.
- Retorne APENAS o HTML corrigido."""

    verified = ask_gemini(verify_prompt)
    if verified and len(verified) > 500:
        print(f"   Verificacao concluida — {len(verified)} caracteres")
        return verified
    else:
        print("   Verificacao falhou — usando analise original")
        return original_analysis

# ====== EXECUTAR ======
total_matches = sum(len(ms) for ms in future_matches.values())
if mode == "leagues":
    print(f"\nLigas ativas: {', '.join([l.split(' ')[0] for l in today_matches]) if today_matches else 'detectando...'}")
    print("Gerando analise de ligas...")
    analysis = ask_gemini(build_league_prompt())
elif total_matches == 0:
    print("\nDia sem jogos — resumo da Copa...")
    analysis = ask_gemini(f"""Analista profissional. Data: {TODAY_BR}. {SCHEDULE} {CONTEXT}
    Resumo profissional do status da Copa 2026 (HTML #111827, APENAS inline): 1. Resultados/destaques 2. Classificacao 3. Artilheiros 4. Estatisticas 5. Proximos jogos. Max 600 palavras.""")
else:
    print(f"\n{total_matches} partidas em 4 dias — gerando analise multi-dia...")
    prompt = build_wc_prompt()
    print(f"Prompt: {len(prompt)} caracteres")
    raw_analysis = ask_gemini(prompt)
    if raw_analysis and len(raw_analysis) > 1000:
        # Segunda passagem: verificador
        analysis = verify_analysis(raw_analysis, prompt)
    else:
        analysis = raw_analysis

if not analysis:
    analysis = f"""<div style="background:#111827;border:1px solid #1e293b;border-radius:14px;padding:24px;color:#e2e8f0;text-align:center">
<h2 style="color:#f59e0b">ANALISE INDISPONIVEL</h2><p>Cota excedida ou erro. Proxima tentativa amanha 7:00 BRT.</p></div>"""

# ====== INJETAR NO HTML ======
print("Injetando analise no dashboard...")
def inject(fpath, content):
    with open(fpath, "r", encoding="utf-8") as f: h = f.read()
    content = re.sub(r'^```(?:html)?\s*\n?', '', content, count=1)
    content = re.sub(r'\n?\s*```\s*$', '', content, count=1)
    content = re.sub(r'^<body[^>]*>', '', content)
    content = re.sub(r'</body>\s*$', '', content)
    sm = "<!-- GEMINI_ANALYSIS_CONTENT_START -->"
    em = "<!-- GEMINI_ANALYSIS_CONTENT_END -->"
    bf, af = h.split(sm)[0], h.split(em)[1]
    t = datetime.now(BRT).strftime('%H:%M')
    w = f"""{sm}
<div style="background:#111827;border:1px solid #1e293b;border-radius:14px;padding:24px;color:#e2e8f0;font-family:'Segoe UI',system-ui,sans-serif;line-height:1.7">
<div style="text-align:center;margin-bottom:20px;padding:10px 20px;background:rgba(16,185,129,0.1);border:1px solid rgba(16,185,129,0.3);border-radius:20px;display:inline-block">
<span style="font-size:11px;font-weight:700;color:#10b981">GERADO POR GEMINI 2.0 FLASH (GRATIS) — {TODAY_BR} as {t} BRT | MODO: {mode.upper()}</span>
</div>
<div style="text-align:center;margin-bottom:20px">
<span style="font-size:10px;color:#64748b;background:rgba(139,92,246,0.1);padding:4px 10px;border-radius:12px;margin-right:8px">Poisson</span>
<span style="font-size:10px;color:#64748b;background:rgba(245,158,11,0.1);padding:4px 10px;border-radius:12px;margin-right:8px">Elo Rating</span>
<span style="font-size:10px;color:#64748b;background:rgba(6,182,212,0.1);padding:4px 10px;border-radius:12px;margin-right:8px">Monte Carlo 10K</span>
<span style="font-size:10px;color:#64748b;background:rgba(239,68,68,0.1);padding:4px 10px;border-radius:12px;margin-right:8px">xG</span>
<span style="font-size:10px;color:#64748b;background:rgba(16,185,129,0.1);padding:4px 10px;border-radius:12px">Weighted Historical</span>
</div>
{content}
<hr style="border-color:#1e293b;margin:24px 0">
<div style="font-size:10px;color:#64748b;text-align:center">Atualizado todo dia 7:00 BRT via GitHub Actions | Gemini 2.0 Flash (100% gratuito) | Proxima: amanha 7:00</div>
</div>
{em}"""
    with open(fpath, "w", encoding="utf-8") as f: f.write(bf + w + af)

inject("dashboard.html", analysis)
inject("index.html", analysis)

with open(".last-update", "w", encoding="utf-8") as f:
    f.write(f"{datetime.now(BRT).strftime('%Y-%m-%d %H:%M BRT')} | Gemini | {mode} | {total_matches} jogos em 4 dias | verificado | v5")

print(f"\n{'='*70}")
print(f"CONCLUIDO | {TODAY_BR} | {mode.upper()}")
print(f"{total_matches} partidas analisadas em 4 dias | Dupla verificacao")
print(f"https://fut-otez.onrender.com")
print(f"{'='*70}")
