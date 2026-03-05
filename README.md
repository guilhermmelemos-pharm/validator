# 🧬 Validador Lemos

> Ferramenta de análise técnica de artigos científicos para **farmacologia e biologia molecular**, com simulação de peer review e avaliação de compatibilidade com revistas científicas.

![Python](https://img.shields.io/badge/Python-3.10+-blue?logo=python&logoColor=white)
![Streamlit](https://img.shields.io/badge/Streamlit-1.x-FF4B4B?logo=streamlit&logoColor=white)
![Gemini](https://img.shields.io/badge/Google%20Gemini-2.5-4285F4?logo=google&logoColor=white)
![License](https://img.shields.io/badge/license-MIT-green)

---

## 📸 Visão Geral

O Validador Lemos usa o modelo **Gemini 2.5** para analisar manuscritos científicos em PDF, avaliando rigor estatístico, qualidade metodológica e plausibilidade biológica — tudo em português, com score ponderado e veredito final.

---

## ✨ Funcionalidades

- **Análise Metodológica** — Score ponderado em 4 dimensões com veredito ACEITAR / REVISÃO / REJEITAR
- **Penalidade por N Baixo** — Detecta n < 6 por grupo e penaliza automaticamente o rigor estatístico
- **Avaliação por Revista** — Informe qualquer revista científica e receba um score de compatibilidade temática (previne desk-rejection)
- **Revisor #2 Hardcore** — Simula um peer reviewer implacável com 5 objeções técnicas duras
- **Advogado de Defesa** — Gera estratégia de rebuttal científica e polida contra as críticas

---

## 🚀 Instalação

```bash
# 1. Clone o repositório
git clone https://github.com/seu-usuario/validador-lemos.git
cd validador-lemos

# 2. Instale as dependências
python -m pip install -r requirements.txt

# 3. Execute
python -m streamlit run app.py
```

**Windows:** pode usar o `iniciar.bat` diretamente.

---

## 🔑 API Key

Gere sua chave gratuita em: [https://aistudio.google.com/app/apikey](https://aistudio.google.com/app/apikey)

Cole na barra lateral da interface — não é salva em nenhum arquivo.

---

## 📊 Como o Score é Calculado

| Dimensão | Peso |
|---|---|
| Rigor Estatístico | ×3 |
| Metodologia | ×3 |
| Plausibilidade Biológica | ×2 |
| Clareza e Novidade | ×2 |

$$Score = \frac{(Estatística \times 3) + (Metodologia \times 3) + (Biologia \times 2) + (Novidade \times 2)}{10} \times 10$$

| Score | Veredito |
|---|---|
| ≥ 80 | ✅ ACEITAR |
| 50 – 79 | ⚠️ REVISÃO |
| < 50 | ❌ REJEITAR |

> **Penalidade:** se n < 6 por grupo, o score de rigor estatístico é travado em no máximo 4.

---

## 📰 Avaliação por Revista

Digite o nome de qualquer revista no campo opcional antes de validar. O Gemini avalia:

- Compatibilidade temática e de escopo
- Adequação do nível de rigor
- Público-alvo típico da revista

**Exemplos de uso:** `Nature Neuroscience`, `Journal of Urology`, `PLOS ONE`, `Pharmacology & Therapeutics`

**Vereditos possíveis:** `EXCELENTE FIT` · `BOM FIT` · `FIT MARGINAL` · `INCOMPATÍVEL`

---

## 📁 Estrutura do Projeto

```
validador-lemos/
├── app.py                  # Interface Streamlit
├── requirements.txt        # Dependências
├── iniciar.bat             # Atalho Windows
├── core/
│   └── engine.py           # Lógica de análise e API
├── teste_api.py            # Diagnóstico de conexão
└── tudo.py                 # Consolidador de arquivos
```

---

## 🤖 Modelos Utilizados

Fallback automático na seguinte ordem:

1. `gemini-2.5-flash` *(principal)*
2. `gemini-2.5-pro` *(fallback)*

---

## 📝 Changelog

Veja [CHANGELOG.md](CHANGELOG.md) para o histórico completo de versões.

---

*v1.1 — Lemos Lambda Core*
