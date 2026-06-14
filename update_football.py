#!/usr/bin/env python3
"""
⚽ ANLS — Análise Diária com Gemini 2.0 Flash (100% GRÁTIS)
GitHub Actions roda todo dia às 7:00 Brasília
Injeta a análise direto no dashboard.html
"""
import sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

import os, re, json, time
from datetime import datetime, timezone, timedelta
from google import genai

# ── Config ──────────────────────────────────────────
API_KEY = os.environ.get("GEMINI_API_KEY")
if not API_KEY:
    print("❌ ERRO: GEMINI_API_KEY não configurada no GitHub Secrets!")
    print("   1. Vá em https://aistudio.google.com/apikey")
    print("   2. Clique 'Create API Key'")
    print("   3. No GitHub: Settings → Secrets → Actions → New → GEMINI_API_KEY")
    exit(1)

client = genai.Client(api_key=API_KEY)
BRT = timezone(timedelta(hours=-3))
TODAY = datetime.now(BRT).strftime("%Y-%m-%d")
TODAY_BR = datetime.now(BRT).strftime("%d/%m/%Y")

# ── Calendário ───────────────────────────────────────
SCHEDULE = """
GRUPO A: México🇲🇽, Coreia do Sul🇰🇷, Tchéquia🇨🇿, África do Sul🇿🇦
11/06 15:00 México 2-0 África do Sul | Quiñones 9', Jiménez 67'
12/06 14:00 Coreia do Sul 2-1 Tchéquia | Krejčí 59' CZE | Hwang 67', Oh 80' KOR
18/06 16:00 Tchéquia vs África do Sul (Mercedes-Benz, Atlanta)
18/06 20:00 México vs Coreia do Sul (Akron, Guadalajara)
24/06 20:00 Tchéquia vs México (Azteca, Cidade do México)
24/06 20:00 África do Sul vs Coreia do Sul (BBVA, Monterrey)

GRUPO B: Canadá🇨🇦, Bósnia🇧🇦, Catar🇶🇦, Suíça🇨🇭
12/06 20:00 Canadá 1-1 Bósnia | Lukić 21' BIH | Larin 78' CAN
13/06 16:00 Catar 1-1 Suíça | Embolo 17'(p) SUI | Khoukhi 90+4' QAT
18/06 14:00 Suíça vs Bósnia (SoFi, Los Angeles)
19/06 20:00 Canadá vs Catar (BC Place, Vancouver)
24/06 16:00 Suíça vs Canadá (BC Place, Vancouver)
24/06 16:00 Bósnia vs Catar (Lumen Field, Seattle)

GRUPO C: Brasil🇧🇷, Marrocos🇲🇦, Escócia🏴󠁧󠁢󠁳󠁣󠁴󠁿, Haiti🇭🇹
13/06 14:00 Haiti 0-1 Escócia | McGinn 29'
13/06 20:00 Brasil 1-1 Marrocos | Saibari 21' MAR | Vini Jr 32' BRA
19/06 20:00 Escócia vs Marrocos (Gillette, Boston)
19/06 14:00 Brasil vs Haiti (Lincoln Financial, Philadelphia)
24/06 14:00 Escócia vs Brasil (Hard Rock, Miami)
24/06 14:00 Marrocos vs Haiti (Mercedes-Benz, Atlanta)

GRUPO D: EUA🇺🇸, Paraguai🇵🇾, Austrália🇦🇺, Turquia🇹🇷
12/06 20:00 EUA 4-1 Paraguai | Mauricio 7' PAR | Balogun 31' 45+5', Bobadilla(OG) 73', Reyna 90+8' USA
13/06 23:00 Austrália 2-0 Turquia | Irankunda 27', Metcalfe 75'
19/06 16:00 Turquia vs Paraguai (Levi's, San Francisco)
19/06 20:00 EUA vs Austrália (Lumen Field, Seattle)
25/06 20:00 Turquia vs EUA (SoFi, Los Angeles)
25/06 20:00 Paraguai vs Austrália (Levi's, San Francisco)

GRUPO E: Alemanha🇩🇪, Curaçao🇨🇼, Costa do Marfim🇨🇮, Equador🇪🇨
14/06 14:00 Alemanha vs Curaçao (NRG Stadium, Houston)
14/06 20:00 Costa do Marfim vs Equador (Lincoln Financial, Philadelphia)
20/06 16:00 Alemanha vs Costa do Marfim (BMO Field, Toronto)
20/06 20:00 Equador vs Curaçao (Arrowhead, Kansas City)
25/06 16:00 Equador vs Alemanha (MetLife, NY/NJ)
25/06 16:00 Curaçao vs Costa do Marfim (Lincoln Financial, Philadelphia)

GRUPO F: Holanda🇳🇱, Japão🇯🇵, Suécia🇸🇪, Tunísia🇹🇳
14/06 17:00 Holanda vs Japão (AT&T Stadium, Dallas)
14/06 23:00 Suécia vs Tunísia (BBVA, Monterrey)
20/06 14:00 Holanda vs Suécia (NRG Stadium, Houston)
20/06 18:00 Tunísia vs Japão (BBVA, Monterrey)
25/06 20:00 Japão vs Suécia (AT&T Stadium, Dallas)
25/06 20:00 Tunísia vs Holanda (Arrowhead, Kansas City)

GRUPO G: Bélgica🇧🇪, Egito🇪🇬, Irã🇮🇷, Nova Zelândia🇳🇿
15/06 14:00 Bélgica vs Egito (Lumen Field, Seattle)
15/06 20:00 Irã vs Nova Zelândia (SoFi, Los Angeles)
21/06 14:00 Bélgica vs Irã (SoFi, Los Angeles)
21/06 20:00 Nova Zelândia vs Egito (BC Place, Vancouver)
26/06 16:00 Egito vs Irã (Lumen Field, Seattle)
26/06 16:00 Nova Zelândia vs Bélgica (BC Place, Vancouver)

GRUPO H: Espanha🇪🇸, Uruguai🇺🇾, Arábia Saudita🇸🇦, Cabo Verde🇨🇻
15/06 16:00 Espanha vs Cabo Verde (Mercedes-Benz, Atlanta)
15/06 18:00 Arábia Saudita vs Uruguai (Hard Rock, Miami)
21/06 16:00 Espanha vs Arábia Saudita (Mercedes-Benz, Atlanta)
21/06 20:00 Uruguai vs Cabo Verde (Hard Rock, Miami)
26/06 18:00 Cabo Verde vs Arábia Saudita (NRG, Houston)
26/06 18:00 Uruguai vs Espanha (Akron, Guadalajara)

GRUPO I: França🇫🇷, Senegal🇸🇳, Noruega🇳🇴, Iraque🇮🇶
16/06 14:00 França vs Senegal (MetLife, NY/NJ)
16/06 20:00 Iraque vs Noruega (Gillette, Boston)
22/06 14:00 Noruega vs Senegal (MetLife, NY/NJ)
22/06 20:00 França vs Iraque (Lincoln Financial, Philadelphia)
26/06 20:00 Noruega vs França (Gillette, Boston)
26/06 20:00 Senegal vs Iraque (BMO Field, Toronto)

GRUPO J: Argentina🇦🇷, Argélia🇩🇿, Áustria🇦🇹, Jordânia🇯🇴
16/06 20:00 Argentina vs Argélia (Arrowhead, Kansas City)
17/06 14:00 Áustria vs Jordânia (Levi's, San Francisco)
22/06 16:00 Argentina vs Áustria (AT&T, Dallas)
22/06 18:00 Jordânia vs Argélia (Levi's, San Francisco)
27/06 20:00 Jordânia vs Argentina (Arrowhead, Kansas City)
27/06 20:00 Argélia vs Áustria (AT&T, Dallas)

GRUPO K: Portugal🇵🇹, Congo DR🇨🇩, Uzbequistão🇺🇿, Colômbia🇨🇴
17/06 16:00 Portugal vs Congo DR (NRG, Houston)
17/06 20:00 Uzbequistão vs Colômbia (Azteca, Cidade do México)
23/06 14:00 Portugal vs Uzbequistão (NRG, Houston)
23/06 20:00 Colômbia vs Congo DR (Akron, Guadalajara)
27/06 16:00 Colômbia vs Portugal (Hard Rock, Miami)
27/06 16:00 Congo DR vs Uzbequistão (Mercedes-Benz, Atlanta)

GRUPO L: Inglaterra🏴󠁧󠁢󠁥󠁮󠁧󠁿, Croácia🇭🇷, Gana🇬🇭, Panamá🇵🇦
17/06 20:00 Inglaterra vs Croácia (AT&T, Dallas)
17/06 20:00 Gana vs Panamá (BMO Field, Toronto)
23/06 16:00 Inglaterra vs Gana (Gillette, Boston)
23/06 18:00 Panamá vs Croácia (BMO Field, Toronto)
27/06 14:00 Panamá vs Inglaterra (MetLife, NY/NJ)
27/06 14:00 Croácia vs Gana (Lincoln Financial, Philadelphia)
"""

print("=" * 60)
print("⚽ ANLS — Gemini 2.0 Flash (GRÁTIS)")
print(f"📅 {TODAY_BR}")
print("=" * 60)

# ── 1. Identificar jogos de hoje ─────────────────────
def find_today_matches():
    matches = []
    for line in SCHEDULE.strip().split("\n"):
        if line.startswith("GRUPO") or not line.strip():
            continue
        parts = line.split(" ", 2)
        if len(parts) < 2:
            continue
        try:
            date_str = parts[0]
            day, month = date_str.split("/")
            match_date = f"2026-{month.zfill(2)}-{day.zfill(2)}"
            if match_date == TODAY:
                matches.append(line.strip())
        except:
            continue
    return matches

today_matches = find_today_matches()
print(f"\n📋 {len(today_matches)} jogo(s) hoje")

# ── 2. Coletar resultados já ocorridos ───────────────
completed = []
for line in SCHEDULE.strip().split("\n"):
    if not line.startswith("GRUPO") and re.search(r'\d+-\d+', line):
        completed.append(line.strip())
print(f"✅ {len(completed)} resultados registrados")

# ── 3. Chamar Gemini ─────────────────────────────────
def ask_gemini(prompt, retries=3):
    """Chama Gemini com retry automático e fallback entre modelos gratuitos."""
    models = [
        "gemini-2.0-flash",
        "gemini-2.5-flash-lite",
        "gemini-1.5-flash",
        "gemini-1.5-flash-8b",
    ]
    for attempt in range(retries):
        model = models[attempt % len(models)]
        try:
            print(f"   🤖 Tentativa {attempt+1}/{retries} — modelo: {model}")
            resp = client.models.generate_content(
                model=model,
                contents=prompt,
                config={"temperature": 0.4, "max_output_tokens": 8192}
            )
            print(f"   ✅ Resposta recebida ({len(resp.text)} caracteres)")
            return resp.text
        except Exception as e:
            err = str(e)
            if "429" in err or "RESOURCE_EXHAUSTED" in err or "quota" in err.lower():
                wait = 15 * (attempt + 1)
                print(f"   ⏳ Cota cheia — aguardando {wait}s...")
                time.sleep(wait)
            elif "404" in err or "not found" in err.lower():
                print(f"   ⚠️ Modelo {model} indisponível, tentando próximo...")
                continue
            else:
                print(f"   ⚠️ Erro: {e}")
                continue
    return None

# Se não tem jogos hoje, gera resumo geral
if not today_matches:
    print("\n📅 Dia sem jogos da Copa — gerando resumo...")
    prompt = f"""Data: {TODAY_BR}. Calendário da Copa 2026:
{SCHEDULE}

Escreva um resumo profissional em português (formato HTML) sobre o status atual da Copa 2026:
- Resultados já ocorridos e destaques
- Próximos jogos
- Artilheiros até agora
- Classificação atual dos grupos conforme resultados
- Curiosidades e estatísticas

Use tags HTML: <h2>, <h3>, <p>, <table>, <tr>, <td>, <strong>, <span style="color:...">
Máximo 500 palavras. Tom de analista esportivo profissional."""
else:
    print("\n🧠 Gerando análise dos jogos de hoje...")
    prompt = f"""Data: {TODAY_BR}. Calendário completo:
{SCHEDULE}

JOGOS DE HOJE:
{chr(10).join(today_matches)}

TAREFA: Análise profissional em português (formato HTML). Incluir:

1. <h2>📋 Jogos de Hoje</h2> - lista com horário e estádio
2. <h2>📊 Análise Tática</h2> - para CADA jogo de hoje:
   - Probabilidade de vitória/empate (estimativa fundamentada)
   - Pontos fortes e fracos de cada time
   - Jogador-chave de cada lado
   - Placar mais provável
3. <h2>📈 Classificação Atual</h2> - tabela dos grupos com os resultados reais
4. <h2>⚽ Artilheiros da Copa</h2> - lista dos goleadores
5. <h2>🔮 Palpites do Dia</h2> - resumo dos palpites para hoje

Use tags HTML com estilo inline (style="color:#10b981" para verde, #ef4444 para vermelho, #f59e0b para amarelo, #3b82f6 para azul).
Fundo escuro: background:#111827; color:#e2e8f0. Máximo 800 palavras."""

print("🤖 Consultando Gemini 2.0 Flash (grátis)...")
analysis = ask_gemini(prompt)

if not analysis:
    analysis = f"""<div style="background:#111827;border:1px solid #1e293b;border-radius:14px;padding:24px;color:#e2e8f0;text-align:center">
<h2 style="color:#f59e0b">⚠️ Análise Indisponível</h2>
<p>O Gemini não pôde gerar a análise neste momento.</p>
<p style="font-size:12px;color:#94a3b8;margin-top:12px">O sistema tentará novamente amanhã às 7:00 (Brasília).</p>
<p style="font-size:12px;color:#94a3b8">Data da tentativa: {TODAY_BR}</p>
</div>"""

# ── 4. Injetar no dashboard ──────────────────────────
print("💾 Injetando análise no dashboard...")

def inject_into_html(filepath, content):
    with open(filepath, "r", encoding="utf-8") as f:
        html = f.read()

    # Limpa marcadores de código markdown que o Gemini às vezes inclui
    content = re.sub(r'^```(?:html)?\s*\n?', '', content, count=1)
    content = re.sub(r'\n?\s*```\s*$', '', content, count=1)
    content = re.sub(r'^<body[^>]*>', '', content)
    content = re.sub(r'</body>\s*$', '', content)

    start_marker = "<!-- ⬇️ GEMINI_ANALYSIS_CONTENT_START ⬇️ -->"
    end_marker = "<!-- ⬆️ GEMINI_ANALYSIS_CONTENT_END ⬆️ -->"

    before = html.split(start_marker)[0]
    after = html.split(end_marker)[1]

    wrapper = f'''{start_marker}
<div style="background:#111827;border:1px solid #1e293b;border-radius:14px;padding:24px;color:#e2e8f0;font-family:'Segoe UI',system-ui,sans-serif;line-height:1.7">
<div style="text-align:center;margin-bottom:16px;padding:8px 16px;background:rgba(16,185,129,0.1);border:1px solid rgba(16,185,129,0.3);border-radius:20px;display:inline-block;font-size:11px;font-weight:700;color:#10b981">
🟢 GERADO POR GEMINI 2.0 FLASH (GRÁTIS) — {TODAY_BR} às {datetime.now(BRT).strftime('%H:%M')}
</div>
{content}
<hr style="border-color:#1e293b;margin:20px 0">
<div style="font-size:10px;color:#64748b;text-align:center;margin-top:16px">
⚡ Atualizado automaticamente todo dia às 7:00 (Brasília) via GitHub Actions<br>
🤖 Inteligência: Gemini 2.0 Flash (Google AI — 100% gratuito) |
📅 Próxima atualização: amanhã às 7:00 BRT
</div>
</div>
{end_marker}'''

    new_html = before + wrapper + after
    with open(filepath, "w", encoding="utf-8") as f:
        f.write(new_html)

# Atualiza dashboard.html e index.html
inject_into_html("dashboard.html", analysis)
inject_into_html("index.html", analysis)

# ── 5. Registrar ─────────────────────────────────────
with open(".last-update", "w", encoding="utf-8") as f:
    f.write(f"{datetime.now(BRT).strftime('%Y-%m-%d %H:%M BRT')} | Gemini 2.0 Flash | {len(today_matches)} jogos hoje | ✅")

print()
print("=" * 60)
print("✅ ATUALIZAÇÃO CONCLUÍDA COM SUCESSO")
print(f"📅 {TODAY_BR}")
print(f"📋 {len(today_matches)} jogos hoje")
print(f"✅ {len(completed)} resultados na base")
print(f"🤖 Análise Gemini injetada no dashboard")
print(f"🌐 https://fut-otez.onrender.com")
print("=" * 60)
