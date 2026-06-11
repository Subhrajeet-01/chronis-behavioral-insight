# Chronis Behavioral Insight Engine

The Chronis Behavioral Insight Engine is a long-horizon behavioral analysis system designed to analyze personal metric logs (steps, sleep, screen time, deep work focus, and physical exercise) and generate actionable, evidence-backed insights. 

Built with privacy and precision in mind, the engine isolates profiles, identifies multi-variable correlations, and employs a mathematical **Abstention Engine** to shield users from noisy, false, or premature claims.

---

## Key Features

1. **Pattern Discovery (Component 1)**: Computes Cohen's d effect sizes for weekly trend shifts, Pearson correlation ($r$) for cross-metric associations, and Coefficient of Variation ($CV$) for sleep routine consistency.
2. **Anomaly Detection (Component 2)**: Detects rolling Z-score outliers ($|Z| \ge 2.0$) and compound behavioral distress events (such as "Digital Burnout" where high screen time and low sleep occur simultaneously).
3. **Insight Generation (Component 3)**: Generates human-readable, evidence-backed claims paired with dynamic confidence ratings.
4. **Evidence Sufficiency Protocol (Component 4)**: Automatically suppresses candidate insights that fall below a 70% confidence threshold ($C < 0.70$) to prevent false conclusions.
5. **Interactive Dashboard**: Generates a premium dark OLED-themed dashboard containing user profiles, metrics stats, and Chart.js correlation timelines.

---

## Technology Stack

* **Language**: Python 3.10+
* **Data Processing**: Pandas, NumPy
* **Templating Engine**: Jinja2
* **Testing**: Pytest
* **Visualization (Dashboard)**: Vanilla HTML5, CSS3, Chart.js

---

## Directory Structure

```text
chronis/
├── engine/
│   ├── __init__.py
│   ├── anomaly_detection.py  # Outliers and compound events
│   ├── parser.py             # Data loading and cleaning
│   ├── pattern_discovery.py  # Cohen's d, CV, and correlations
│   ├── insight_generator.py  # Sufficiency shielding and synthesis
│   ├── reporter.py           # CLI summaries and HTML dashboard rendering
│   └── report_template.html  # Premium dark OLED HTML template
├── tests/
│   ├── test_parser.py
│   ├── test_anomaly_detection.py
│   ├── test_pattern_discovery.py
│   └── test_insight_generator.py
├── main.py                   # Main pipeline CLI entry point
├── run.sh                    # Single-command workflow script
├── decisions.md              # Mathematical methodology & failure modes
├── requirements.txt          # Project dependencies
└── .gitignore
```

---

## Getting Started

### Prerequisites
Ensure you have Python 3.10+ installed on your system.

---

### Executing the Workflow (Single-Command)

#### On Linux & macOS:
```bash
# Grant execution permission to the script
chmod +x run.sh

# Execute the workflow
./run.sh
```

#### On Windows (using Git Bash or WSL):
```bash
# Execute the workflow using bash
bash run.sh
```

#### On Windows (using PowerShell):
```powershell
# Create virtual environment
python -m venv .venv

# Activate virtual environment
.venv\Scripts\Activate.ps1

# Install requirements
pip install -r requirements.txt

# Run the test suite
python -m pytest tests/ -v

# Run the pipeline
python main.py --data "Chronis_TaskA_Synthetic_Behavioral_Data_v2-2 (1).csv"
```

#### On Windows (using Command Prompt):
```cmd
:: Create virtual environment
python -m venv .venv

:: Activate virtual environment
.venv\Scripts\activate.bat

:: Install requirements
pip install -r requirements.txt

:: Run the test suite
python -m pytest tests/ -v

:: Run the pipeline
python main.py --data "Chronis_TaskA_Synthetic_Behavioral_Data_v2-2 (1).csv"
```

---

## Pipeline Outputs

Upon a successful run, the engine outputs two summary files in the root workspace directory:
* **`chronis_report.json`**: Machine-readable JSON output containing parsed profiles, verified patterns, detected anomalies, and withheld statistics.
* **`chronis_report.html`**: A premium, interactive dashboard showcasing behavioral correlations and dynamic timeline graphs for each profile.

### How to Open the HTML Dashboard

You can open the generated `chronis_report.html` dashboard directly using a terminal command or by using your file browser:

#### Using Command Line:
*   **Linux**:
    ```bash
    xdg-open chronis_report.html
    ```
*   **macOS**:
    ```bash
    open chronis_report.html
    ```
*   **Windows**:
    ```cmd
    start chronis_report.html
    ```

#### Using Graphical Interface (All Platforms):
*   Double-click the file `chronis_report.html` inside your file browser (Explorer/Finder/Files).
*   Alternatively, drag and drop the `chronis_report.html` file into any open web browser (Chrome, Firefox, Safari, Edge).
