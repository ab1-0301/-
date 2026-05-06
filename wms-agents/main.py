#!/usr/bin/env python3
"""WMS Multi-Agent System — C5-AG2 Challenge.

Two cooperating AG2 Beta agents (Coordinator + Inventory) answer
warehouse inventory queries via sub-task delegation.

Run:
    pip install -r requirements.txt
    cp .env.example .env   # fill OPENROUTER_API_KEY
    python main.py
"""
from __future__ import annotations

import asyncio
import os

from dotenv import load_dotenv

from agents.coordinator import create_coordinator

load_dotenv()


def get_config():
    """Create model config from environment."""
    from autogen.beta.config import OpenAIConfig

    model = os.getenv("AG2_DEFAULT_MODEL", "google/gemini-2.5-flash")
    api_key = os.getenv("OPENROUTER_API_KEY", "")
    base_url = os.getenv("OPENAI_BASE_URL", "https://openrouter.ai/api/v1")

    return OpenAIConfig(
        model=model,
        temperature=0.2,
        api_key=api_key,
        base_url=base_url,
    )


async def main() -> None:
    config = get_config()
    coordinator = create_coordinator(config)

    print("=" * 50)
    print("  WMS 多智能体系统 / WMS Multi-Agent System")
    print("  C5-AG2 Challenge — Track: multi-agent")
    print("=" * 50)
    print("Agent: Coordinator <-> Inventory Specialist")
    print("输入 'quit' 退出 / Type 'quit' to exit\n")

    while True:
        try:
            question = input("🧑‍💻 You: ").strip()
        except (EOFError, KeyboardInterrupt):
            print()
            break

        if not question:
            continue
        if question.lower() in ("quit", "exit", "q"):
            break

        print(f"\n🤖 Coordinator 正在处理...")
        try:
            reply = await coordinator.ask(question)
            print(f"\n🤖 Coordinator:\n{reply.body}\n")
        except Exception as e:
            print(f"\n⚠️ Error: {e}\n")

    print("👋 再见！")


if __name__ == "__main__":
    asyncio.run(main())
