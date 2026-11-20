# Jellyfish World 🪼

A calm, cosmetic-driven terminal world where each user owns exactly one AI jellyfish that floats in their terminal and answers when called.

---

## 🌊 Direct Commands

You can speak to your jellyfish directly from any directory:

```powershell
# Chat with your jellyfish instantly
jellyfish how are you doing?
jellyfish hello
jellyfish I am working on a tough bug
```

To launch the full interactive companion dashboard:
```powershell
jellyfish
```

### Features Inside the Companion:
- **💬 Chat**: Type `1` or type directly to chat in character.
- **🔭 Watch Other Agents**: Type `2` to view real-time activity from **Claude Code, OpenCode, Codex, Hermes, and DeepSeek** reporting via MCP.
- **🎯 Work Options**: Type `3` to get calm, gentle recommendations for your current workspace.
- **✨ Feed Light**: Type `4` for your daily tap.
- **🪟 Dock to Sidepane**: Type `5` to open a floating sidepane in Windows Terminal.

---

## 🤖 Universal Agent Bridge (MCP)

Jellyfish World exposes an MCP server over stdio, connecting with any coding assistant:

```powershell
# Check which agents are detected on your machine
jelly connect status

# Connect all agents with one command
jelly connect all
```

---

## 🚀 Windows Terminal Autostart & Fast Greeting

```powershell
# Check autostart status
jelly autostart status

# Enable autostart
jelly autostart on
```

---

## 🪼 Continuous Drift Mode (24/7 Display)

Run your jellyfish continuously below the line while working:

```powershell
# Run indefinitely (perfect for agent work)
jelly drift

# With custom interval
jelly drift --interval 0.3

# Force compact 40x20 viewport
jelly drift --compact
```

The `--silent` mode in `jelly home` also works for non-interactive display:

```powershell
jelly home --silent
```

---

## 🧪 Test Suite

Run all automated unit tests:
```powershell
cd scratch/jellyfish_world
.\venv\Scripts\python.exe -m pytest tests
```
