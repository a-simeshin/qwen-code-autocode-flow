#!/bin/bash
# Install Qwen Code hooks for Java/React/Python projects
# Usage: curl -fsSL https://raw.githubusercontent.com/a-simeshin/qwen-code-autocode-flow/main/install.sh | bash

set -e

REPO="a-simeshin/qwen-code-autocode-flow"
BRANCH="main"

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
RED='\033[0;31m'
NC='\033[0m'

echo -e "${GREEN}Qwen Code Autocode Flow Installer${NC}"
echo -e "${CYAN}For Java / React / Python projects${NC}"
echo ""

# ─────────────────────────────────────────────────────────────
# Non-interactive mode detection
# ─────────────────────────────────────────────────────────────
if [ "${NONINTERACTIVE:-0}" = "1" ] || [ ! -t 0 ] || [ ! -e /dev/tty ]; then
    INTERACTIVE=false
    echo -e "${YELLOW}Non-interactive mode: using defaults${NC}"
else
    INTERACTIVE=true
fi

# ─────────────────────────────────────────────────────────────
# Check prerequisites
# ─────────────────────────────────────────────────────────────
echo ""
echo -e "${CYAN}Checking prerequisites...${NC}"

MISSING=()

# Check git
if command -v git &> /dev/null; then
    echo -e "  ${GREEN}git: $(git --version | head -1)${NC}"
else
    MISSING+=("git")
    echo -e "  ${RED}git: not found${NC}"
fi

# Check node
if command -v node &> /dev/null; then
    echo -e "  ${GREEN}node: $(node --version)${NC}"
else
    MISSING+=("node")
    echo -e "  ${YELLOW}node: not found (optional, needed for JS/TS validators)${NC}"
fi

# Check and install UV (required for hooks)
if command -v uv &> /dev/null; then
    echo -e "  ${GREEN}uv: $(uv --version)${NC}"
else
    echo -e "${YELLOW}  uv: not found. Installing...${NC}"

    if [[ "$OSTYPE" == "darwin"* ]] && command -v brew &> /dev/null; then
        brew install uv
    else
        curl -LsSf https://astral.sh/uv/install.sh | sh
        export PATH="$HOME/.local/bin:$PATH"
    fi

    if command -v uv &> /dev/null; then
        echo -e "  ${GREEN}uv: installed successfully${NC}"
    else
        MISSING+=("uv")
        echo -e "  ${RED}uv: installation failed. Add ~/.local/bin to PATH and retry${NC}"
    fi
fi

# Report missing critical tools
if [[ " ${MISSING[*]} " =~ " git " ]]; then
    echo ""
    echo -e "${RED}Error: git is required but not found. Please install git and retry.${NC}"
    exit 1
fi

if [[ " ${MISSING[*]} " =~ " uv " ]]; then
    echo ""
    echo -e "${RED}Error: uv is required but could not be installed. See https://docs.astral.sh/uv/${NC}"
    exit 1
fi

echo ""

# ─────────────────────────────────────────────────────────────
# Handle existing .qwen/settings.json
# ─────────────────────────────────────────────────────────────
SETTINGS_FILE=".qwen/settings.json"
MERGE_SETTINGS=false
BACKUP_SETTINGS=""

if [ -f "$SETTINGS_FILE" ]; then
    echo -e "${YELLOW}Existing .qwen/settings.json detected.${NC}"

    if [ "$INTERACTIVE" = true ]; then
        echo "Options:"
        echo "  [k] Keep existing settings.json (skip overwrite)"
        echo "  [b] Backup existing and install new settings.json"
        echo "  [o] Overwrite with new settings.json"
        read -p "Choice [k/b/o] (default: k): " -n 1 -r SETTINGS_CHOICE </dev/tty
        echo
    else
        SETTINGS_CHOICE="k"
        echo -e "${YELLOW}Keeping existing settings.json (non-interactive mode)${NC}"
    fi

    case "$SETTINGS_CHOICE" in
        [Bb])
            BACKUP_SETTINGS="${SETTINGS_FILE}.backup.$(date +%Y%m%d%H%M%S)"
            cp "$SETTINGS_FILE" "$BACKUP_SETTINGS"
            echo -e "${GREEN}Backed up to ${BACKUP_SETTINGS}${NC}"
            ;;
        [Oo])
            echo -e "${YELLOW}Will overwrite settings.json${NC}"
            ;;
        *)
            MERGE_SETTINGS=true
            echo -e "${GREEN}Will keep existing settings.json${NC}"
            ;;
    esac
    echo ""
fi

# ─────────────────────────────────────────────────────────────
# Download and extract
# ─────────────────────────────────────────────────────────────
TMP_DIR=$(mktemp -d)
trap "rm -rf $TMP_DIR" EXIT

echo "Downloading from github.com/${REPO}..."
curl -fsSL "https://github.com/${REPO}/archive/refs/heads/${BRANCH}.tar.gz" | tar -xz -C "$TMP_DIR"

SRC_DIR="$TMP_DIR/qwen-code-autocode-flow-${BRANCH}"

# ─────────────────────────────────────────────────────────────
# Copy .qwen directory contents
# ─────────────────────────────────────────────────────────────
echo "Installing .qwen/ directory..."

# Create target directories
mkdir -p .qwen

# If keeping existing settings, save it temporarily
if [ "$MERGE_SETTINGS" = true ] && [ -f "$SETTINGS_FILE" ]; then
    cp "$SETTINGS_FILE" "$TMP_DIR/settings.json.keep"
fi

# Copy all .qwen contents (hooks, agents, skills, refs, output-styles, settings.json)
if [ -d "$SRC_DIR/.qwen" ]; then
    # Copy subdirectories
    for dir in hooks agents skills refs output-styles; do
        if [ -d "$SRC_DIR/.qwen/$dir" ]; then
            mkdir -p ".qwen/$dir"
            cp -r "$SRC_DIR/.qwen/$dir/." ".qwen/$dir/"
            echo -e "  ${GREEN}Copied .qwen/$dir/${NC}"
        fi
    done

    # Copy settings.json (unless keeping existing)
    if [ "$MERGE_SETTINGS" = true ]; then
        # Restore kept settings
        cp "$TMP_DIR/settings.json.keep" "$SETTINGS_FILE"
        echo -e "  ${GREEN}Kept existing settings.json${NC}"
    elif [ -f "$SRC_DIR/.qwen/settings.json" ]; then
        cp "$SRC_DIR/.qwen/settings.json" "$SETTINGS_FILE"
        echo -e "  ${GREEN}Installed settings.json${NC}"
    fi
else
    echo -e "${RED}Error: .qwen directory not found in downloaded archive${NC}"
    exit 1
fi

# Create specs and logs directories
mkdir -p specs logs

# ─────────────────────────────────────────────────────────────
# Configuration
# ─────────────────────────────────────────────────────────────
echo ""
echo -e "${GREEN}Configuration${NC}"

# TTS Notifications
if [ "$INTERACTIVE" = true ]; then
    read -p "Enable TTS notifications? (requires ElevenLabs/OpenAI) [y/N]: " -n 1 -r TTS_CHOICE </dev/tty
    echo
else
    TTS_CHOICE="${TTS_ENABLED:-n}"
fi

if [[ ! $TTS_CHOICE =~ ^[Yy]$ ]]; then
    # Remove --notify flags if present
    if [ -f "$SETTINGS_FILE" ]; then
        sed -i.bak 's/ --notify//g' "$SETTINGS_FILE" && rm -f "$SETTINGS_FILE.bak"
    fi
    echo "  TTS: disabled"
else
    echo "  TTS: enabled"
fi

echo "  Validators: Java, React/TS, Python (all installed)"
echo ""

# ─────────────────────────────────────────────────────────────
# Summary
# ─────────────────────────────────────────────────────────────
echo -e "${GREEN}Installation complete!${NC}"
echo ""
echo "Installed to .qwen/"
if [ -n "$BACKUP_SETTINGS" ]; then
    echo "Settings backup: $BACKUP_SETTINGS"
fi
echo ""
echo "Run 'qwen' to start Qwen Code."
