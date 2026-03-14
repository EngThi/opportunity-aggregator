# Opportunity Aggregator 🚀

Seu assistente inteligente para encontrar Bolsas, Hackathons e Vagas Tech em tempo real.

## 📁 Estrutura do Projeto
- `src/sources/`: Scrapers para Devpost, MLH, TabNews e GitHub Jobs.
- `src/scorer.py`: Inteligência Artificial (Gemini) calculando seu match com a vaga.
- `src/notifier.py`: Notificações formatadas para o Telegram.
- `bot.py`: Interface do usuário via bot.
- `main.py`: Scheduler diário de sincronização.

## 🚀 Quick Start
1. Instale as dependências:
   ```bash
   pip install -r requirements.txt
   ```
2. Configure seu `.env`:
   ```bash
   cp .env.example .env
   # Adicione seu TELEGRAM_BOT_TOKEN e GEMINI_API_KEY
   ```
3. Inicie o buscador diário:
   ```bash
   python main.py
   ```
4. Inicie o Bot:
   ```bash
   python bot.py
   ```

## 🤖 Comandos do Bot
- `/start`: Apresentação.
- `/search <termo>`: Busca rápida no banco local.
- `/today`: Oportunidades frescas coletadas hoje.
- `/match`: Envie suas skills e a IA dirá quais as 3 melhores oportunidades para você agora.

## 🔗 Sources
- [Devpost](https://devpost.com/hackathons)
- [MLH](https://mlh.io/seasons/2026/events)
- [TabNews](https://www.tabnews.com.br/)
- [GitHub Jobs](https://github.com/search?q=label%3Ajob+is%3Aopen&type=issues)
