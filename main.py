import sys
import os
from dotenv import load_dotenv

# Adiciona o diretório src ao path para importações
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from sources.mlh import fetch_mlh
from sources.tabnews import fetch_tabnews
from sources.devpost import fetch_devpost
from scorer import AIScorer
from database import save_opportunity, init_db

load_dotenv()

def run_aggregator():
    print("🚀 Iniciando Opportunity Aggregator Inteligente...")
    init_db()
    
    # 1. Coleta de dados
    all_opportunities = []
    
    print("📡 Coletando do MLH...")
    all_opportunities.extend(fetch_mlh())
    
    print("📡 Coletando do TabNews...")
    all_opportunities.extend(fetch_tabnews())
    
    print("📡 Coletando do Devpost...")
    all_opportunities.extend(fetch_devpost())

    print(f"✅ Total de {len(all_opportunities)} oportunidades encontradas.")

    # 2. Pontuação por IA
    print("🧠 Iniciando pontuação inteligente com Gemini...")
    scorer = AIScorer()
    scored_opportunities = []
    
    # Limit score to avoid rate limit in tests, but process enough to be useful
    for opp in all_opportunities[:20]:
        print(f"   🧐 Avaliando: {opp['title'][:50]}...")
        score, rationale = scorer.score_opportunity(opp)
        opp['score'] = score
        opp['rationale'] = rationale
        scored_opportunities.append(opp)

    # 3. Salvamento no Banco
    print("💾 Salvando no banco de dados...")
    saved_count = save_opportunity(scored_opportunities)
    print(f"✨ {saved_count} novas oportunidades salvas com sucesso!")

    # 4. Sumário das melhores
    top_matches = sorted(scored_opportunities, key=lambda x: x['score'], reverse=True)[:5]
    
    print("\n" + "="*50)
    print("🏆 TOP 5 MATCHES DO DIA")
    print("="*50)
    for i, opp in enumerate(top_matches, 1):
        print(f"{i}. [{opp['score']}%] {opp['title']}")
        print(f"   🔗 {opp['url']}")
        print(f"   💡 {opp['rationale']}\n")
    
    # 5. Estratégia do Dia
    print("="*50)
    print("🎯 ESTRATÉGIA RECOMENDADA")
    print("="*50)
    strategy = scorer.generate_daily_strategy(scored_opportunities)
    print(strategy)
    print("="*50)

if __name__ == "__main__":
    run_aggregator()
