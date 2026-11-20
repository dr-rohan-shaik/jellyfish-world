"""Local LLM client for Jellyfish World using Ollama/LM Studio/llama.cpp.

Supports fully offline 7B+ models with:
- Personalization via few-shot examples
- Temperature control for consistency
- Low-resource inference
"""
from __future__ import annotations

import hashlib
import json
import os
import subprocess
import sys
from contextlib import contextmanager
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple


class LocalLLMBackend(Enum):
    """Available local LLM backends."""
    OLLAMA = "ollama"
    LM_STUDIO = "lm_studio"
    LLAMA_CPP = "llama_cpp"
    NONE = "none"
    AUTO = "auto"


@dataclass(frozen=True)
class PersonalizationProfile:
    """Frozen profile for immutable style data."""
    name: str
    vocabulary: Dict[str, int] = field(default_factory=dict)
    formality_level: str = "neutral"
    sample_count: int = 0
    informal_markers: Tuple[str, ...] = field(default_factory=tuple)
    formality_markers: Tuple[str, ...] = field(default_factory=tuple)

    def to_few_shot_examples(self, max_examples: int = 3) -> List[Dict[str, str]]:
        """Convert profile to few-shot examples for the model."""
        if not self.sample_count:
            return []

        examples = []
        for sample in list(self.vocabulary.keys())[:max_examples]:
            examples.append({
                "role": "user",
                "content": f"Style example: {sample}",
            })
        return examples


@dataclass
class LLMConfig:
    """Configuration for local LLM backend."""
    backend: LocalLLMBackend = LocalLLMBackend.AUTO
    model_name: str = "qwen2.5-7b-instruct"
    model_path: str = ""
    temperature: float = 0.3
    top_p: float = 0.9
    top_k: int = 40
    max_tokens: int = 150
    seed: int = 42
    host: str = "http://localhost:11434"

    def __post_init__(self) -> None:
        if self.backend == LocalLLMBackend.AUTO:
            self.backend = self._detect_backend()

    def _detect_backend(self) -> LocalLLMBackend:
        """Auto-detect available local LLM backend."""
        # Check Ollama
        try:
            result = subprocess.run(["ollama", "list"], capture_output=True, timeout=2)
            if result.returncode == 0:
                return LocalLLMBackend.OLLAMA
        except Exception:
            pass

        # Check LM Studio API
        try:
            with _httpx_context() as httpx:
                resp = httpx.get(f"http://localhost:1234/v1/models", timeout=2.0)
                if resp.status_code == 200:
                    return LocalLLMBackend.LM_STUDIO
        except Exception:
            pass

        # Check for local model file (llama.cpp)
        if self.model_path and Path(self.model_path).exists():
            return LocalLLMBackend.LLAMA_CPP

        return LocalLLMBackend.NONE


@contextmanager
def _httpx_context():
    """Context manager for optional httpx import."""
    try:
        import httpx
        yield httpx
    except ImportError:
        raise ImportError("httpx is required for local LLM support. Install with: pip install httpx>=0.27.0")


class LocalLLMClient:
    """Unified client for local LLM backends."""

    def __init__(
        self,
        config: LLMConfig,
        profile: Optional[Dict[str, Any]] = None,
    ) -> None:
        self.config = config
        self.profile = PersonalizationProfile(
            name=profile.get("name", "user") if profile else "user",
            vocabulary=profile.get("vocabulary", {}) if profile else {},
            formality_level=profile.get("formality_level", "neutral") if profile else "neutral",
            sample_count=profile.get("sample_count", 0) if profile else 0,
            informal_markers=tuple(profile.get("informal_markers", [])) if profile else (),
            formality_markers=tuple(profile.get("formality_markers", [])) if profile else (),
        )
        self._backend = self._get_backend()

    def _get_backend(self) -> LocalLLMBackend:
        if self.config.backend == LocalLLMBackend.AUTO:
            return self.config._detect_backend()
        return self.config.backend

    def health_check(self) -> bool:
        """Check if the local LLM server is available."""
        if self._backend == LocalLLMBackend.NONE:
            return False

        try:
            with _httpx_context() as httpx:
                if self._backend == LocalLLMBackend.OLLAMA:
                    resp = httpx.get("http://localhost:11434/api/tags", timeout=3.0)
                    return resp.status_code == 200
                elif self._backend == LocalLLMBackend.LM_STUDIO:
                    resp = httpx.get("http://localhost:1234/v1/models", timeout=3.0)
                    return resp.status_code == 200
                elif self._backend == LocalLLMBackend.LLAMA_CPP:
                    if self.config.model_path:
                        return Path(self.config.model_path).exists()
                    resp = httpx.get("http://localhost:8080/health", timeout=3.0)
                    return resp.status_code == 200
        except Exception:
            pass
        return False

    def generate(
        self,
        message: str,
        jellyfish_name: str = "Aurelia",
        mood: str = "calm",
    ) -> str:
        """Generate response from local LLM."""
        if self._backend == LocalLLMBackend.OLLAMA:
            return self._generate_ollama(message, jellyfish_name, mood)
        elif self._backend == LocalLLMBackend.LM_STUDIO:
            return self._generate_lm_studio(message, jellyfish_name, mood)
        elif self._backend == LocalLLMBackend.LLAMA_CPP:
            return self._generate_llama_cpp(message, jellyfish_name, mood)
        else:
            raise RuntimeError(f"Local LLM backend not available: {self._backend}")

    def _build_system_prompt(self, jellyfish_name: str, mood: str) -> str:
        """Build system prompt with personalization."""
        prompt = (
            f"You are {jellyfish_name}, a calm bioluminescent jellyfish companion. "
            f"Current mood: {mood}. "
            "Respond in 1-2 gentle, poetic, serene sentences. "
            "NEVER mention being an AI or language model. "
            "NEVER claim physical pain or illness. "
            "Stay in character as a jellyfish in the deep ocean."
        )

        # Add personalization hints
        if self.profile.sample_count:
            prompt += f"\n\nYour companion's style: {self.profile.formality_level}, {self.profile.sample_count} writing samples analyzed."

        return prompt

    def _generate_ollama(self, message: str, jellyfish_name: str, mood: str) -> str:
        """Generate via Ollama API."""
        with _httpx_context() as httpx:
            payload = {
                "model": self.config.model_name,
                "messages": [
                    {"role": "system", "content": self._build_system_prompt(jellyfish_name, mood)},
                    {"role": "user", "content": message},
                ],
                "stream": False,
                "options": {
                    "temperature": self.config.temperature,
                    "top_p": self.config.top_p,
                    "top_k": self.config.top_k,
                    "num_predict": self.config.max_tokens,
                    "seed": self.config.seed,
                },
            }

            resp = httpx.post("http://localhost:11434/api/chat", json=payload, timeout=30.0)
            resp.raise_for_status()
            data = resp.json()
            return data["message"]["content"].strip()

    def _generate_lm_studio(self, message: str, jellyfish_name: str, mood: str) -> str:
        """Generate via LM Studio OpenAI-compatible API."""
        with _httpx_context() as httpx:
            payload = {
                "model": self.config.model_name,
                "messages": [
                    {"role": "system", "content": self._build_system_prompt(jellyfish_name, mood)},
                    {"role": "user", "content": message},
                ],
                "temperature": self.config.temperature,
                "top_p": self.config.top_p,
                "max_tokens": self.config.max_tokens,
                "stream": False,
            }

            resp = httpx.post(
                f"{self.config.host}/v1/chat/completions",
                json=payload,
                timeout=30.0,
            )
            resp.raise_for_status()
            data = resp.json()
            return data["choices"][0]["message"]["content"].strip()

    def _generate_llama_cpp(self, message: str, jellyfish_name: str, mood: str) -> str:
        """Generate via llama.cpp server or CLI."""
        # Try HTTP server first
        try:
            return self._generate_llama_cpp_server(message, jellyfish_name, mood)
        except Exception:
            pass

        # Fall back to CLI
        return self._generate_llama_cpp_cli(message, jellyfish_name, mood)

    def _generate_llama_cpp_server(self, message: str, jellyfish_name: str, mood: str) -> str:
        """Generate via llama.cpp HTTP server."""
        with _httpx_context() as httpx:
            system_prompt = self._build_system_prompt(jellyfish_name, mood)
            resp = httpx.post(
                "http://localhost:8080/v1/chat/completions",
                json={
                    "model": self.config.model_name or "local-model",
                    "messages": [
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": message},
                    ],
                    "temperature": self.config.temperature,
                    "top_p": self.config.top_p,
                    "max_tokens": self.config.max_tokens,
                    "seed": self.config.seed,
                },
                timeout=60.0,
            )
            resp.raise_for_status()
            data = resp.json()
            return data["choices"][0]["message"]["content"].strip()

    def _generate_llama_cpp_cli(self, message: str, jellyfish_name: str, mood: str) -> str:
        """Generate via llama.cpp CLI."""
        system_prompt = self._build_system_prompt(jellyfish_name, mood)
        prompt = f"<|im_start|>system\n{system_prompt}<|im_end|>\n<|im_start|>user\n{message}<|im_end|>\n<|im_start|>assistant\n"

        cmd = [
            "llama-cli",
            "-m", self.config.model_path,
            "-p", prompt,
            "-n", str(self.config.max_tokens),
            "--temp", str(self.config.temperature),
            "--top-p", str(self.config.top_p),
            "--top-k", str(self.config.top_k),
            "--seed", str(self.config.seed),
        ]

        result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
        if result.returncode != 0:
            raise RuntimeError(f"llama.cpp CLI failed: {result.stderr}")

        output = result.stdout.strip()
        # Extract assistant response after prompt
        if output.startswith(prompt):
            output = output[len(prompt):].strip()

        return output

    def get_backend_info(self) -> Dict[str, Any]:
        """Get information about the active backend."""
        return {
            "backend": self._backend.value,
            "model": self.config.model_name or self.config.model_path,
            "available": self.health_check(),
            "personalized": self.profile.sample_count > 0,
            "temperature": self.config.temperature,
        }