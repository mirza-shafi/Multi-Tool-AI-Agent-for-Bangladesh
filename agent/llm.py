"""LLM provider selection: Google Gemini (default) or Groq, both free-tier."""

import os


def get_llm():
    provider = os.getenv("LLM_PROVIDER", "gemini").lower()

    if provider == "groq":
        from langchain_groq import ChatGroq

        return ChatGroq(
            model=os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile"),
            temperature=0,
        )

    from langchain_google_genai import ChatGoogleGenerativeAI

    return ChatGoogleGenerativeAI(
        model=os.getenv("GEMINI_MODEL", "gemini-2.0-flash"),
        temperature=0,
    )
