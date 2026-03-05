# Changelog — Validador Lemos

Todas as mudanças relevantes do projeto são documentadas aqui.
Formato baseado em [Keep a Changelog](https://keepachangelog.com/pt-BR/1.0.0/).

---

## [1.1.0] — 2025-03-05

### Adicionado
- **Avaliação por Revista (campo livre):** O usuário pode digitar o nome de qualquer revista científica na interface. O sistema avalia compatibilidade temática, de escopo e de rigor entre o artigo e a revista informada.
- **Score de Compatibilidade (0–10):** Novo indicador visual com barra de progresso exclusiva para o fit com a revista.
- **Veredito de Compatibilidade:** Quatro categorias — `EXCELENTE FIT`, `BOM FIT`, `FIT MARGINAL`, `INCOMPATÍVEL`.
- **Justificativa de Compatibilidade:** Explicação em português gerada pelo modelo sobre o motivo do score.
- **Alerta visual contextual:** Mensagem de sucesso/aviso/erro baseada no score de compatibilidade, alertando sobre risco de desk-rejection.
- Campo de revista é **completamente opcional** — análise funciona normalmente sem preenchimento.

### Alterado
- `engine.py`: método `analyze()` agora aceita o parâmetro opcional `journal_name`. O prompt ao Gemini inclui dinamicamente o bloco de análise de revista apenas quando o campo é preenchido.
- `app.py`: versão atualizada para `v1.1`. Novo campo de texto adicionado antes do botão de validação. Bloco de exibição do resultado de revista renderizado condicionalmente.

---

## [1.0.0] — lançamento inicial

### Adicionado
- Upload de PDF e extração de texto via `pypdf`.
- Análise metodológica com 4 dimensões: rigor estatístico, metodologia, plausibilidade biológica, clareza/novidade.
- Score final ponderado (estatística e metodologia com peso ×3, biologia e novidade com peso ×2).
- Penalidade automática por N baixo (n < 6 por grupo trava rigor estatístico em máximo 4).
- Vereditos: ACEITAR / REVISÃO / REJEITAR.
- Zona de Conflito: Revisor #2 com 5 críticas duras simulando peer review.
- Advogado de Defesa: sugestão de estratégia de rebuttal contra as críticas.
- Fallback automático entre modelos Gemini (`2.5-flash` → `2.5-pro` → `2.0-flash`).
- Interface Streamlit com dashboard de métricas, barra de progresso e abas.
- Script `teste_api.py` para diagnóstico de conexão.
- Script `tudo.py` para consolidação de arquivos do projeto.
- Suporte a execução via `iniciar.bat` no Windows.
