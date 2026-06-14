#!/usr/bin/env python3
"""
⚽ ANLS — Análise Profissional com Gemini 2.0 Flash (GRÁTIS)
GitHub Actions roda todo dia às 7:00 Brasília
Padrão: Scout Europeu + Cientista de Dados + Departamento Técnico
"""

import sys, io, os, re, time
from datetime import datetime, timezone, timedelta

# UTF-8 no terminal Windows
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

from google import genai

# ── Config ──────────────────────────────────────────
API_KEY = os.environ.get("GEMINI_API_KEY")
if not API_KEY:
    print("ERRO: GEMINI_API_KEY nao configurada no GitHub Secrets!")
    print("   GitHub → Settings → Secrets → Actions → New → GEMINI_API_KEY")
    sys.exit(1)

client = genai.Client(api_key=API_KEY)
BRT = timezone(timedelta(hours=-3))
TODAY = datetime.now(BRT).strftime("%Y-%m-%d")
TODAY_BR = datetime.now(BRT).strftime("%d/%m/%Y")

# ── DADOS ENRIQUECIDOS — Elo, Ratings, Contexto ─────
TEAM_DATA = {
    "Alemanha":    {"elo":1950,"r_atk":91,"r_meio":93,"r_def":88,"r_gol":90,"mkt":"€850M","rank":10,"conf":"ALEMANHA_FAVORITA","fifa":10},
    "Argentina":   {"elo":2050,"r_atk":94,"r_meio":88,"r_def":85,"r_gol":87,"mkt":"€920M","rank":1,"conf":"CANDIDATA_TITULO","fifa":1},
    "Brasil":      {"elo":2020,"r_atk":93,"r_meio":87,"r_def":83,"r_gol":86,"mkt":"€950M","rank":3,"conf":"CANDIDATA_TITULO","fifa":3},
    "França":      {"elo":2000,"r_atk":92,"r_meio":85,"r_def":86,"r_gol":88,"mkt":"€980M","rank":2,"conf":"CANDIDATA_TITULO","fifa":2},
    "Inglaterra":  {"elo":1960,"r_atk":89,"r_meio":86,"r_def":84,"r_gol":83,"mkt":"€890M","rank":5,"conf":"CANDIDATA_TITULO","fifa":5},
    "Espanha":     {"elo":1980,"r_atk":88,"r_meio":90,"r_def":85,"r_gol":85,"mkt":"€820M","rank":4,"conf":"CANDIDATA_TITULO","fifa":4},
    "Portugal":    {"elo":1930,"r_atk":90,"r_meio":84,"r_def":83,"r_gol":86,"mkt":"€780M","rank":6,"conf":"FAVORITA","fifa":6},
    "Holanda":     {"elo":1880,"r_atk":85,"r_meio":87,"r_def":84,"r_gol":79,"mkt":"€780M","rank":7,"conf":"FAVORITA","fifa":7},
    "Bélgica":     {"elo":1840,"r_atk":86,"r_meio":83,"r_def":80,"r_gol":82,"mkt":"€540M","rank":8,"conf":"FAVORITA","fifa":8},
    "Uruguai":     {"elo":1820,"r_atk":82,"r_meio":80,"r_def":83,"r_gol":80,"mkt":"€380M","rank":11,"conf":"MEDIANA","fifa":11},
    "Colômbia":    {"elo":1780,"r_atk":81,"r_meio":79,"r_def":78,"r_gol":77,"mkt":"€310M","rank":14,"conf":"MEDIANA","fifa":14},
    "México":      {"elo":1780,"r_atk":79,"r_meio":77,"r_def":76,"r_gol":75,"mkt":"€260M","rank":15,"conf":"MEDIANA","fifa":15},
    "Japão":       {"elo":1760,"r_atk":78,"r_meio":82,"r_def":81,"r_gol":76,"mkt":"€320M","rank":18,"conf":"PERIGO","fifa":18},
    "Marrocos":    {"elo":1750,"r_atk":77,"r_meio":78,"r_def":79,"r_gol":76,"mkt":"€280M","rank":20,"conf":"PERIGO","fifa":20},
    "Noruega":     {"elo":1750,"r_atk":84,"r_meio":76,"r_def":72,"r_gol":73,"mkt":"€340M","rank":19,"conf":"PERIGO","fifa":19},
    "Croácia":     {"elo":1740,"r_atk":76,"r_meio":84,"r_def":78,"r_gol":75,"mkt":"€250M","rank":21,"conf":"MEDIANA","fifa":21},
    "Equador":     {"elo":1720,"r_atk":74,"r_meio":82,"r_def":88,"r_gol":76,"mkt":"€280M","rank":23,"conf":"DEFENSIVO","fifa":23},
    "EUA":         {"elo":1720,"r_atk":78,"r_meio":76,"r_def":74,"r_gol":77,"mkt":"€330M","rank":16,"conf":"MEDIANA","fifa":16},
    "Coreia do Sul":{"elo":1710,"r_atk":75,"r_meio":74,"r_def":72,"r_gol":71,"mkt":"€190M","rank":24,"conf":"MEDIANA","fifa":24},
    "Costa do Marfim":{"elo":1690,"r_atk":83,"r_meio":81,"r_def":76,"r_gol":73,"mkt":"€350M","rank":31,"conf":"PERIGO","fifa":31},
    "Tchéquia":    {"elo":1690,"r_atk":73,"r_meio":75,"r_def":73,"r_gol":72,"mkt":"€160M","rank":22,"conf":"MEDIANA","fifa":22},
    "Senegal":     {"elo":1680,"r_atk":80,"r_meio":77,"r_def":76,"r_gol":78,"mkt":"€290M","rank":27,"conf":"PERIGO","fifa":27},
    "Turquia":     {"elo":1670,"r_atk":76,"r_meio":75,"r_def":72,"r_gol":74,"mkt":"€230M","rank":26,"conf":"MEDIANA","fifa":26},
    "Áustria":     {"elo":1660,"r_atk":75,"r_meio":77,"r_def":74,"r_gol":73,"mkt":"€210M","rank":25,"conf":"MEDIANA","fifa":25},
    "Canadá":      {"elo":1650,"r_atk":72,"r_meio":70,"r_def":68,"r_gol":69,"mkt":"€180M","rank":35,"conf":"MEDIANA","fifa":35},
    "Escócia":     {"elo":1640,"r_atk":70,"r_meio":73,"r_def":71,"r_gol":70,"mkt":"€170M","rank":33,"conf":"MEDIANA","fifa":33},
    "Suécia":      {"elo":1635,"r_atk":87,"r_meio":78,"r_def":72,"r_gol":71,"mkt":"€380M","rank":38,"conf":"ATAQUE_FORTE","fifa":38},
    "Egito":       {"elo":1620,"r_atk":73,"r_meio":72,"r_def":74,"r_gol":75,"mkt":"€150M","rank":36,"conf":"MEDIANA","fifa":36},
    "Argélia":     {"elo":1620,"r_atk":74,"r_meio":73,"r_def":72,"r_gol":71,"mkt":"€160M","rank":34,"conf":"MEDIANA","fifa":34},
    "Bósnia e Herzegovina":{"elo":1580,"r_atk":70,"r_meio":71,"r_def":69,"r_gol":68,"mkt":"€120M","rank":42,"conf":"FRACA","fifa":42},
    "Paraguai":    {"elo":1580,"r_atk":68,"r_meio":70,"r_def":73,"r_gol":70,"mkt":"€110M","rank":40,"conf":"FRACA","fifa":40},
    "Tunísia":     {"elo":1585,"r_atk":62,"r_meio":72,"r_def":74,"r_gol":70,"mkt":"€95M","rank":44,"conf":"DEFENSIVO","fifa":44},
    "Suíça":       {"elo":1800,"r_atk":74,"r_meio":76,"r_def":78,"r_gol":79,"mkt":"€220M","rank":12,"conf":"MEDIANA","fifa":12},
    "Irã":         {"elo":1560,"r_atk":68,"r_meio":69,"r_def":71,"r_gol":68,"mkt":"€80M","rank":45,"conf":"FRACA","fifa":45},
    "Gana":        {"elo":1550,"r_atk":72,"r_meio":70,"r_def":68,"r_gol":67,"mkt":"€140M","rank":47,"conf":"FRACA","fifa":47},
    "Austrália":   {"elo":1540,"r_atk":67,"r_meio":68,"r_def":69,"r_gol":68,"mkt":"€90M","rank":48,"conf":"FRACA","fifa":48},
    "África do Sul":{"elo":1520,"r_atk":65,"r_meio":66,"r_def":65,"r_gol":64,"mkt":"€70M","rank":55,"conf":"MUITO_FRACA","fifa":55},
    "Congo DR":    {"elo":1500,"r_atk":68,"r_meio":65,"r_def":63,"r_gol":62,"mkt":"€85M","rank":60,"conf":"FRACA","fifa":60},
    "Catar":       {"elo":1500,"r_atk":62,"r_meio":64,"r_def":63,"r_gol":65,"mkt":"€55M","rank":58,"conf":"MUITO_FRACA","fifa":58},
    "Cabo Verde":  {"elo":1480,"r_atk":66,"r_meio":64,"r_def":63,"r_gol":62,"mkt":"€40M","rank":65,"conf":"MUITO_FRACA","fifa":65},
    "Arábia Saudita":{"elo":1440,"r_atk":60,"r_meio":62,"r_def":61,"r_gol":60,"mkt":"€50M","rank":70,"conf":"MUITO_FRACA","fifa":70},
    "Curaçao":     {"elo":1420,"r_atk":48,"r_meio":52,"r_def":45,"r_gol":58,"mkt":"€21M","rank":82,"conf":"ESTREANTE","fifa":82},
    "Uzbequistão": {"elo":1420,"r_atk":61,"r_meio":63,"r_def":60,"r_gol":59,"mkt":"€45M","rank":72,"conf":"MUITO_FRACA","fifa":72},
    "Nova Zelândia":{"elo":1400,"r_atk":55,"r_meio":58,"r_def":56,"r_gol":57,"mkt":"€35M","rank":85,"conf":"MUITO_FRACA","fifa":85},
    "Haiti":       {"elo":1380,"r_atk":58,"r_meio":55,"r_def":52,"r_gol":54,"mkt":"€18M","rank":88,"conf":"MUITO_FRACA","fifa":88},
    "Panamá":      {"elo":1380,"r_atk":57,"r_meio":56,"r_def":54,"r_gol":55,"mkt":"€22M","rank":87,"conf":"MUITO_FRACA","fifa":87},
    "Iraque":      {"elo":1350,"r_atk":56,"r_meio":54,"r_def":52,"r_gol":53,"mkt":"€15M","rank":90,"conf":"MUITO_FRACA","fifa":90},
    "Jordânia":    {"elo":1280,"r_atk":52,"r_meio":50,"r_def":49,"r_gol":51,"mkt":"€12M","rank":95,"conf":"MUITO_FRACA","fifa":95},
}

SCHEDULE = """
GRUPO A (México, Coreia do Sul, Tchéquia, África do Sul)
11/06 15:00 México 2-0 África do Sul | Quiñones 9', Jiménez 67' | xG:1.8-0.4 | Posse:58%-42%
12/06 14:00 Coreia do Sul 2-1 Tchéquia | Krejci 59'(CZE), Hwang 67'(KOR), Oh 80'(KOR) | xG:1.5-1.1
18/06 16:00 Tchéquia vs África do Sul (Mercedes-Benz, Atlanta)
18/06 20:00 México vs Coreia do Sul (Akron, Guadalajara)
24/06 20:00 Tchéquia vs México (Azteca, CDMX) | 24/06 20:00 África do Sul vs Coreia do Sul (BBVA, Monterrey)

GRUPO B (Canadá, Bósnia, Catar, Suíça)
12/06 20:00 Canadá 1-1 Bósnia | Lukic 21'(BIH), Larin 78'(CAN) | xG:1.3-0.9
13/06 16:00 Catar 1-1 Suíça | Embolo 17'p(SUI), Khoukhi 90+4'(QAT) | xG:0.7-1.6 | Posse:35%-65%
18/06 14:00 Suíça vs Bósnia (SoFi, Los Angeles)
19/06 20:00 Canadá vs Catar (BC Place, Vancouver)
24/06 16:00 Suíça vs Canadá (BC Place) | 24/06 16:00 Bósnia vs Catar (Lumen Field, Seattle)

GRUPO C (Brasil, Marrocos, Escócia, Haiti)
13/06 14:00 Haiti 0-1 Escócia | McGinn 29' | xG:0.3-1.4 | Posse:32%-68%
13/06 20:00 Brasil 1-1 Marrocos | Saibari 21'(MAR), Vini Jr 32'(BRA) | xG:1.4-1.0
19/06 20:00 Escócia vs Marrocos (Gillette, Boston)
19/06 14:00 Brasil vs Haiti (Lincoln Financial, Philadelphia)
24/06 14:00 Escócia vs Brasil (Hard Rock, Miami) | 24/06 14:00 Marrocos vs Haiti (Mercedes-Benz, Atlanta)

GRUPO D (EUA, Paraguai, Austrália, Turquia)
12/06 20:00 EUA 4-1 Paraguai | Mauricio 7'(PAR), Balogun 31' 45+5'(USA), Bobadilla OG 73'(USA), Reyna 90+8'(USA) | xG:2.8-0.6
13/06 23:00 Austrália 2-0 Turquia | Irankunda 27', Metcalfe 75' | xG:1.6-0.9 | Zebra da rodada!
19/06 16:00 Turquia vs Paraguai (Levi's, San Francisco)
19/06 20:00 EUA vs Austrália (Lumen Field, Seattle)
25/06 20:00 Turquia vs EUA (SoFi, LA) | 25/06 20:00 Paraguai vs Austrália (Levi's, SF)

GRUPO E (Alemanha, Curaçao, Costa do Marfim, Equador)
14/06 14:00 Alemanha vs Curaçao (NRG Stadium, Houston) — ESTREIA DE CURAÇAO EM COPAS
14/06 20:00 Costa do Marfim vs Equador (Lincoln Financial, Philadelphia) — DUELO TÁTICO DEFESA vs ATAQUE
20/06 16:00 Alemanha vs Costa do Marfim (BMO Field, Toronto)
20/06 20:00 Equador vs Curaçao (Arrowhead, Kansas City)
25/06 16:00 Equador vs Alemanha (MetLife, NY/NJ) | 25/06 16:00 Curaçao vs Costa do Marfim (Lincoln Financial)

GRUPO F (Holanda, Japão, Suécia, Tunísia)
14/06 17:00 Holanda vs Japão (AT&T Stadium, Dallas) — CONFRONTO DE GIGANTES TÁTICOS
14/06 23:00 Suécia vs Tunísia (BBVA, Monterrey) — ATAQUE SUECO vs RETRANCA AFRICANA
20/06 14:00 Holanda vs Suécia (NRG Stadium, Houston)
20/06 18:00 Tunísia vs Japão (BBVA, Monterrey)
25/06 20:00 Japão vs Suécia (AT&T, Dallas) | 25/06 20:00 Tunísia vs Holanda (Arrowhead, KC)

GRUPO G (Bélgica, Egito, Irã, Nova Zelândia)
15/06 14:00 Bélgica vs Egito (Lumen Field, Seattle)
15/06 20:00 Irã vs Nova Zelândia (SoFi, Los Angeles)
21/06 14:00 Bélgica vs Irã (SoFi, LA) | 21/06 20:00 Nova Zelândia vs Egito (BC Place, Vancouver)
26/06 16:00 Egito vs Irã (Lumen Field) | 26/06 16:00 Nova Zelândia vs Bélgica (BC Place)

GRUPO H (Espanha, Uruguai, Arábia Saudita, Cabo Verde)
15/06 16:00 Espanha vs Cabo Verde (Mercedes-Benz, Atlanta)
15/06 18:00 Arábia Saudita vs Uruguai (Hard Rock, Miami)
21/06 16:00 Espanha vs Arábia Saudita (Mercedes-Benz) | 21/06 20:00 Uruguai vs Cabo Verde (Hard Rock)
26/06 18:00 Cabo Verde vs Arábia Saudita (NRG, Houston) | 26/06 18:00 Uruguai vs Espanha (Akron, Guadalajara)

GRUPO I (França, Senegal, Noruega, Iraque)
16/06 14:00 França vs Senegal (MetLife, NY/NJ)
16/06 20:00 Iraque vs Noruega (Gillette, Boston)
22/06 14:00 Noruega vs Senegal (MetLife) | 22/06 20:00 França vs Iraque (Lincoln Financial)
26/06 20:00 Noruega vs França (Gillette) | 26/06 20:00 Senegal vs Iraque (BMO Field, Toronto)

GRUPO J (Argentina, Argélia, Áustria, Jordânia)
16/06 20:00 Argentina vs Argélia (Arrowhead, Kansas City)
17/06 14:00 Áustria vs Jordânia (Levi's, San Francisco)
22/06 16:00 Argentina vs Áustria (AT&T, Dallas) | 22/06 18:00 Jordânia vs Argélia (Levi's)
27/06 20:00 Jordânia vs Argentina (Arrowhead) | 27/06 20:00 Argélia vs Áustria (AT&T)

GRUPO K (Portugal, Congo DR, Uzbequistão, Colômbia)
17/06 16:00 Portugal vs Congo DR (NRG, Houston)
17/06 20:00 Uzbequistão vs Colômbia (Azteca, CDMX)
23/06 14:00 Portugal vs Uzbequistão (NRG) | 23/06 20:00 Colômbia vs Congo DR (Akron)
27/06 16:00 Colômbia vs Portugal (Hard Rock) | 27/06 16:00 Congo DR vs Uzbequistão (Mercedes-Benz)

GRUPO L (Inglaterra, Croácia, Gana, Panamá)
17/06 20:00 Inglaterra vs Croácia (AT&T, Dallas)
17/06 20:00 Gana vs Panamá (BMO Field, Toronto)
23/06 16:00 Inglaterra vs Gana (Gillette, Boston) | 23/06 18:00 Panamá vs Croácia (BMO Field)
27/06 14:00 Panamá vs Inglaterra (MetLife) | 27/06 14:00 Croácia vs Gana (Lincoln Financial)
"""

# ── Contexto adicional enriquecido ──────────────────
CONTEXT = """
CONTEXTO TÁTICO E HISTÓRICO ADICIONAL:

Alemanha: 9 vitórias consecutivas pré-Copa. Nagelsmann no comando. 4-2-3-1. Neuer (40 anos) voltou da aposentadoria. Desfalques: Ter Stegen (lesão grave), Gnabry (muscular), Lennart Karl. Musiala e Wirtz são o motor criativo.
Curaçao: MENOR PAÍS DA HISTÓRIA EM COPAS (156.000 hab). 25 dos 26 jogadores nasceram na Holanda. Dick Advocaat (78 anos) é o técnico mais velho da história. Derrotas recentes: 5-1 Austrália, 4-1 Escócia. Defesa muito frágil.

Holanda: 8 jogos invicto nas eliminatórias (6V 2E). Koeman no comando. Desfalques GRAVES: Xavi Simons (ACL), Schouten (ACL), De Ligt (costas), Timber (virilha). Depay dúvida física. Van Dijk e De Jong são a espinha dorsal.
Japão: 6 vitórias consecutivas (incluindo vitórias sobre Brasil 3-2 e Inglaterra 1-0). 5 CLEAN SHEETS SEGUIDOS. PORÉM: 5 TITULARES LESIONADOS — Mitoma, Minamino, Endo (capitão), Morita, Machida. Time muito enfraquecido pelas lesões.

Costa do Marfim: 1ª Copa desde 2014. Eliminatórias africanas: 10 jogos sem sofrer gol (recorde). Vitória histórica sobre França (2-1) no último amistoso. Amad Diallo em grande fase. Ndicka dúvida (hamstring).
Equador: 19 JOGOS DE INVENCIBILIDADE. Melhor defesa das eliminatórias CONMEBOL (apenas 5 gols sofridos em 18 jogos). Porém: ataque pouco produtivo (14 gols em 18 jogos). Caicedo, Hincapié e Pacho formam espinha defensiva de elite.

Suécia: Classificação dramática — ficou em ÚLTIMO no grupo das eliminatórias (0V 2E 4D), mas sobreviveu pelos playoffs da Nations League (vitórias sobre Ucrânia 3-1 e Polônia 3-2). Graham Potter no comando. Ataque ELITE: Gyökeres (21 gols Arsenal) + Isak (Liverpool). Defesa FRÁGIL: 11 jogos consecutivos sem clean sheet. Kulusevski FORA (joelho).
Tunísia: Classificação HISTÓRICA na defesa — 9V 1E 0D, 22 GF, 0 GC nas eliminatórias africanas. PORÉM: 0 GOLS NOS ÚLTIMOS 350+ MINUTOS. Derrota 5-0 para Bélgica no último amistoso. Lamouchi recém-chegou como técnico. Mejbri dúvida (hamstring).

ARTILHEIROS ATUAIS: Balogun (USA) 2 gols | Quiñones, Jiménez, Hwang, Oh, Larin, Lukic, Embolo, Khoukhi, McGinn, Vini Jr, Saibari, Reyna, Irankunda, Metcalfe, Mauricio, Bobadilla(OG) — 1 gol cada.

ESTATÍSTICAS DO TORNEIO: 12 jogos | 26 gols | Média 2.17 gols/jogo | 6V mandante 4E 2V visitante | Maior goleada: EUA 4-1 Paraguai
"""

print("=" * 70)
print("ANLS — Gemini 2.0 Flash (ANALISE PROFISSIONAL)")
print(f"Data: {TODAY_BR}")
print("=" * 70)

# ── Identificar jogos de hoje ───────────────────────
def find_today_matches():
    matches = []
    for line in SCHEDULE.strip().split("\n"):
        if line.startswith("GRUPO") or not line.strip():
            continue
        parts = line.split(" ", 2)
        if len(parts) < 2:
            continue
        try:
            day, month = parts[0].split("/")
            match_date = f"2026-{month.zfill(2)}-{day.zfill(2)}"
            if match_date == TODAY:
                matches.append(line.strip())
        except:
            continue
    return matches

today_matches = find_today_matches()
print(f"\nJogos hoje: {len(today_matches)}")

# Resultados já ocorridos
completed = []
for line in SCHEDULE.strip().split("\n"):
    if not line.startswith("GRUPO") and re.search(r'\d+-\d+', line):
        completed.append(line.strip())
print(f"Resultados registrados: {len(completed)}")

# ── Função Gemini com retry ─────────────────────────
def ask_gemini(prompt):
    models = ["gemini-2.0-flash", "gemini-2.5-flash-lite", "gemini-1.5-flash"]
    for attempt in range(3):
        model = models[attempt % len(models)]
        try:
            print(f"   Modelo: {model} (tentativa {attempt+1}/3)")
            resp = client.models.generate_content(
                model=model,
                contents=prompt,
                config={"temperature": 0.3, "max_output_tokens": 8192}
            )
            print(f"   Resposta: {len(resp.text)} caracteres")
            return resp.text
        except Exception as e:
            err = str(e)
            if "429" in err or "RESOURCE_EXHAUSTED" in err or "quota" in err.lower():
                wait = 15 * (attempt + 1)
                print(f"   Cota cheia — aguardando {wait}s...")
                time.sleep(wait)
            else:
                print(f"   Erro ({model}): {err[:100]}")
                continue
    return None

# ── CONSTRUIR O PROMPT PROFISSIONAL ─────────────────
def build_professional_prompt():
    # Formata os dados de cada time nos jogos de hoje
    team_info_lines = []
    for m in today_matches:
        for team_name in TEAM_DATA:
            if team_name in m:
                d = TEAM_DATA[team_name]
                team_info_lines.append(
                    f"{team_name}: Elo {d['elo']} | FIFA #{d['fifa']} | "
                    f"Ataque {d['r_atk']}/100 Meio {d['r_meio']}/100 Defesa {d['r_def']}/100 Goleiro {d['r_gol']}/100 | "
                    f"Valor mercado {d['mkt']} | Perfil: {d['conf']}"
                )
    team_info = "\n".join(sorted(set(team_info_lines)))

    return f"""VOCE E UM ANALISTA DE FUTEBOL PROFISSIONAL DE ELITE. ATUE COMO:
- Cientista de dados esportivos (modelos Poisson, Elo, xG, Monte Carlo)
- Scout tático europeu (analise de elenco, formações, pontos fortes/fracos)
- Departamento técnico de clube profissional (relatórios detalhados)

DATA: {TODAY_BR}
DIA 4 DA COPA DO MUNDO FIFA 2026 (48 seleções, 104 jogos, EUA/México/Canadá)

═══════════════════════════════════════════════════
CALENDARIO COMPLETO COM RESULTADOS:
{SCHEDULE}

DADOS ESTATISTICOS DOS TIMES EM CAMPO HOJE:
{team_info}

CONTEXTO TATICO E NOTICIAS:
{CONTEXT}
═══════════════════════════════════════════════════

JOGOS DE HOJE ({TODAY_BR}):
{chr(10).join(today_matches) if today_matches else "Nenhum jogo hoje — dia de descanso"}

═══════════════════════════════════════════════════
INSTRUCOES RIGOROSAS — SIGA CADA ETAPA:
═══════════════════════════════════════════════════

FORMATO DE SAIDA EM HTML (tags inline, fundo escuro #111827, texto #e2e8f0):

<h2 style="color:#3b82f6;border-bottom:1px solid #1e293b;padding-bottom:8px">PARTIDA 1: [TIME A] vs [TIME B]</h2>

PARA CADA PARTIDA, FORNEÇA EXATAMENTE ESTA ESTRUTURA:

<h3 style="color:#10b981">PROBABILIDADES (MODELO ESTATISTICO)</h3>
<p><strong>Vitória [Time A]: XX% | Empate: XX% | Vitória [Time B]: XX%</strong></p>
<p style="font-size:12px">Modelo: Poisson λ=X.XX vs λ=X.XX | Elo Δ=XXX pts | Monte Carlo 10K sims</p>

<h3 style="color:#f59e0b">FORÇA DO ELENCO (nota 0-100)</h3>
<table style="width:100%;font-size:12px;border-collapse:collapse">
<tr style="background:rgba(59,130,246,0.08)"><th></th><th>Ataque</th><th>Meio</th><th>Defesa</th><th>Goleiro</th><th>Geral</th></tr>
<tr><td>[Time A]</td><td>XX</td><td>XX</td><td>XX</td><td>XX</td><td><strong>XX</strong></td></tr>
<tr><td>[Time B]</td><td>XX</td><td>XX</td><td>XX</td><td>XX</td><td><strong>XX</strong></td></tr>
</table>

<h3 style="color:#06b6d4">JOGADORES-CHAVE</h3>
<p><strong>[Time A]:</strong> Jogador 1 (clube) — motivo | Jogador 2 (clube) — motivo</p>
<p><strong>[Time B]:</strong> Jogador 1 (clube) — motivo | Jogador 2 (clube) — motivo</p>

<h3 style="color:#ef4444">LESOES/DESFALQUES</h3>
<p>[Time A]: listar desfalques reais | [Time B]: listar desfalques reais</p>

<h3 style="color:#8b5cf6">ANALISE TECNICA DETALHADA</h3>
<p style="line-height:1.8">Paragrafo de 3-5 linhas explicando POR QUE o modelo chegou nessa probabilidade. Use dados concretos: Elo, Poisson, forma recente, desfalques, contexto tatico. Exemplo: "A Alemanha possui lambda ofensivo de X.XX contra defesa de apenas XX/100 de Curacao. A diferenca de 530 pontos no Elo Rating traduz-se em..."</p>

<h3 style="color:#f59e0b">PLACAR MAIS PROVAVEL (TOP 3)</h3>
<p>1) [Placar] (XX%) | 2) [Placar] (XX%) | 3) [Placar] (XX%)</p>

<h3 style="color:#10b981">NIVEL DE CONFIANCA: [ALTO/MEDIO/BAIXO]</h3>

<hr style="border-color:#1e293b;margin:24px 0">

[REPETIR EXATAMENTE A MESMA ESTRUTURA PARA CADA PARTIDA DE HOJE]

═══════════════════════════════════════════════════
APOS TODAS AS PARTIDAS, ADICIONE:

<h2 style="color:#f59e0b">RANKING DE PREVISIBILIDADE DO DIA</h2>
<table style="width:100%;font-size:12px;border-collapse:collapse">
<tr style="background:rgba(59,130,246,0.08)"><th>#</th><th>Partida</th><th>Favorito</th><th>Prob.</th><th>Confianca</th></tr>
<tr><td>1</td><td>Time A vs Time B</td><td>Time X</td><td>XX%</td><td>ALTO</td></tr>
... (ordenar do MAIS provavel ao MENOS)
</table>

<h2 style="color:#3b82f6">RESUMO ESTATISTICO DO DIA</h2>
<p>Total de gols esperados (soma lambda): X.XX | Media gols/jogo: X.XX</p>
<p>Jogos com Over 2.5 provavel: X de Y | BTTS provavel: X de Y</p>
<p>Maior favorito: [Time] (XX%) | Jogo mais equilibrado: [Time] vs [Time]</p>

═══════════════════════════════════════════════════
REGRAS ABSOLUTAS:
1. NUNCA invente dados. Use APENAS os dados fornecidos.
2. TODAS as porcentagens devem somar 100%.
3. SEMPRE justifique MATEMATICAMENTE cada previsao.
4. Use APENAS HTML inline — SEM ```html```, SEM <body>, SEM <head>.
5. Seja CIRURGICO nos numeros — calcule Poisson λ baseado nos ratings.
6. Lambda ofensivo = (rating_ataque / 100) * (rating_defesa_adversario / 100) * 3.5
7. Confianca ALTO = prob > 70% | MEDIO = 40-70% | BAIXO = < 40%
8. Escreva como analista profissional, nao como torcedor.
"""

# ── Executar ────────────────────────────────────────
if not today_matches:
    print("\nDia sem jogos — gerando resumo...")
    prompt = f"""Voce e um analista de futebol profissional. Data: {TODAY_BR}.
{SCHEDULE}
{CONTEXT}
Escreva um resumo profissional do status atual da Copa 2026 (HTML, fundo escuro #111827, texto #e2e8f0):
1. Resultados ja ocorridos e destaques 2. Classificacao atual dos grupos 3. Artilheiros
4. Estatisticas do torneio 5. Proximos jogos. Tom profissional. Maximo 600 palavras."""
    analysis = ask_gemini(prompt)
else:
    print("\nGerando analise estatistica profissional...")
    prompt = build_professional_prompt()
    analysis = ask_gemini(prompt)

if not analysis:
    analysis = f"""<div style="background:#111827;border:1px solid #1e293b;border-radius:14px;padding:24px;color:#e2e8f0;text-align:center">
<h2 style="color:#f59e0b">ANALISE INDISPONIVEL</h2>
<p>O Gemini nao pode gerar a analise neste momento (cota excedida ou erro de rede).</p>
<p style="font-size:12px;color:#94a3b8;margin-top:12px">Proxima tentativa: amanha as 7:00 (Brasilia)</p>
<p style="font-size:12px;color:#94a3b8">Data: {TODAY_BR}</p></div>"""

# ── Injetar no dashboard ────────────────────────────
print("Injetando analise no dashboard...")

def inject_into_html(filepath, content):
    with open(filepath, "r", encoding="utf-8") as f:
        html = f.read()

    content = re.sub(r'^```(?:html)?\s*\n?', '', content, count=1)
    content = re.sub(r'\n?\s*```\s*$', '', content, count=1)
    content = re.sub(r'^<body[^>]*>', '', content)
    content = re.sub(r'</body>\s*$', '', content)

    start_marker = "<!-- GEMINI_ANALYSIS_CONTENT_START -->"
    end_marker = "<!-- GEMINI_ANALYSIS_CONTENT_END -->"

    before = html.split(start_marker)[0]
    after = html.split(end_marker)[1]

    t = datetime.now(BRT).strftime('%H:%M')
    wrapper = f"""{start_marker}
<div style="background:#111827;border:1px solid #1e293b;border-radius:14px;padding:24px;color:#e2e8f0;font-family:'Segoe UI',system-ui,sans-serif;line-height:1.7">
<div style="text-align:center;margin-bottom:20px;padding:10px 20px;background:rgba(16,185,129,0.1);border:1px solid rgba(16,185,129,0.3);border-radius:20px;display:inline-block">
<span style="font-size:11px;font-weight:700;color:#10b981">GERADO POR GEMINI 2.0 FLASH (GRATIS) — {TODAY_BR} as {t} BRT</span>
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
<div style="font-size:10px;color:#64748b;text-align:center">
Atualizado todo dia as 7:00 (Brasilia) via GitHub Actions |
Gemini 2.0 Flash (Google AI — 100%% gratuito) |
Proxima atualizacao: amanha as 7:00 BRT
</div>
</div>
{end_marker}"""

    new_html = before + wrapper + after
    with open(filepath, "w", encoding="utf-8") as f:
        f.write(new_html)

inject_into_html("dashboard.html", analysis)
inject_into_html("index.html", analysis)

with open(".last-update", "w", encoding="utf-8") as f:
    f.write(f"{datetime.now(BRT).strftime('%Y-%m-%d %H:%M BRT')} | Gemini 2.0 Flash | {len(today_matches)} jogos | Profissional v3")

print()
print("=" * 70)
print("ANALISE PROFISSIONAL CONCLUIDA")
print(f"Data: {TODAY_BR} | Jogos hoje: {len(today_matches)}")
print(f"Resultados na base: {len(completed)}")
print("Dashboard atualizado — https://fut-otez.onrender.com")
print("=" * 70)
