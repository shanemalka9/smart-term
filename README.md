# SmartTerm: Context-Aware Zsh Autosuggestions

SmartTerm is a lightweight, AI-assisted autosuggestion tool for the Zsh shell. Unlike standard autocomplete, it uses a background Python daemon to analyze your command history **and** your current directory context to provide "smart" suggestions.

It features a hybrid architecture that runs entirely locally, ensuring zero latency and full privacy.

## 🚀 Features

* **Hybrid Intelligence:**
    * **Frequency-Based:** Remembers your most used commands (via SQLite).
    * **Context-Aware:** Detects specific scenarios (e.g., if a folder is empty, it suggests `git clone`).
* **Smart Cleanup:** Automatically deletes "one-time use" commands (like specific `git clone` URLs) after 24 hours to keep your history clean.
* **Zero Clutter:** Runs in an isolated Python Virtual Environment (`venv`).
* **Ghost Text UI:** Displays suggestions in gray text (like VS Code or Fish shell); press `Tab` to accept.

## 📋 Prerequisites

Before installing, ensure you have the following:

* **OS:** macOS or Linux
* **Shell:** Zsh
* **Python:** Version 3.x
* **System Packages:** `jq` (Required for JSON processing in the shell)
    * *Mac:* `brew install jq`
    * *Ubuntu/Debian:* `sudo apt install jq`
    * *Fedora:* `sudo dnf install jq`

## 📦 Installation

1.  **Clone the Repository**
    ```bash
    git clone [https://github.com/yourusername/smart-term.git](https://github.com/yourusername/smart-term.git)
    cd smart-term
    ```

2.  **Set up the Environment**
    Run the following commands to create an isolated Python environment and install dependencies. This keeps your global system clean.
    ```bash
    # Create virtual environment
    python3 -m venv venv

    # Activate it
    source venv/bin/activate

    # Install dependencies
    pip install -r requirements.txt
    ```

## 🚦 Usage

SmartTerm consists of two parts: the **Daemon** (Background Service) and the **Interface** (Zsh Hook). Both must be active.

### 1. Start the Daemon
The daemon must be running to process suggestions. Run this in a **separate terminal tab** (or keep it in the background):

```bash
# Ensure you are in the project folder and venv is active
python daemon.py

```

### 2. Activate the Interface

In your **main terminal window** (where you want the suggestions), load the Zsh hook:

```bash
# Replace with your actual path
source ~/smart-term/hook.zsh

```

### 3. Verify it Works

1. **Train:** Type `git commit -m "initial commit"` and hit **Enter**.
2. **Predict:** Type `git c`.
3. **Result:** You should see `ommit -m "initial commit"` appear in gray. Press **Tab** to accept it.

---

## ⚙️ Auto-Start (Recommended)

To avoid running these commands manually every time, add the following to your `.zshrc` file. This script will automatically start the background daemon if it isn't running.

**1. Open your config:**

```bash
nano ~/.zshrc

```

**2. Add this snippet to the bottom:**
*Make sure to replace `$HOME/smart-term` with the actual path where you cloned the repo if different.*

```bash
# --- SmartTerm Auto-Start ---
SMART_TERM_DIR="$HOME/smart-term"

# Start Daemon silently if not running
if ! pgrep -f "python.*daemon.py" > /dev/null; then
   (cd "$SMART_TERM_DIR" && source venv/bin/activate && python daemon.py > /dev/null 2>&1 &)
fi

# Load the hook
source "$SMART_TERM_DIR/hook.zsh"
# ----------------------------

```

**3. Apply changes:**

```bash
source ~/.zshrc

```

## 🧠 How the Logic Works

The `predict()` function in `daemon.py` follows this priority:

1. **Context Check (Priority 1):**
* If the current directory is **empty** and you type `g` or `gi`, it assumes you want to start a project and suggests `git clone`.


2. **History Check (Priority 2):**
* It looks up your history database (`history.db`).
* It finds the command that matches your current input and has the **highest usage count**.


3. **Cleanup (Automatic):**
* On startup, the daemon deletes commands that have a `usage_count` of 1 and are older than 24 hours.



## 🗑️ Uninstall

To remove SmartTerm:

1. Remove the "Auto-Start" snippet from your `~/.zshrc`.
2. Kill the daemon process: `pkill -f daemon.py`
3. Delete the cloned repository folder.
