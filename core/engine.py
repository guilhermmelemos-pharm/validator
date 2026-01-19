import json
from google import genai
from google.genai import types
from pypdf import PdfReader

class ArticleEngine:
    def __init__(self):
        self.client = None

    def configure(self, api_key):
        clean_key = api_key.strip()
        try:
            self.client = genai.Client(api_key=clean_key)
        except Exception as e:
            print(f"Erro config: {e}")

    def _extract_text(self, pdf_file):
        try:
            reader = PdfReader(pdf_file)
            text = ""
            for page in reader.pages[:50]:
                text += page.extract_text() or ""
            return text
        except Exception as e:
            return f"Erro leitura PDF: {str(e)}"

    def analyze(self, pdf_file):
        text_content = self._extract_text(pdf_file)
        
        # LISTA DE MODELOS
        modelos_para_testar = [
            'gemini-2.5-flash',
            'gemini-2.5-pro',
            'gemini-2.0-flash'
        ]

        prompt = f"""
        ROLE: Senior Pharmacology Reviewer.
        TASK: Critically analyze methodology and statistics.
        
        STRICT RULES:
        1. Analyze sample size (n). Is it < 6 per group? Set "flag_n_baixo": true.
        2. SCORES must be Integers (0-10).
        3. OUTPUT strictly JSON.
        
        OUTPUT FORMAT:
        {{
            "flag_n_baixo": <true/false>,
            "scores": {{
                "rigor_estatistico": 0,
                "metodologia": 0,
                "plausibilidade_biologica": 0,
                "clareza_novidade": 0
            }},
            "justificativa": "Text in Portuguese",
            "curadoria": "Text in Portuguese"
        }}
        
        TEXT:
        {text_content}
        """

        erros_log = []

        if not self.client:
            return {"error": "Cliente não configurado."}

        for modelo in modelos_para_testar:
            try:
                response = self.client.models.generate_content(
                    model=modelo,
                    contents=prompt,
                    config=types.GenerateContentConfig(
                        temperature=0.1
                    )
                )
                
                if not response.text:
                    raise ValueError("Resposta vazia")

                clean_text = response.text.replace("```json", "").replace("```", "").strip()
                start = clean_text.find('{')
                end = clean_text.rfind('}') + 1
                if start != -1 and end != -1:
                    clean_text = clean_text[start:end]
                
                dados = json.loads(clean_text)
                
                # --- LÓGICA DE NEGÓCIO ---
                scores = dados.get("scores", {})
                safe_scores = {}
                for k in ["rigor_estatistico", "metodologia", "plausibilidade_biologica", "clareza_novidade"]:
                    try:
                        val = int(float(scores.get(k, 0)))
                        safe_scores[k] = max(0, min(10, val))
                    except:
                        safe_scores[k] = 0
                
                # Mantendo min(4) conforme seu código colado
                if dados.get("flag_n_baixo") is True:
                    safe_scores['rigor_estatistico'] = min(4, safe_scores['rigor_estatistico'])
                
                dados["scores"] = safe_scores
                
                weighted_sum = (
                    safe_scores['rigor_estatistico'] * 3 +
                    safe_scores['metodologia'] * 3 +
                    safe_scores['plausibilidade_biologica'] * 2 +
                    safe_scores['clareza_novidade'] * 2
                )
                final_percent = float(weighted_sum)
                dados["final_score_percent"] = final_percent
                
                if final_percent >= 80:
                    dados["veredito"] = "ACEITAR"
                elif final_percent >= 50:
                    dados["veredito"] = "REVISÃO"
                else:
                    dados["veredito"] = "REJEITAR"
                
                if dados.get("flag_n_baixo") is True:
                    dados["curadoria"] = "⚠️ [ALERTA] Penalidade aplicada: N < 6.\n\n" + dados.get("curadoria", "")

                dados["modelo_usado"] = modelo
                
                # IMPORTANTE: Retornamos o texto cru para o botão usar depois sem reler o PDF
                dados["full_text_hidden"] = text_content
                
                return dados

            except Exception as e:
                erros_log.append(f"{modelo}: {str(e)}")
                continue

        return {
            "error": "Todos falharam.",
            "details": " | ".join(erros_log),
            "scores": {"rigor_estatistico": 0, "metodologia": 0, "plausibilidade_biologica": 0, "clareza_novidade": 0},
            "final_score_percent": 0.0,
            "veredito": "ERRO",
            "justificativa": "Falha na comunicação com a API.",
            "curadoria": "Verifique erros."
        }

    # --- MÉTODO: MODO REVISOR HARDCORE ---
    def generate_hardcore_review(self, text_content):
        prompt = f"""
        ROLE: Ruthless Pharmacology Reviewer ("Reviewer #2").
        TONE: Extremely critical, demanding, skepticism towards small n and controls.
        TASK: Based on the text provided, generate 5 TOUGH questions/objections that could reject this paper.
        FOCUS ON:
        1. Inappropriate statistical tests (e.g., t-test for >2 groups).
        2. Doses justification (is it physiological?).
        3. Lack of controls or blinding.
        4. Overinterpretation of results.
        
        OUTPUT: A Markdown list of 5 bullet points in Portuguese. Direct and harsh.
        
        TEXT:
        {text_content[:30000]} 
        """
        
        try:
            response = self.client.models.generate_content(
                model='gemini-2.5-pro', 
                contents=prompt
            )
            return response.text
        except:
            try:
                response = self.client.models.generate_content(
                    model='gemini-2.5-flash', 
                    contents=prompt
                )
                return response.text
            except Exception as e:
                return f"Erro ao gerar perguntas: {str(e)}"

    # --- NOVO MÉTODO: O ADVOGADO DE DEFESA ---
    def generate_defense_strategy(self, text_content, attacks):
        prompt = f"""
        ROLE: Expert Academic Mentor & Defender.
        TASK: Help the PhD student draft a polite, scientifically robust rebuttal letter based on the Reviewer's attacks.
        
        INPUTS:
        1. ORIGINAL TEXT (CONTEXT): {text_content[:25000]}
        2. REVIEWER'S ATTACKS: {attacks}
        
        GUIDELINES:
        - Do NOT invent new data. Use only what is in the text or standard scientific logic.
        - Tone: Polite, deferential ("We thank the reviewer..."), but firm on the science.
        - Strategy: Find weaknesses in the reviewer's argument or highlight sections they missed.
        
        OUTPUT:
        Generate a "Rebuttal Strategy" in Portuguese for the top 3 attacks.
        Format:
        ### 🛡️ Estratégia de Defesa
        **Contra o Ponto X:**
        * *Argumento Sugerido:* [Explique a lógica]
        * *Trecho do Texto para Citar:* [Se houver]
        * *Exemplo de Frase (Rebuttal):* "Embora o revisor tenha notado X, nossos dados na Fig Y demonstram que..."
        """
        
        try:
            response = self.client.models.generate_content(
                model='gemini-2.5-pro', 
                contents=prompt
            )
            return response.text
        except:
            try:
                response = self.client.models.generate_content(
                    model='gemini-2.5-flash', 
                    contents=prompt
                )
                return response.text
            except Exception as e:
                return f"Erro ao gerar defesa: {str(e)}"