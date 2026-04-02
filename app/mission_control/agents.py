from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class Agent:
    name: str
    purpose: str

    def run(self, idea: str, scope: str) -> str:
        return f"[{self.name}] entregable inicial para '{idea}' con scope '{scope}'."


DEFAULT_AGENTS: dict[str, Agent] = {
    "product": Agent("product", "Define visión, roadmap y backlog"),
    "legal": Agent("legal", "Gestiona cumplimiento, privacidad y contratos"),
    "marketing": Agent("marketing", "Diseña posicionamiento y GTM"),
    "design": Agent("design", "Diseña UX, flujos y sistema visual"),
    "development": Agent("development", "Construye arquitectura y features"),
    "qa": Agent("qa", "Define estrategia de pruebas y calidad"),
}
