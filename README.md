# Jellyfish World 🪼

A calm, cosmetic-driven terminal world where each user owns exactly one AI jellyfish that floats in their terminal and answers when called.

---

## 🌊 Quick Start: Launch the Interactive Companion

To start your companion right now:

```powershell
cd C:\Users\rohan\.gemini\antigravity\scratch\jellyfish_world
.\jellyfish.cmd
```
*(Or double-click [start.bat](file:///C:/Users/rohan/.gemini/antigravity/scratch/jellyfish_world/start.bat) in Windows Explorer)*

### Features Inside the Companion:
- **💬 Chat**: Type `1` or directly type `hey jellyfish <message>` to chat in character.
- **🔭 Watch Other Agents**: Type `2` to view real-time activity from **Claude Code, OpenCode, Codex, Hermes, and DeepSeek** reporting via MCP.
- **🎯 Work Options**: Type `3` to get calm, gentle recommendations for your current workspace.
- **✨ Feed Light**: Type `4` for your daily tap.
- **🪟 Dock to Sidepane**: Type `5` to open a floating sidepane in Windows Terminal.

---

## 🤖 Universal Agent Bridge (MCP)

Jellyfish World exposes an MCP server over stdio, connecting with any coding assistant:

```powershell
# Check which agents are detected on your machine
python src/cli/jelly.py connect status

# Connect all agents with one command
python src/cli/jelly.py connect all
```

---

## 🚀 Windows Terminal Autostart & Fast Greeting

```powershell
# Check autostart status
python src/cli/jelly.py autostart status

# Enable autostart
python src/cli/jelly.py autostart on
```

---

## 🧪 Test Suite

Run all automated unit tests:
```powershell
cd scratch/jellyfish_world
.\venv\Scripts\python.exe -m pytest tests
```
