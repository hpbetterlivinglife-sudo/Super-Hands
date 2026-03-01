#!/bin/bash

echo "🚀 Starting Super Hands OS Setup..."

# 1. Update system and install base dependencies
echo "📦 Updating system packages..."
sudo apt update && sudo apt upgrade -y
sudo apt install -y curl git python3 python3-pip python3-venv build-essential

# 2. Install Docker (for the AI Sandbox)
if ! command -v docker &> /dev/null; then
    echo "🐳 Installing Docker..."
    curl -fsSL https://get.docker.com -o get-docker.sh
    sudo sh get-docker.sh
    sudo usermod -aG docker $USER
    rm get-docker.sh
else
    echo "✅ Docker is already installed."
fi

# 3. Install Node.js (for the Next.js UI)
if ! command -v node &> /dev/null; then
    echo "🟢 Installing Node.js (v20)..."
    curl -fsSL https://deb.nodesource.com/setup_20.x | sudo -E bash -
    sudo apt-get install -y nodejs
else
    echo "✅ Node.js is already installed."
fi

# 4. Install PM2 (to keep apps running in the background forever)
echo "⚙️ Installing PM2..."
sudo npm install -g pm2

# 5. Create the OS folder structure
echo "📁 Building directory structure..."
cd ~
mkdir -p super_hands_os/agent
mkdir -p super_hands_os/tools
mkdir -p super_hands_os/agent_workspace

echo ""
echo "===================================================="
echo "✅ SUPER HANDS OS ENVIRONMENT PREPARED SUCCESSFULLY!"
echo "===================================================="
echo ""
echo "NEXT STEPS:"
echo "1. Put your Python files into the ~/super_hands_os folder."
echo "2. Put your Next.js files into a ~/super-hands-ui folder."
echo "3. Run this command to start your Python backend:"
echo "   cd ~/super_hands_os && python3 -m venv venv && source venv/bin/activate && pip install fastapi uvicorn google-genai pydantic docker && pm2 start 'uvicorn main:app --host 0.0.0.0 --port 8000' --name super-hands-backend"
echo ""
echo "4. Run this command to start your Frontend UI:"
echo "   cd ~/super-hands-ui && npm install && npm run build && pm2 start npm --name super-hands-frontend -- start"
echo "===================================================="
