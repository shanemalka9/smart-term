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

## 🛠️ Architecture

The tool consists of two parts working in tandem:

1.  **The Brain (`daemon.py`):** A lightweight Flask server running in the background. It manages the SQLite database, handles the logic for suggestions, and performs cleanup tasks.
2.  **The Interface (`hook.zsh`):** A Zsh script that captures keystrokes, queries the Brain, and renders the "ghost text" overlay using ZLE (Zsh Line Editor) widgets.

## 📋 Prerequisites

* **OS:** macOS or Linux
* **Shell:** Zsh
* **Dependencies:**
    * Python 3
    * `jq` (Command-line JSON processor)
        * *Mac:* `brew install jq`
        * *Ubuntu/Debian:* `sudo apt install jq`

## 📦 Installation

This project is designed to be self-contained.

1.  **Create the Project Directory:**
    ```bash
    cd ~/smart-term
    ```

2.  **Set up the Isolated Python Environment:**
    ```bash
    python3 -m venv venv
    source venv/bin/activate
    ```

3.  **Install Python Dependencies:**
    Create a `requirements.txt` with the following content:
    ```text
    flask
    ```
    Then run:
    ```bash
    pip install -r requirements.txt
    ```

4.  **Create the Source Files:**
    * Create `daemon.py` (The Python Logic).
    * Create `hook.zsh` (The Shell Interface).
    *(Refer to the setup guide or source code for the contents of these files)*.

## 🚦 Usage

### 1. Start the Daemon
The Python script must be running to process suggestions. Open a terminal tab and run:

```bash
cd ~/smart-term
source venv/bin/activate
python daemon.py