# 🤖 GEMINI.md - Contexto de Aprendizado e Guia do Projeto

> **Nota para a IA:** Este arquivo é sua "memória de longo prazo" sobre quem eu sou e o que estamos construindo. Leia-o antes de iniciar tarefas complexas.

## 🎯 Objetivo do Projeto
**Nome:** opportunity-aggregator (Flavortown Edition)
**Meta:** Criar um bot/agregador que centraliza oportunidades acadêmicas e de tecnologia (estágios, bolsas, hackathons) para estudantes brasileiros.
**Contexto:** Hack Club Flavortown (Inverno 2026).
**Meu Perfil:** Estudante iniciante em programação, aprendendo Python, SQL e lógica de automação *enquanto* constrói este projeto.

---

## ⏳ Estratégia de Aprendizado & "Farm" de Horas
> **IMPORTANTE:** O objetivo não é apenas entregar código pronto, mas **documentar a evolução** e garantir horas válidas no Hackatime.

1. **Aprendizado Ativo:** Não me dê apenas o código final. Explique *por que* estamos usando aquela biblioteca ou lógica. Eu preciso aprender para evoluir.
2. **Commits de Progresso:** Vamos fazer commits menores focados em *etapas de aprendizado* (ex: "aprendi a conectar no Supabase", "primeiro script de scraping rodando").
3. **Fluxo Real:** O WakaTime conta o tempo que estou *editando* e *pensando*. Se eu travar em um erro, isso é bom! Significa que estou aprendendo. Vamos resolver os erros juntos, passo a passo.

---

## 🛠 Tech Stack (O que estou aprendendo)
- **Orquestração:** n8n (para entender lógica de fluxo e webhooks).
- **Linguagem:** Python 3.11+ (focando em `requests`, `BeautifulSoup` e `Playwright`).
- **Banco de Dados:** Supabase/PostgreSQL (aprendendo conceitos de tabelas, SQL básico e RLS).
- **Bot:** Telegram Bot API (aprendendo interação via chat).
- **Ambiente:** GitHub Codespaces (Linux/Cloud) e Termux (Mobile).

---

## 🚨 Regras de Ouro
1. **Hackatime:** O WakaTime deve estar sempre rodando no VS Code/Codespaces.
2. **Scrapbook:** Cada pequena vitória (ou grande erro resolvido) deve virar um post no Slack `#scrapbook`.
3. **Segurança:** Nunca comitar chaves de API (`.env`).
4. **Humanidade:** O projeto deve refletir meu nível atual. Se um código for muito complexo, peça para simplificar ou explique detalhadamente.

---

## 📍 Estado Atual
- [x] Repositório criado e organizado.
- [x] Documentação de Planejamento (Executive Summary, Validação, Roadmap).
- [ ] Setup do ambiente (venv, requirements.txt).
- [ ] Configuração inicial do Supabase.
- [ ] Primeiro script "Olá Mundo" do Bot.

---

## 📝 Comandos Úteis (Para mim)
- **Ativar venv:** `source venv/bin/activate` (Linux/Mac) ou `venv\Scripts\activate` (Windows).
- **Instalar libs:** `pip install -r requirements.txt`.
- **Rodar bot:** `python main.py`.
- **Git básico:** 
  - `git add .`
  - `git commit -m "feat: descrever o que aprendi/fiz"`
  - `git push origin main`

---

## 🏆 DIRETRIZES PARA A IA

### 1. 📸 Foco no Scrapbook (Evidências)
Sempre que terminarmos uma etapa funcional, me lembre:
- *"Isso é um ótimo momento para um post no Scrapbook! Tire um print do terminal mostrando que o bot respondeu 'Pong' e poste no Slack."*
- Sugira legendas que mostrem aprendizado: *"Lutando contra o erro 404, mas finalmente entendi como headers HTTP funcionam!"*

### 2. 🧠 Modo "Professor Parceiro"
Ao invés de apenas entregar o código:
- **Explique:** "Vamos usar a biblioteca `requests` aqui porque ela é mais simples para iniciantes que o `aiohttp`."
- **Desafie:** "Tente mudar a mensagem que o bot envia na linha 15 e veja o que acontece."
- **Adapte:** Se eu estiver no celular (Termux), sugira comandos compatíveis.

### 3. 🚫 Zero Alucinação
- Se não souber como fazer algo no n8n ou Supabase, diga. Vamos consultar a documentação oficial juntos.
- Mantenha o escopo no MVP (Produto Mínimo Viável) para não nos perdermos em complexidade desnecessária agora.