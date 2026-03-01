# 🦾 Super Hands OS

Super Hands OS is a fully autonomous, self-correcting AI agent operating system. Unlike standard chatbots, it features a recursive "Plan-Act-Verify" loop, a high-speed WebSocket streaming connection, and an isolated Docker sandbox to execute terminal commands safely.



## 🏗️ Architecture Overview

The system is split into three main components:
1. **The Brain (Backend):** A Python/FastAPI server connected to the Gemini API. It handles the logic, loop execution, and WebSocket streaming.
2. **The Hands (Sandbox):** An isolated, ephemeral Ubuntu Docker container where the AI safely executes terminal commands without risking your main server.
3. **The Command Center (Frontend):** A Next.js application providing a split-pane view with a chat interface and a live streaming terminal window.

---

## 🚀 End-to-End Installation Guide (VPS Deployment)

This guide is designed for deploying Super Hands OS on a Linux VPS (like Hostinger, DigitalOcean, etc.) directly from this GitHub repository.

### Prerequisites
* A Linux VPS running Ubuntu (20.04 or 22.04 recommended).
* Root or `sudo` access to the VPS.
* A Gemini API Key from Google AI Studio.

### Step 1: Clone the Repository to Your Server
SSH into your VPS and clone your repository. Replace `YOUR_GITHUB_URL` with your actual repository link.

```bash
# SSH into your server
ssh root@your_vps_ip_address

# Clone the code
git clone YOUR_GITHUB_URL super-hands-os
cd super-hands-os
