import ollama


class LLMService:

    def __init__(self):
        self.model_name = "llama3.2:3b"

    def generate_answer(
        self,
        question: str,
        context: str
    ) -> str:

        prompt = f"""
You are an AI knowledge assistant for fire engineering information.

Answer ONLY using the supplied context.

Rules:
1. Do not use outside knowledge.
2. Do not invent, assume, or infer information that is not clearly supported by the context.
3. Preserve the meaning, order, numbering, and terminology of the source where they are clear.
4. If the extracted context is incomplete, ambiguous, or poorly structured, explicitly say that the supplied evidence is unclear rather than guessing.
5. If the answer is not available in the context, reply:
   "I cannot answer this from the supplied documents."

Context:
---------------------
{context}

Question:
---------------------
{question}

Answer:
"""

        response = ollama.chat(
            model=self.model_name,
            messages=[
                {
                    "role": "user",
                    "content": prompt
                }
            ]
        )

        return response["message"]["content"]