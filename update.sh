#!/bin/bash
# ⚽ ANLS — Script de atualização diária
# Executado pelo GitHub Actions todo dia às 7:00 (Brasília)

set -e
TODAY=$(date +%Y-%m-%d)
echo "=========================================="
echo "⚽ ANLS — Atualização Diária"
echo "Data: $TODAY"
echo "=========================================="

# Verifica quais jogos são hoje
TODAY_MATCHES=$(grep -c "\"$TODAY\"" dashboard.html 2>/dev/null || echo "0")
echo "Jogos hoje: $TODAY_MATCHES"

# Verifica se há resultados novos para coletar
# (Este script pode ser expandido com APIs reais de futebol)
# Por enquanto, registra a execução

echo "✅ Verificação concluída em $(date)"
echo "📊 Dashboard: https://fut-otez.onrender.com"
