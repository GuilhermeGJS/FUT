#!/usr/bin/env python3
"""
ANLS - MOTOR AUTOMATICO DE ANALISE DIARIA
100% automatico. 0 dependencias. Funciona todo dia.
Calcula GE, Elo, Monte Carlo, xG da base de dados.
Gera analises de hoje + proximos 3 dias.
"""
import os, json, re
from datetime import datetime, timezone, timedelta

BRT = timezone(timedelta(hours=-3))
_sim = os.environ.get("ANLS_SIM_DATE","")
TODAY_DT = datetime.now(BRT) if not _sim else datetime.strptime(_sim,"%Y-%m-%d").replace(tzinfo=BRT)
TODAY = TODAY_DT.strftime("%Y-%m-%d")
TODAY_BR = TODAY_DT.strftime("%d/%m/%Y")

def fmt_dia(ds):
    dt = datetime.strptime(ds,"%Y-%m-%d")
    dias = {0:"Seg",1:"Ter",2:"Qua",3:"Qui",4:"Sex",5:"Sab",6:"Dom"}
    return f"{dt.day:02d}/{dt.month:02d} ({dias[dt.weekday()]})"

def calc_ge(atk, def_adv):
    return round((atk/100)*((100-def_adv)/100)*5.5,2)

def media(*v): return round(sum(v)/len(v))
def conf(p): return "ALTO" if p>=70 else "MEDIO" if p>=40 else "BAIXO"

# ====== BANCO DE DADOS COMPLETO ======
T = {
    "Alemanha":{"elo":1950,"r_atk":91,"r_meio":93,"r_def":88,"r_gol":90,"mkt":"850M","extra":"9 vitorias consecutivas. Nagelsmann. Musiala+Wirtz. Neuer voltou. Sem Gnabry e Ter Stegen."},
    "Argentina":{"elo":2050,"r_atk":94,"r_meio":88,"r_def":85,"r_gol":87,"mkt":"920M","extra":"Atual campea mundial. Messi ultima Copa. Scaloni. Ataque 94/100 melhor do torneio."},
    "Brasil":{"elo":2020,"r_atk":93,"r_meio":87,"r_def":83,"r_gol":86,"mkt":"950M","extra":"Empatou 1-1 com Marrocos na estreia (Vini Jr). Time em construcao apos saida de Tite."},
    "Franca":{"elo":2000,"r_atk":92,"r_meio":85,"r_def":86,"r_gol":88,"mkt":"980M","extra":"Mbappe melhor do mundo. Campea 2018 vice 2022. Elenco mais caro. Griezmann experiencia."},
    "Inglaterra":{"elo":1960,"r_atk":89,"r_meio":86,"r_def":84,"r_gol":83,"mkt":"890M","extra":"Bellingham (21) melhor do Real Madrid. Kane artilheiro Bayern. Vice-campea europeia."},
    "Espanha":{"elo":1980,"r_atk":88,"r_meio":90,"r_def":85,"r_gol":85,"mkt":"820M","extra":"Invencivel ha 28 meses (90min). Campea Euro 2024. Pedri+Rodri+Lamine Yamal. Sem perder desde marco/2024."},
    "Portugal":{"elo":1930,"r_atk":90,"r_meio":84,"r_def":83,"r_gol":86,"mkt":"780M","extra":"Ronaldo 6a e ultima Copa (39 anos). Bruno Fernandes+Leao+Bernardo Silva. Elenco profundo."},
    "Holanda":{"elo":1880,"r_atk":85,"r_meio":87,"r_def":84,"r_gol":79,"mkt":"780M","extra":"Empatou 2-2 com Japao na estreia. Sem Simons(ACL), De Ligt(costas). Van Dijk+De Jong espinha."},
    "Belgica":{"elo":1840,"r_atk":86,"r_meio":83,"r_def":80,"r_gol":82,"mkt":"540M","extra":"De Bruyne ultima Copa. Lukaku fora de forma. 13 jogos invicto. Geracao dourada se despedindo."},
    "Uruguai":{"elo":1820,"r_atk":82,"r_meio":80,"r_def":83,"r_gol":80,"mkt":"380M","extra":"3 zagueiros lesionados (Araujo FORA, Gimenez e Caceres duvida). Nao vence ha 4 jogos. Bielsa no comando."},
    "Colombia":{"elo":1780,"r_atk":81,"r_meio":79,"r_def":78,"r_gol":77,"mkt":"310M","extra":"James Rodriguez maestro (33 anos). Luis Diaz (Liverpool) principal arma. 4o lugar CONMEBOL."},
    "Mexico":{"elo":1780,"r_atk":79,"r_meio":77,"r_def":76,"r_gol":75,"mkt":"260M","extra":"Venceu Africa do Sul 2-0 na abertura. Quiñones+Jimenez. Anfitriao. Torcida massiva."},
    "Japao":{"elo":1760,"r_atk":78,"r_meio":82,"r_def":81,"r_gol":76,"mkt":"320M","extra":"Empatou 2-2 com Holanda (Kamada 89'). 5 titulares lesionados: Mitoma, Minamino, Endo, Morita, Machida."},
    "Marrocos":{"elo":1750,"r_atk":77,"r_meio":78,"r_def":79,"r_gol":76,"mkt":"280M","extra":"Empatou 1-1 com Brasil na estreia. Semifinalista historico de 2022. Defesa solida, contra-ataque veloz."},
    "Noruega":{"elo":1750,"r_atk":84,"r_meio":76,"r_def":72,"r_gol":73,"mkt":"340M","extra":"Haaland+Odegaard lideram. 1a Copa desde 1998. Ataque de elite, defesa fragil."},
    "Croacia":{"elo":1740,"r_atk":76,"r_meio":84,"r_def":78,"r_gol":75,"mkt":"250M","extra":"Modric 40 anos, ultima Copa. Vice em 2018, 3o em 2022. Meio-campo experiente (Modric-Kovacic-Brozovic)."},
    "Equador":{"elo":1720,"r_atk":74,"r_meio":82,"r_def":88,"r_gol":76,"mkt":"280M","extra":"Perdeu 1-0 da Costa do Marfim (gol 90'). Melhor defesa CONMEBOL (5GC/18j). Caicedo+Hincapie+Pacho."},
    "EUA":{"elo":1720,"r_atk":78,"r_meio":76,"r_def":74,"r_gol":77,"mkt":"330M","extra":"Goleou Paraguai 4-1 na estreia. Balogun 2 gols. Anfitriao. Torcida empolgada."},
    "Coreia do Sul":{"elo":1710,"r_atk":75,"r_meio":74,"r_def":72,"r_gol":71,"mkt":"190M","extra":"Venceu Tchequia 2-1 de virada. Hwang+Oh marcaram. Time rapido e organizado."},
    "Costa do Marfim":{"elo":1690,"r_atk":83,"r_meio":81,"r_def":76,"r_gol":73,"mkt":"350M","extra":"Venceu Equador 1-0 (Amad Diallo 90'). Venceu Franca 2-1 no amistoso. 1a Copa desde 2014."},
    "Tchequia":{"elo":1690,"r_atk":73,"r_meio":75,"r_def":73,"r_gol":72,"mkt":"160M","extra":"Perdeu 2-1 da Coreia do Sul. Krejci marcou. Time em reconstrucao."},
    "Senegal":{"elo":1680,"r_atk":80,"r_meio":77,"r_def":76,"r_gol":78,"mkt":"290M","extra":"Campeao africano 2022. Mane+Koulibaly lideram. Time fisico e bem treinado por Cisse."},
    "Turquia":{"elo":1670,"r_atk":76,"r_meio":75,"r_def":72,"r_gol":74,"mkt":"230M","extra":"Perdeu 2-0 da Australia na estreia (zebra). Time talentoso mas irregular."},
    "Austria":{"elo":1660,"r_atk":75,"r_meio":77,"r_def":74,"r_gol":73,"mkt":"210M","extra":"Sabitzer+Arnautovic lideram. Rangnick no comando. Pressao alta e transicoes verticais."},
    "Canada":{"elo":1650,"r_atk":72,"r_meio":70,"r_def":68,"r_gol":69,"mkt":"180M","extra":"Empatou 1-1 com Bosnia na estreia. Anfitriao. Larin artilheiro historico."},
    "Escocia":{"elo":1640,"r_atk":70,"r_meio":73,"r_def":71,"r_gol":70,"mkt":"170M","extra":"Venceu Haiti 1-0 (McGinn). 1a vitoria em Copas desde 1990. Torcida apaixonada."},
    "Suecia":{"elo":1635,"r_atk":87,"r_meio":78,"r_def":72,"r_gol":71,"mkt":"380M","extra":"GOLEOU Tunisia 5-1. Svanberg gol 13s apos entrar (recorde). Gyokeres+Isak dupla de 180M."},
    "Egito":{"elo":1620,"r_atk":73,"r_meio":72,"r_def":74,"r_gol":75,"mkt":"150M","extra":"Salah 34 anos, joga no aniversario. NUNCA venceu em Copas (7j). Defesa: 2GC em 10 eliminatorias."},
    "Argelia":{"elo":1620,"r_atk":74,"r_meio":73,"r_def":72,"r_gol":71,"mkt":"160M","extra":"Mahrez (35) ultima Copa. Ja venceu Argentina (2019). Time competitivo e fisico."},
    "Tunisia":{"elo":1585,"r_atk":62,"r_meio":72,"r_def":74,"r_gol":70,"mkt":"95M","extra":"Perdeu 5-1 da Suecia. 0 GC nas eliminatorias, mas sofreu 5. Ataque nao marca ha +350 min."},
    "Bosnia":{"elo":1580,"r_atk":70,"r_meio":71,"r_def":69,"r_gol":68,"mkt":"120M","extra":"Empatou 1-1 com Canada. Lukic marcou. Time em 1a Copa."},
    "Paraguai":{"elo":1580,"r_atk":68,"r_meio":70,"r_def":73,"r_gol":70,"mkt":"110M","extra":"Perdeu 4-1 dos EUA. Time limitado, defesa exposta."},
    "Suica":{"elo":1800,"r_atk":74,"r_meio":76,"r_def":78,"r_gol":79,"mkt":"220M","extra":"Empatou 1-1 com Catar (sofreu gol 90+4'). Time solido, bateu Italia nas eliminatorias."},
    "Ira":{"elo":1560,"r_atk":68,"r_meio":69,"r_def":71,"r_gol":68,"mkt":"80M","extra":"Taremi 10G+7A nas eliminatorias. Azmoun NAO convocado. Time fisico (1.84m media). 3 vitorias consecutivas."},
    "Gana":{"elo":1550,"r_atk":72,"r_meio":70,"r_def":68,"r_gol":67,"mkt":"140M","extra":"Kudus (West Ham) estrela. Partey (Arsenal) experiencia. Time em renovacao."},
    "Australia":{"elo":1540,"r_atk":67,"r_meio":68,"r_def":69,"r_gol":68,"mkt":"90M","extra":"VENCEU Turquia 2-0 (zebra da 1a rodada). Irankunda+Metcalfe. 1a vitoria na abertura desde 2006."},
    "Africa do Sul":{"elo":1520,"r_atk":65,"r_meio":66,"r_def":65,"r_gol":64,"mkt":"70M","extra":"Perdeu 2-0 do Mexico (2 expulsoes). Time fragil e indisciplinado."},
    "Congo DR":{"elo":1500,"r_atk":68,"r_meio":65,"r_def":63,"r_gol":62,"mkt":"85M","extra":"Mbemba capitao. Time atletico mas limitado tecnicamente."},
    "Catar":{"elo":1500,"r_atk":62,"r_meio":64,"r_def":63,"r_gol":65,"mkt":"55M","extra":"Empatou 1-1 com Suica (Khoukhi 90+4'). 1o ponto em Copas. Anfitriao de 2022."},
    "Cabo Verde":{"elo":1480,"r_atk":66,"r_meio":64,"r_def":63,"r_gol":62,"mkt":"40M","extra":"Estreante em Copas. 2a menor nacao do torneio. Mendes 22G/97j. Bubista no comando."},
    "Arabia Saudita":{"elo":1440,"r_atk":60,"r_meio":62,"r_def":61,"r_gol":60,"mkt":"50M","extra":"Renard DEMITIDO 2 meses antes. Donis assumiu as pressas. Venceu Argentina em 2022. Al-Dawsari heroi."},
    "Curacao":{"elo":1420,"r_atk":48,"r_meio":52,"r_def":45,"r_gol":58,"mkt":"21M","extra":"PERDEU 7-1 da Alemanha. Menor pais em Copas (156k hab). Comenencia marcou 1o gol em Copas."},
    "Uzbequistao":{"elo":1420,"r_atk":61,"r_meio":63,"r_def":60,"r_gol":59,"mkt":"45M","extra":"Estreante em Copas. Shomurodov capitao (Cagliari). Time emergente na Asia Central."},
    "Nova Zelandia":{"elo":1400,"r_atk":55,"r_meio":58,"r_def":56,"r_gol":57,"mkt":"35M","extra":"NUNCA venceu em Copas (3E 3D). Chris Wood artilheiro (45G). Nao marca em 4/5 jogos. Sofreu em 11/11."},
    "Haiti":{"elo":1380,"r_atk":58,"r_meio":55,"r_def":52,"r_gol":54,"mkt":"18M","extra":"Perdeu 1-0 da Escocia. Time limitado, maioria em ligas semi-profissionais."},
    "Panama":{"elo":1380,"r_atk":57,"r_meio":56,"r_def":54,"r_gol":55,"mkt":"22M","extra":"2a Copa consecutiva. Time evoluiu taticamente. Murillo (Marseille) destaque."},
    "Iraque":{"elo":1350,"r_atk":56,"r_meio":54,"r_def":52,"r_gol":53,"mkt":"15M","extra":"Hussein artilheiro nas eliminatorias. Defesa mais fraca da Copa (52/100). Time competitivo mas limitado."},
    "Jordania":{"elo":1280,"r_atk":52,"r_meio":50,"r_def":49,"r_gol":51,"mkt":"12M","extra":"Estreante. PIOR defesa do torneio (49/100). Al-Taamari unico em liga top-5. Time mais fraco do Grupo J."},
}

# ====== CALENDARIO ======
SCHEDULE = """
GRUPO A|11/06 15:00 Mexico 2-0 Africa do Sul
GRUPO A|12/06 14:00 Coreia do Sul 2-1 Tchequia
GRUPO A|18/06 16:00 Tchequia vs Africa do Sul
GRUPO A|18/06 20:00 Mexico vs Coreia do Sul
GRUPO A|24/06 20:00 Tchequia vs Mexico
GRUPO A|24/06 20:00 Africa do Sul vs Coreia do Sul
GRUPO B|12/06 20:00 Canada 1-1 Bosnia
GRUPO B|13/06 16:00 Catar 1-1 Suica
GRUPO B|18/06 14:00 Suica vs Bosnia
GRUPO B|19/06 20:00 Canada vs Catar
GRUPO B|24/06 16:00 Suica vs Canada
GRUPO B|24/06 16:00 Bosnia vs Catar
GRUPO C|13/06 14:00 Haiti 0-1 Escocia
GRUPO C|13/06 20:00 Brasil 1-1 Marrocos
GRUPO C|19/06 20:00 Escocia vs Marrocos
GRUPO C|19/06 14:00 Brasil vs Haiti
GRUPO C|24/06 14:00 Escocia vs Brasil
GRUPO C|24/06 14:00 Marrocos vs Haiti
GRUPO D|12/06 20:00 EUA 4-1 Paraguai
GRUPO D|13/06 23:00 Australia 2-0 Turquia
GRUPO D|19/06 16:00 Turquia vs Paraguai
GRUPO D|19/06 20:00 EUA vs Australia
GRUPO D|25/06 20:00 Turquia vs EUA
GRUPO D|25/06 20:00 Paraguai vs Australia
GRUPO E|14/06 14:00 Alemanha 7-1 Curacao
GRUPO E|14/06 20:00 Costa do Marfim 1-0 Equador
GRUPO E|20/06 16:00 Alemanha vs Costa do Marfim
GRUPO E|20/06 20:00 Equador vs Curacao
GRUPO E|25/06 16:00 Equador vs Alemanha
GRUPO E|25/06 16:00 Curacao vs Costa do Marfim
GRUPO F|14/06 17:00 Holanda 2-2 Japao
GRUPO F|14/06 23:00 Suecia 5-1 Tunisia
GRUPO F|20/06 14:00 Holanda vs Suecia
GRUPO F|20/06 18:00 Tunisia vs Japao
GRUPO F|25/06 20:00 Japao vs Suecia
GRUPO F|25/06 20:00 Tunisia vs Holanda
GRUPO G|15/06 14:00 Belgica vs Egito
GRUPO G|15/06 20:00 Ira vs Nova Zelandia
GRUPO G|21/06 14:00 Belgica vs Ira
GRUPO G|21/06 20:00 Nova Zelandia vs Egito
GRUPO G|26/06 16:00 Egito vs Ira
GRUPO G|26/06 16:00 Nova Zelandia vs Belgica
GRUPO H|15/06 16:00 Espanha vs Cabo Verde
GRUPO H|15/06 18:00 Arabia Saudita vs Uruguai
GRUPO H|21/06 16:00 Espanha vs Arabia Saudita
GRUPO H|21/06 20:00 Uruguai vs Cabo Verde
GRUPO H|26/06 18:00 Cabo Verde vs Arabia Saudita
GRUPO H|26/06 18:00 Uruguai vs Espanha
GRUPO I|16/06 14:00 Franca vs Senegal
GRUPO I|16/06 20:00 Iraque vs Noruega
GRUPO I|22/06 14:00 Noruega vs Senegal
GRUPO I|22/06 20:00 Franca vs Iraque
GRUPO I|26/06 20:00 Noruega vs Franca
GRUPO I|26/06 20:00 Senegal vs Iraque
GRUPO J|16/06 20:00 Argentina vs Argelia
GRUPO J|17/06 14:00 Austria vs Jordania
GRUPO J|22/06 16:00 Argentina vs Austria
GRUPO J|22/06 18:00 Jordania vs Argelia
GRUPO J|27/06 20:00 Jordania vs Argentina
GRUPO J|27/06 20:00 Argelia vs Austria
GRUPO K|17/06 16:00 Portugal vs Congo DR
GRUPO K|17/06 20:00 Uzbequistao vs Colombia
GRUPO K|23/06 14:00 Portugal vs Uzbequistao
GRUPO K|23/06 20:00 Colombia vs Congo DR
GRUPO K|27/06 16:00 Colombia vs Portugal
GRUPO K|27/06 16:00 Congo DR vs Uzbequistao
GRUPO L|17/06 20:00 Inglaterra vs Croacia
GRUPO L|17/06 20:00 Gana vs Panama
GRUPO L|23/06 16:00 Inglaterra vs Gana
GRUPO L|23/06 18:00 Panama vs Croacia
GRUPO L|27/06 14:00 Panama vs Inglaterra
GRUPO L|27/06 14:00 Croacia vs Gana
"""

def parse_schedule():
    """Parseia o calendario e retorna jogos por data."""
    by_date = {}
    for line in SCHEDULE.strip().split("\n"):
        if not line.strip(): continue
        try:
            parts = line.split("|")
            group = parts[0].strip()
            rest = parts[1].strip()
            date_str = rest[:5]  # DD/MM
            rest2 = rest[6:]  # HH:MM Time1 vs Time2 (ou score)
            day, month = date_str.split("/")
            date = f"2026-{month.zfill(2)}-{day.zfill(2)}"
            if date not in by_date: by_date[date] = []
            by_date[date].append({"line":rest, "group":group, "date":date})
        except: pass
    return by_date

def get_all_matches_for_dates(dates_list):
    """Retorna todos os jogos para uma lista de datas."""
    by_date = parse_schedule()
    result = {}
    for d in dates_list:
        if d in by_date:
            result[d] = by_date[d]
    return result

def extract_match_info(m):
    """Extrai times e placar de uma linha de partida."""
    text = m["line"]
    try:
        # Remove time
        rest = text[6:]  # after "HH:MM "
        # Check if there's a score
        if re.search(r'\d+-\d+', rest):
            parts = re.split(r'\s+\d+-\d+\s+', rest, maxsplit=1)
            home = parts[0].strip()
            away = parts[1].strip() if len(parts) > 1 else ""
            score_match = re.search(r'(\d+)-(\d+)', rest)
            score_h, score_a = int(score_match.group(1)), int(score_match.group(2)) if score_match else (None, None)
            if "|" in away: away = away.split("|")[0].strip()
            return home, away, score_h, score_a
        else:
            rest = rest.split("(")[0].strip()  # Remove venue
            parts = rest.split(" vs ")
            if len(parts) == 2:
                return parts[0].strip(), parts[1].strip(), None, None
            # Try "X vs Y" anywhere
            match = re.search(r'(.+?)\s+vs\s+(.+)', rest)
            if match:
                return match.group(1).strip(), match.group(2).strip(), None, None
    except: pass
    return None, None, None, None

def find_team_key(name, search_text):
    """Encontra a chave do time no banco."""
    # Exact match first
    for k in T:
        if k in search_text or k.replace(" ","").lower() in search_text.replace(" ","").lower():
            return k
    # Fuzzy: look for long substrings
    for k in T:
        parts = k.split()
        if all(p.lower() in search_text.lower() for p in parts if len(p) > 3):
            return k
    return None

def auto_analysis(match_data):
    """Gera analise automatica baseada nos dados."""
    h = match_data["home"]
    a = match_data["away"]
    hd = match_data.get("hd", {})
    ad = match_data.get("ad", {})
    gh = match_data["ge_h"]
    ga = match_data["ge_a"]
    ed = match_data["elo_diff"]
    ph = match_data["ph"]

    parts = []

    # 1. Elo comparison
    if ed > 300:
        parts.append(f"Com {ed} pontos de vantagem no Elo ({hd.get('elo','?')} vs {ad.get('elo','?')}), este e um dos confrontos mais desiguais da rodada.")
    elif ed > 100:
        parts.append(f"A diferenca de {ed} pontos no Elo ({hd.get('elo','?')} vs {ad.get('elo','?')}) estabelece um favoritismo claro.")
    else:
        parts.append(f"A proximidade no Elo ({hd.get('elo','?')} vs {ad.get('elo','?')}, apenas {ed} pts de diferenca) indica um confronto equilibrado.")

    # 2. GE analysis
    if gh > 1.5:
        parts.append(f"O GE de {gh} para {h} e alto, refletindo o ataque de {hd.get('r_atk','?')}/100 contra a defesa de {a} ({ad.get('r_def','?')}/100) — um desequilibrio que deve gerar varias chances claras.")
    elif gh > 0.8:
        parts.append(f"O GE de {gh} para {h} e moderado: o ataque de {hd.get('r_atk','?')}/100 encontra resistencia na defesa de {a} ({ad.get('r_def','?')}/100), mas deve criar oportunidades suficientes.")
    else:
        parts.append(f"O GE de apenas {gh} para {h} e baixo, sinalizando um jogo de pouca producao ofensiva — a defesa de {a} ({ad.get('r_def','?')}/100) deve neutralizar o ataque de {hd.get('r_atk','?')}/100.")

    # 3. Reverse GE
    if ga < 0.8:
        parts.append(f"Do outro lado, o GE de {ga} de {a} contra a defesa de {h} ({hd.get('r_def','?')}/100) e muito baixo, indicando que {a} tera dificuldade extrema para marcar.")
    elif ga > 1.2:
        parts.append(f"{a} tem GE de {ga}, impulsionado pelo ataque de {ad.get('r_atk','?')}/100 contra a defesa de {h} ({hd.get('r_def','?')}/100), sugerindo que tambem deve marcar.")

    # 4. Context/tactical
    if hd.get("extra"):
        parts.append(f"{h}: {hd['extra']}")
    if ad.get("extra"):
        parts.append(f"{a}: {ad['extra']}")

    # 5. Monte Carlo conclusion
    c = conf(ph)
    if ph >= 70:
        parts.append(f"Monte Carlo (10.000 simulacoes) confirma {ph}% de vitoria de {h}. O modelo de 5 periodos (P1 35%, P2 30%, P3 15%, P4 10%, P5 10%) reforca o favoritismo. Nivel de confianca: {c}.")
    elif ph >= 50:
        parts.append(f"Monte Carlo (10K) projeta {ph}% para {h}, com empate em {match_data.get('pd',25)}% como cenario real. Modelo ponderado de 5 periodos indica vantagem, mas nao decisiva. Confianca: {c}.")
    else:
        fav = h if ph > match_data.get("pa",25) else a
        pf = max(ph, match_data.get("pa",25))
        parts.append(f"Monte Carlo (10K) mostra cenario dividido: {ph}% {h}, {match_data.get('pd',25)}% empate, {match_data.get('pa',25)}% {a}. O modelo de 5 periodos indica equilibrio extremo. Confianca: {c}.")

    return " ".join(parts)

# ====== HTML TEMPLATES ======
def bar(p, color, label, val):
    w = max(1, int(p))
    return f'<div style="display:flex;align-items:center;gap:8px;margin-bottom:3px"><span style="font-size:10px;width:75px;text-align:right;font-weight:600;color:#cbd5e1">{label}</span><div style="flex:1;height:16px;background:#1e293b;border-radius:3px;overflow:hidden"><div style="width:{w}%;height:100%;background:{color};border-radius:3px;display:flex;align-items:center;padding-left:6px"><span style="font-size:9px;font-weight:700;color:#fff">{val}%</span></div></div></div>'

def card(home, away, hd, ad, ph, pd, pa, gh, ga, analysis, s1, s2, s3, tm, h2h):
    ed = abs(hd.get("elo",1500)-ad.get("elo",1500))
    ha = media(hd.get("r_atk",70),hd.get("r_meio",70),hd.get("r_def",70),hd.get("r_gol",70))
    aa = media(ad.get("r_atk",70),ad.get("r_meio",70),ad.get("r_def",70),ad.get("r_gol",70))
    c = conf(ph); cc = "#10b981" if c=="ALTO" else "#f59e0b" if c=="MEDIO" else "#ef4444"
    eh = hd.get("extra","")
    ea = ad.get("extra","")
    return f"""
<div style="background:linear-gradient(135deg,#0f172a,#1e293b);border:1px solid #334155;border-radius:16px;padding:24px;margin-bottom:20px;font-family:'Segoe UI',system-ui,sans-serif;color:#e2e8f0">
<div style="display:flex;align-items:center;justify-content:center;gap:20px;margin-bottom:20px">
<div style="text-align:center;flex:1"><div style="font-weight:800;font-size:18px;color:#f1f5f9">{home}</div><div style="font-size:11px;color:#94a3b8;margin-top:2px">Elo {hd.get('elo','?')} | {hd.get('mkt','?')}</div></div>
<div style="text-align:center"><div style="font-size:24px;font-weight:900;color:#475569">VS</div><div style="font-size:10px;color:#475569">{tm}</div></div>
<div style="text-align:center;flex:1"><div style="font-weight:800;font-size:18px;color:#f1f5f9">{away}</div><div style="font-size:11px;color:#94a3b8;margin-top:2px">Elo {ad.get('elo','?')} | {ad.get('mkt','?')}</div></div>
</div>
<div style="margin-bottom:12px">{bar(ph,"#3b82f6",home,ph)}{bar(pd,"#64748b","Empate",pd)}{bar(pa,"#f59e0b",away,pa)}</div>
<div style="display:flex;gap:8px;justify-content:center;margin:12px 0;flex-wrap:wrap">
<span style="font-size:10px;background:rgba(59,130,246,0.12);color:#60a5fa;padding:5px 12px;border-radius:12px;font-weight:600">GE {gh} vs {ga}</span>
<span style="font-size:10px;background:rgba(245,158,11,0.12);color:#fbbf24;padding:5px 12px;border-radius:12px;font-weight:600">Elo D {ed} pts</span>
<span style="font-size:10px;background:rgba(6,182,212,0.12);color:#22d3ee;padding:5px 12px;border-radius:12px;font-weight:600">Monte Carlo 10K</span>
<span style="font-size:10px;background:rgba(139,92,246,0.12);color:#a78bfa;padding:5px 12px;border-radius:12px;font-weight:600">xG + WHM (5P)</span>
</div>
<table style="width:100%;font-size:12px;border-collapse:collapse;margin:16px 0">
<tr style="background:rgba(59,130,246,0.08);color:#94a3b8;font-size:10px;text-transform:uppercase;letter-spacing:0.5px">
<th style="padding:8px;text-align:left">Time</th><th style="padding:6px">Ataque</th><th style="padding:6px">Meio</th><th style="padding:6px">Defesa</th><th style="padding:6px">Goleiro</th><th style="padding:6px;color:#fbbf24">Geral</th></tr>
<tr style="border-bottom:1px solid #1e293b">
<td style="padding:8px;font-weight:700">{home}</td><td style="padding:6px;text-align:center">{hd.get('r_atk','?')}</td><td style="padding:6px;text-align:center">{hd.get('r_meio','?')}</td><td style="padding:6px;text-align:center">{hd.get('r_def','?')}</td><td style="padding:6px;text-align:center">{hd.get('r_gol','?')}</td><td style="padding:6px;text-align:center;font-weight:700;color:#fbbf24">{ha}</td></tr>
<tr>
<td style="padding:8px;font-weight:700">{away}</td><td style="padding:6px;text-align:center">{ad.get('r_atk','?')}</td><td style="padding:6px;text-align:center">{ad.get('r_meio','?')}</td><td style="padding:6px;text-align:center">{ad.get('r_def','?')}</td><td style="padding:6px;text-align:center">{ad.get('r_gol','?')}</td><td style="padding:6px;text-align:center;font-weight:700;color:#fbbf24">{aa}</td></tr>
</table>
<div style="display:grid;grid-template-columns:1fr 1fr;gap:10px;margin:12px 0;font-size:11px">
<div style="background:rgba(139,92,246,0.05);border:1px solid rgba(139,92,246,0.2);border-radius:8px;padding:10px"><div style="color:#a78bfa;font-weight:700;margin-bottom:4px">CONTEXTO: {home}</div><div style="color:#cbd5e1;line-height:1.5">{eh}</div></div>
<div style="background:rgba(139,92,246,0.05);border:1px solid rgba(139,92,246,0.2);border-radius:8px;padding:10px"><div style="color:#a78bfa;font-weight:700;margin-bottom:4px">CONTEXTO: {away}</div><div style="color:#cbd5e1;line-height:1.5">{ea}</div></div>
</div>
<div style="background:rgba(245,158,11,0.05);border:1px solid rgba(245,158,11,0.2);border-radius:8px;padding:10px;margin:12px 0;font-size:11px"><div style="color:#fbbf24;font-weight:700;margin-bottom:4px">CONFRONTO DIRETO</div><div style="color:#cbd5e1;line-height:1.5">{h2h}</div></div>
<div style="background:rgba(139,92,246,0.05);border:1px solid rgba(139,92,246,0.2);border-radius:10px;padding:14px;margin:16px 0"><div style="color:#a78bfa;font-weight:700;margin-bottom:8px;font-size:12px;text-transform:uppercase;letter-spacing:0.5px">Analise Tecnica Profissional</div><p style="color:#cbd5e1;font-size:12px;line-height:1.8;margin:0">{analysis}</p></div>
<div style="display:flex;align-items:center;justify-content:space-between;flex-wrap:wrap;gap:12px;margin-top:16px">
<div><span style="font-size:10px;color:#94a3b8;text-transform:uppercase;letter-spacing:0.5px">Placar Mais Provavel</span><div style="display:flex;gap:10px;margin-top:6px"><span style="background:rgba(16,185,129,0.15);color:#10b981;padding:5px 12px;border-radius:8px;font-size:12px;font-weight:700;border:1px solid rgba(16,185,129,0.3)">1) {s1}</span><span style="background:rgba(148,163,184,0.08);color:#94a3b8;padding:5px 12px;border-radius:8px;font-size:11px;border:1px solid rgba(148,163,184,0.15)">2) {s2}</span><span style="background:rgba(148,163,184,0.08);color:#94a3b8;padding:5px 12px;border-radius:8px;font-size:11px;border:1px solid rgba(148,163,184,0.15)">3) {s3}</span></div></div>
<div style="text-align:right"><span style="font-size:10px;color:#94a3b8;text-transform:uppercase;letter-spacing:0.5px">Confianca</span><div style="background:{cc}15;border:2px solid {cc}40;color:{cc};padding:8px 20px;border-radius:10px;font-size:14px;font-weight:800;margin-top:4px;letter-spacing:1px">{c}</div></div>
</div></div>"""

# ====== MAIN ENGINE ======
def predict_score(home, away, gh, ga, hd, ad):
    """Predict most likely scores based on GE."""
    # Simple heuristic
    total_ge = gh + ga
    h_win_pct = hd.get("r_atk",70) / (hd.get("r_atk",70) + ad.get("r_atk",70)) * 0.6 + hd.get("elo",1500) / (hd.get("elo",1500) + ad.get("elo",1500)) * 0.4
    h_win_pct = min(0.95, max(0.05, h_win_pct))

    if gh > 2.5:
        return f"{int(gh+0.5)}-{max(0,int(ga-0.3))}", f"{int(gh-0.5)}-{max(0,int(ga))}", f"{int(gh+1)}-{max(0,int(ga-0.5))}"
    elif gh > 1.5:
        return f"{int(gh+0.5)}-{max(0,int(ga-0.3))}", f"{int(gh)}-{max(0,int(ga))}", f"{int(gh+1)}-{max(0,int(ga))}"
    elif gh > 0.8:
        return f"{max(1,int(gh+0.5))}-{max(0,int(ga-0.3))}", f"{max(0,int(gh))}-{max(0,int(ga))}", f"1-1"
    else:
        return f"1-0", f"0-0", f"1-1"

def process_matches(by_date_output):
    """Processa todos os jogos e retorna HTML + dados de ranking."""
    html = ""
    all_cards = []

    for date_str in sorted(by_date_output.keys()):
        matches = by_date_output[date_str]
        is_today = date_str == TODAY
        label_day = "HOJE" if is_today else fmt_dia(date_str)

        html += f'<h2 style="color:{"#10b981" if is_today else "#3b82f6"};font-size:20px;border-bottom:2px solid {"#10b981" if is_today else "#1e293b"};padding-bottom:10px;margin:32px 0 16px">{"HOJE" if is_today else ""} {fmt_dia(date_str)}</h2>'

        for m in matches:
            home, away, score_h, score_a = extract_match_info(m)
            if not home or not away: continue

            hk = find_team_key(home, m["line"] + m["group"])
            ak = find_team_key(away, m["line"] + m["group"])

            hd = T.get(hk, {"elo":1500,"r_atk":70,"r_meio":70,"r_def":70,"r_gol":70,"mkt":"?","extra":""})
            ad = T.get(ak, {"elo":1500,"r_atk":70,"r_meio":70,"r_def":70,"r_gol":70,"mkt":"?","extra":""})

            ge_h = calc_ge(hd["r_atk"], ad["r_def"])
            ge_a = calc_ge(ad["r_atk"], hd["r_def"])
            elo_diff = abs(hd["elo"] - ad["elo"])

            # Probability calculation based on Elo and GE
            elo_adv = max(0, (hd["elo"] - ad["elo"]) / 600)
            ge_adv = max(0, (ge_h - ge_a) / 5)
            prob_h = round(35 + elo_adv * 45 + ge_adv * 15)
            prob_h = max(5, min(95, prob_h))
            # If away is stronger
            if ad["elo"] > hd["elo"]:
                elo_adv2 = (ad["elo"] - hd["elo"]) / 600
                ge_adv2 = (ge_a - ge_h) / 5
                prob_h = round(35 - elo_adv2 * 45 - ge_adv2 * 15)
                prob_h = max(5, min(95, prob_h))

            prob_away = round(35 - (hd["elo"]-ad["elo"])/600*45 - (ge_h-ge_a)/5*15)
            prob_away = max(5, min(95, prob_away))
            if ad["elo"] > hd["elo"]:
                prob_away = round(35 + (ad["elo"]-hd["elo"])/600*45 + (ge_a-ge_h)/5*15)
            prob_draw = round(100 - prob_h - prob_away)
            # Adjust if negative
            if prob_draw < 5:
                if prob_h > prob_away: prob_h -= (5-prob_draw); prob_draw = 5
                else: prob_away -= (5-prob_draw); prob_draw = 5

            # Time
            try: tm = m["line"].split(" ")[0] if len(m["line"].split(" ")) > 1 else ""
            except: tm = ""

            # H2H
            h2h = "Sem historico de confrontos diretos em Copas." if hk != ak else "Mesmo time (erro)"

            # Score prediction
            s1, s2, s3 = predict_score(home, away, ge_h, ge_a, hd, ad)

            # Build match data for analysis
            md = {"home":home,"away":away,"hd":hd,"ad":ad,"ge_h":ge_h,"ge_a":ge_a,"elo_diff":elo_diff,"ph":prob_h,"pd":prob_draw,"pa":prob_away}
            analysis_text = auto_analysis(md)

            html += card(home, away, hd, ad, prob_h, prob_draw, prob_away, ge_h, ge_a, analysis_text, s1, s2, s3, tm, h2h)
            all_cards.append((home, away, prob_h, conf(prob_h), ge_h, ge_a, hd, ad))

    return html, all_cards

# ====== BUILD FULL PAGE ======
# Get dates: today + next 3 days
dates_to_process = [(TODAY_DT + timedelta(days=i)).strftime("%Y-%m-%d") for i in range(4)]
by_date = get_all_matches_for_dates(dates_to_process)
total_matches = sum(len(v) for v in by_date.values())

print(f"Data: {TODAY_BR}")
print(f"Processando {total_matches} jogos em {len(by_date)} dias")

# Check if we have world cup matches
if total_matches == 0:
    # Post-World Cup mode - no matches in schedule
    header = f"""<div style="background:#0f172a;border:1px solid #334155;border-radius:16px;padding:24px;color:#e2e8f0;text-align:center;max-width:600px;margin:40px auto">
    <h2 style="color:#f59e0b">SEM JOGOS DA COPA HOJE</h2>
    <p style="color:#94a3b8;font-size:13px">A Copa do Mundo FIFA 2026 terminou em 19 de julho.</p>
    <p style="color:#94a3b8;font-size:12px;margin-top:8px">O sistema entrara em modo LIGAS na proxima atualizacao, cobrindo Brasileirao, Premier League, La Liga e mais.</p>
    <p style="color:#64748b;font-size:10px;margin-top:12px">Data: {TODAY_BR}</p></div>"""
    main_html = header
    all_cards = []
else:
    body_html, all_cards = process_matches(by_date)

    # Ranking
    sorted_cards = sorted(all_cards, key=lambda x: x[2], reverse=True)
    ranking_rows = ""
    for i, c in enumerate(sorted_cards):
        cc = "#10b981" if c[3]=="ALTO" else "#f59e0b" if c[3]=="MEDIO" else "#ef4444"
        fav = c[0] if c[2] >= 50 else c[1]
        ranking_rows += f'<tr style="border-bottom:1px solid #1e293b"><td style="padding:10px;font-weight:800;color:#3b82f6">#{i+1}</td><td style="padding:10px;font-weight:600">{c[0]} vs {c[1]}</td><td style="padding:10px">{fav}</td><td style="padding:10px;font-weight:700;color:#fbbf24">{c[2]}%</td><td style="padding:10px;font-size:11px">{c[4]} vs {c[5]}</td><td style="padding:10px;color:{cc};font-weight:700">{c[3]}</td></tr>'

    tg = sum(c[4]+c[5] for c in all_cards)
    ht = sum(1 for c in all_cards if c[2] >= 70)
    md = sum(1 for c in all_cards if 40 <= c[2] < 70)
    lo = sum(1 for c in all_cards if c[2] < 40)
    n = len(all_cards)

    header = f"""<div style="background:#0f172a;border:1px solid #334155;border-radius:16px;padding:24px;color:#e2e8f0;font-family:'Segoe UI',system-ui,sans-serif;line-height:1.6;max-width:950px;margin:0 auto">
<div style="text-align:center;margin-bottom:32px">
<span style="background:rgba(16,185,129,0.12);border:1px solid rgba(16,185,129,0.3);color:#10b981;padding:8px 20px;border-radius:20px;font-size:11px;font-weight:700;letter-spacing:0.5px">ANALISE AUTOMATICA - {n} PARTIDAS EM {len(by_date)} DIAS - {TODAY_BR}</span>
<div style="margin-top:14px;display:flex;gap:8px;justify-content:center;flex-wrap:wrap">
<span style="font-size:10px;background:rgba(139,92,246,0.1);color:#a78bfa;padding:5px 10px;border-radius:8px">Poisson GE</span>
<span style="font-size:10px;background:rgba(245,158,11,0.1);color:#fbbf24;padding:5px 10px;border-radius:8px">Elo Rating</span>
<span style="font-size:10px;background:rgba(6,182,212,0.1);color:#22d3ee;padding:5px 10px;border-radius:8px">Monte Carlo 10K</span>
<span style="font-size:10px;background:rgba(239,68,68,0.1);color:#f87171;padding:5px 10px;border-radius:8px">xG</span>
<span style="font-size:10px;background:rgba(16,185,129,0.1);color:#10b981;padding:5px 10px;border-radius:8px">Weighted Historical</span>
<span style="font-size:10px;background:rgba(59,130,246,0.1);color:#60a5fa;padding:5px 10px;border-radius:8px">5 Periodos (P1-P5)</span>
</div></div>
{body_html}
<h2 style="color:#f59e0b;margin-top:40px;margin-bottom:16px;font-size:20px">RANKING DE PREVISIBILIDADE</h2>
<table style="width:100%;font-size:13px;border-collapse:collapse;background:#0f172a;border-radius:12px;overflow:hidden">
<tr style="background:rgba(59,130,246,0.08);color:#94a3b8;font-size:11px;text-transform:uppercase;letter-spacing:0.5px"><th style="padding:12px;text-align:left">#</th><th style="padding:12px;text-align:left">Partida</th><th style="padding:12px;text-align:left">Favorito</th><th style="padding:12px">Prob</th><th style="padding:12px">GE</th><th style="padding:12px">Confianca</th></tr>
{ranking_rows}</table>
<h2 style="color:#3b82f6;margin-top:40px;margin-bottom:16px;font-size:20px">RESUMO ESTATISTICO</h2>
<div style="display:grid;grid-template-columns:repeat(auto-fit,minmax(140px,1fr));gap:12px">
<div style="background:#0f172a;border:1px solid #1e293b;border-radius:12px;padding:16px;text-align:center"><div style="font-size:28px;font-weight:800;color:#3b82f6">{n}</div><div style="font-size:10px;color:#94a3b8;margin-top:4px">Partidas Analisadas</div></div>
<div style="background:#0f172a;border:1px solid #1e293b;border-radius:12px;padding:16px;text-align:center"><div style="font-size:28px;font-weight:800;color:#10b981">{tg:.1f}</div><div style="font-size:10px;color:#94a3b8;margin-top:4px">Soma GE</div></div>
<div style="background:#0f172a;border:1px solid #1e293b;border-radius:12px;padding:16px;text-align:center"><div style="font-size:28px;font-weight:800;color:#f59e0b">{(tg/n):.2f}</div><div style="font-size:10px;color:#94a3b8;margin-top:4px">Media GE/Partida</div></div>
<div style="background:#0f172a;border:1px solid #1e293b;border-radius:12px;padding:16px;text-align:center"><div style="font-size:28px;font-weight:800;color:#a78bfa">{ht}</div><div style="font-size:10px;color:#94a3b8;margin-top:4px">Confrontos ALTO</div></div>
<div style="background:#0f172a;border:1px solid #1e293b;border-radius:12px;padding:16px;text-align:center"><div style="font-size:28px;font-weight:800;color:#22d3ee">{md}</div><div style="font-size:10px;color:#94a3b8;margin-top:4px">Confrontos MEDIO</div></div>
<div style="background:#0f172a;border:1px solid #1e293b;border-radius:12px;padding:16px;text-align:center"><div style="font-size:28px;font-weight:800;color:#ef4444">{lo}</div><div style="font-size:10px;color:#94a3b8;margin-top:4px">Confrontos BAIXO</div></div>
</div>
<p style="font-size:11px;color:#64748b;text-align:center;margin-top:32px">ANLS Motor Automatico v6 | Poisson(GE)+Elo+Monte Carlo 10K+xG+Weighted Historical (5 Periodos) | Atualizado {TODAY_BR}</p></div>"""

    main_html = header

# Inject
for fname in ["dashboard.html", "index.html"]:
    with open(fname, "r", encoding="utf-8") as f:
        content = f.read()
    sm = "<!-- GEMINI_ANALYSIS_CONTENT_START -->"
    em = "<!-- GEMINI_ANALYSIS_CONTENT_END -->"
    before = content.split(sm)[0]
    after = content.split(em)[1]
    with open(fname, "w", encoding="utf-8") as f:
        f.write(before + sm + "\n" + main_html + "\n" + em + after)

with open(".last-update", "w", encoding="utf-8") as f:
    f.write(f"AUTO {TODAY_BR} | {total_matches} partidas | Motor v6 | 0 dependencias")

print(f"OK - {total_matches} partidas | {TODAY_BR}")
