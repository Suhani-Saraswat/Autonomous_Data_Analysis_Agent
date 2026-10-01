# Autonomous Data Analysis Agent

An end-to-end web application that turns raw tabular data into **automated analysis, visualizations, evidence-grounded insights, and printable reports**.

The system is designed for users who want to upload a CSV/Excel dataset, ask a natural-language analytical question, and let the application determine the appropriate analysis workflow instead of manually writing pandas code.

> **Project type:** AI/Agentic Data Analysis + Full-Stack Web Application  
> **Frontend:** React + Vite  
> **Backend:** FastAPI + Python  
> **Data layer:** Pandas + NumPy  
> **Workflow orchestration:** LangGraph StateGraph  
> **Reporting:** ReportLab PDF  

---

## Features

### Dataset management

- Load the included fixed Superstore benchmark dataset.
- Load the included live/refreshable Superstore dataset.
- Upload `.csv`, `.xlsx`, and `.xls` files.
- Automatically validate uploaded datasets.
- Preview dataset rows before analysis.
- Profile rows, columns, data types, missing values, unique values, and duplicate rows.

### Autonomous analysis

The user only needs to ask a question such as:

```text
Break down total sales and profit margins across regions.
```

The system determines the required analytical operations and executes them through the workflow.

Supported analysis patterns include:

- Regional comparisons
- Category analysis
- Segment analysis
- Sales/profit analysis
- Profit margin calculations
- Discount analysis
- Time/trend analysis
- Correlation/relationship analysis
- Outlier detection
- General dataset overview questions

### Workflow transparency

The backend uses a StateGraph-based execution pipeline. The web interface exposes the execution process using neutral, user-facing terminology so that a technical reviewer can inspect how the analysis was produced without requiring the UI to advertise a framework name.

The execution flow is:

```text
Dataset Input
      ↓
Planner
      ↓
Analysis Builder
      ↓
Execution
      ↓
Self-Correct
      ↓
Synthesis
      ↓
Charts + Metrics + Insights + Report
```

The technical workflow panel can expose:

- Execution graph
- Event stream
- State information
- Generated analysis recipe
- Selected analysis plan
- Node inputs and outputs
- Validation status

### Visual analytics

- Interactive result views
- Bar charts
- Line/trend charts
- Scatter/correlation charts
- Outlier visualizations
- Metric cards
- Executive summary

### Reporting

- Human-readable text report
- PDF report
- Browser-friendly printable summary
- Executive summary
- Data-quality section
- Analytical plan
- Key metrics
- Evidence-based insights

### UI

- Dark mode
- Enhanced light mode
- Responsive dashboard
- Dataset source panel
- Analysis query panel
- Workflow/execution panel
- Result tabs
- Upload controls
- Live dataset refresh

---

## Architecture

```text
                         ┌──────────────────────┐
                         │       React UI       │
                         │      + Vite          │
                         └──────────┬───────────┘
                                    │ REST API
                                    ▼
                         ┌──────────────────────┐
                         │       FastAPI        │
                         └──────────┬───────────┘
                                    │
                                    ▼
                    ┌──────────────────────────────┐
                    │   Analysis Orchestrator      │
                    │       StateGraph             │
                    └──────────────┬───────────────┘
                                   │
          ┌────────────────────────┼────────────────────────┐
          ▼                        ▼                        ▼
      Planner                Analysis Builder          Execution
          │                        │                        │
          └────────────────────────┼────────────────────────┘
                                   ▼
                              Self-Correct
                                   │
                                   ▼
                               Synthesis
                                   │
                  ┌────────────────┼────────────────┐
                  ▼                ▼                ▼
               Metrics          Charts           Insights
                  │                │                │
                  └────────────────┼────────────────┘
                                   ▼
                              PDF / Print
```

---

## Workflow Details

### 1. Dataset Input

The selected dataset is loaded with Pandas and profiled before analysis begins.

### 2. Planner

The planner interprets the user's natural-language question and selects analytical operations based on the available dataset columns.

### 3. Analysis Builder

A transparent analysis recipe is generated from the selected plan. The recipe documents the intended operations without executing arbitrary user-generated code.

### 4. Execution

The trusted analysis engine performs the required computations and prepares chart-ready data.

### 5. Self-Correct

Computed metrics are validated. If invalid scalar results are detected, the deterministic analysis engine is re-run and validation is performed again.

### 6. Synthesis

The validated metrics and chart evidence are converted into concise, evidence-grounded insights and an executive summary.

### 7. Reporting

The same analysis result can be exported as text or PDF and can also be printed directly from the browser.

---

## Project Structure

```text
autonomous-data-analysis-agent/
│
├── backend/
│   ├── app.py                  # FastAPI routes and report generation
│   ├── functions.py            # Profiling, planning, execution, validation
│   ├── model.py                # Data/model utilities
│   ├── orchestrator.py         # StateGraph analysis workflow
│   ├── schema.py               # API request schemas
│   ├── templates/              # Backend template assets
│   └── static/                 # Backend static assets
│
├── frontend/
│   ├── src/
│   │   ├── App.jsx
│   │   ├── styles.css
│   │   ├── components/
│   │   │   ├── Header.jsx
│   │   │   ├── DatasetCard.jsx
│   │   │   ├── AgentPipeline.jsx
│   │   │   ├── QueryPanel.jsx
│   │   │   ├── ResultsPanel.jsx
│   │   │   └── ProfileTable.jsx
│   │   └── services/
│   │       └── api.js
│   ├── package.json
│   ├── vite.config.js
│   └── index.html
│
├── datasets/
│   ├── superstore_fixed_benchmark_10000plus.csv
│   ├── superstore_fixed_benchmark.xlsx
│   ├── superstore_live_stream_10000plus.csv
│   ├── superstore_live_stream.xlsx
│   ├── generate_live_batch.py
│   └── DATASET_README.csv
│
├── tests/
│   ├── __init__.py
│   └── test_api.py             # Pytest API tests
│
├── helper.py
├── main.py
├── test.py                     # Project-level automated test runner
├── requirement.txt
├── .env.example
├── .gitignore
└── README.md
```

---

## Requirements

### Backend

- Python 3.10+
- FastAPI
- Uvicorn
- Pandas
- NumPy
- OpenPyXL
- Pydantic
- LangGraph
- ReportLab
- Pytest
- HTTPX

### Frontend

- Node.js 18+
- npm
- React
- Vite

---

## Installation

### 1. Clone the repository

```bash
git clone https://github.com/YOUR_USERNAME/autonomous-data-analysis-agent.git
cd autonomous-data-analysis-agent
```

Replace `YOUR_USERNAME` with your GitHub username and use the actual repository URL after publishing the project.

### 2. Create a Python virtual environment

Windows:

```bash
python -m venv .venv
.venv\Scripts\activate
```

macOS/Linux:

```bash
python3 -m venv .venv
source .venv/bin/activate
```

### 3. Install backend dependencies

```bash
pip install -r requirement.txt
```

### 4. Install frontend dependencies

```bash
cd frontend
npm install
cd ..
```

---

## Running the Application

### Start the backend

From the project root:

```bash
uvicorn backend.app:app --reload --host 127.0.0.1 --port 8000
```

Backend:

```text
http://127.0.0.1:8000
```

### Start the frontend

Open another terminal:

```bash
cd frontend
npm run dev
```

Frontend:

```text
http://localhost:5173
```

The Vite development server proxies `/api` requests to the FastAPI server on port `8000`.

---

## How to Use

1. Start the backend.
2. Start the frontend.
3. Open `http://localhost:5173`.
4. Select the fixed or live dataset.
5. Optionally upload your own CSV/Excel dataset.
6. Enter a natural-language analytical question.
7. Click **Analyze**.
8. Inspect the generated metrics, charts, insights, and workflow.
9. Open the technical execution views if you want to inspect the analysis process.
10. Export the result as PDF or print the summary.

### Example queries

```text
Break down total sales and profit margins across regions.
```

```text
Which categories generate the highest profit?
```

```text
Show sales trends over time.
```

```text
Find unusual sales and quantity values.
```

```text
Analyze the relationship between discount and sales.
```

```text
Compare customer segments by profit.
```

---

## API Endpoints

| Method | Endpoint | Purpose |
|---|---|---|
| GET | `/api/health` | Backend/runtime health check |
| GET | `/api/datasets` | List available datasets |
| GET | `/api/profile` | Generate dataset profile |
| GET | `/api/preview` | Preview dataset rows |
| POST | `/api/analyze` | Run autonomous analysis |
| POST | `/api/upload` | Upload and validate dataset |
| POST | `/api/live/refresh` | Refresh the live dataset |
| POST | `/api/report` | Generate text report |
| POST | `/api/report/pdf` | Generate printable PDF report |

---

## Testing

The repository contains both a simple project-level test runner and a Pytest suite.

### Run the project test runner

```bash
python test.py
```

The test suite covers major functionality such as:

- API health
- Dataset discovery
- Dataset profiling
- Dataset preview
- Autonomous analysis
- Workflow execution
- Metric generation
- Insight generation
- Chart generation
- Text report generation
- PDF report generation
- Invalid dataset handling
- Invalid upload handling
- Live dataset refresh

### Run Pytest

```bash
pytest -v
```

### Expected test output

A successful run should report that the project-level test cases passed and provide a final summary similar to:

```text
AUTONOMOUS DATA ANALYSIS AGENT
AUTOMATED TEST SUITE

Tests Passed : 14
Tests Failed : 0
Total Tests  : 14

ALL TESTS PASSED SUCCESSFULLY
```

The exact count may change if additional tests are added later.

---

## Dataset Information

The project includes two Superstore datasets:

### Fixed benchmark

```text
datasets/superstore_fixed_benchmark_10000plus.csv
datasets/superstore_fixed_benchmark.xlsx
```

Use this dataset when reproducible results are required for demonstrations and testing.

### Live/refreshable dataset

```text
datasets/superstore_live_stream_10000plus.csv
datasets/superstore_live_stream.xlsx
```

The refresh endpoint reorders the live dataset to simulate a refreshed stream while retaining the same records.

See `datasets/DATASET_README.csv` for additional dataset information.

---

## Safety and Execution Model

The application does **not** execute arbitrary Python code directly from a user's natural-language query.

The analysis builder produces a transparent recipe, while the trusted backend analysis functions perform the actual operations. This design makes the workflow easier to inspect and reduces the risk associated with executing unrestricted generated code.

---

## Reporting

The generated PDF report contains:

- Dataset information
- User's analytical question
- Executive summary
- Data-quality information
- Autonomous analytical plan
- Key metrics
- Runtime information

The browser print view is intended for quick presentation or physical printing, while the PDF export provides a standalone report file.

---

## UI Modes

The dashboard supports both:

- **Dark mode** for a technical/data-platform style interface.
- **Light mode** with enhanced contrast and readability for reports, demonstrations, and classroom presentations.

The selected theme is persisted in browser local storage.

---

## Troubleshooting

### `Failed to fetch`

Make sure the backend is running on port `8000`:

```bash
uvicorn backend.app:app --reload --host 127.0.0.1 --port 8000
```

Then run the frontend on port `5173`.

### LangGraph import error

Install the project requirements again:

```bash
pip install -r requirement.txt
```

The project includes a compatibility fallback so it can still be inspected before dependencies are installed, but the intended runtime uses the StateGraph implementation.

### Dataset not found

Make sure you start the backend from the project root and that the `datasets/` directory is present.

### PDF generation error

Install ReportLab:

```bash
pip install reportlab
```

---

## Future Improvements

Possible extensions include:

- LLM-assisted natural-language planning
- More analytical operators
- Additional visualization types
- Persistent analysis history
- User authentication
- Database-backed project/workspace storage
- Role-based access control
- Sandboxed generated-code execution
- More advanced anomaly detection
- Semantic retrieval over previous analyses
- Cloud deployment

---

## Project Objective

The objective of this project is to demonstrate how an autonomous analytical workflow can reduce the manual effort involved in exploratory data analysis by combining:

```text
Natural Language Query
        ↓
Automated Planning
        ↓
Deterministic Data Analysis
        ↓
Validation
        ↓
Evidence-Based Insights
        ↓
Visualization
        ↓
Human-Readable Report
```

The result is a full-stack analytical assistant that is transparent enough for technical inspection while remaining accessible to non-technical users.

---

## License

This project is intended for educational, demonstration, and portfolio purposes. Add the license of your choice before distributing the repository publicly.

---

## Author

**Suhani Saraswat**  
B.Tech Computer Science Engineering  

- GitHub: https://github.com/Suhani-Saraswat
- LinkedIn: https://www.linkedin.com/in/suhani-saraswat-3b27ab332
