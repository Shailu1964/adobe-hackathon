# Challenge 1B: Document Understanding with Sentence Transformers

---

## 📚 Table of Contents
- [About the Project](#about-the-project)
- [Features](#features)
- [Project Structure](#project-structure)
- [Quickstart (TL;DR)](#quickstart-tldr)
- [Step-by-Step Setup Guide](#step-by-step-setup-guide)
- [Usage Instructions](#usage-instructions)
- [Docker & Docker Compose](#docker--docker-compose)
- [Troubleshooting](#troubleshooting)
- [Development & Contribution](#development--contribution)
- [License](#license)

---

## About the Project
This project is part of the Adobe Hackathon Challenge 1B. It provides a robust, containerized pipeline to process PDF documents, extract sections, and perform semantic analysis using transformer-based NLP models (`sentence-transformers`).

## Features
- Batch processing of PDF files
- Sentence/section embedding using transformer models (e.g., `all-MiniLM-L6-v2`)
- Semantic ranking and clustering of document sections
- Output results as JSON for downstream analysis
- Fully containerized for reproducibility and easy onboarding

---

## Project Structure
```text
challenge-1b/
├── Dockerfile             # Docker build instructions
├── docker-compose.yml     # Orchestrates container run
├── requirements.txt       # Python dependencies
├── .gitignore             # Files/folders to ignore in git
├── README.md              # This file
├── downloa_models.py      # Script to download transformer models
├── input/                 # Place your PDF files here
├── output/                # Output JSON/results
├── models/                # Pre-downloaded models
└── src/
    ├── main_1b.py         # Main pipeline script
    ├── intelligence_core.py
    └── pdf_utils.py
```

---

## Quickstart (TL;DR)
```bash
git clone <your-repo-url>
cd adobe-hackathon/challenge-1b
# Place your PDFs in input/
docker-compose up --build
# Results will appear in output/
```

---

## Step-by-Step Setup Guide

### 1. Clone the Repository
```bash
git clone <your-repo-url>
cd adobe-hackathon/challenge-1b
```

### 2. Prepare Input Files
- Place **all PDF files** you want to process into the `input/` directory.
- Example:
  ```bash
  cp /path/to/your/*.pdf input/
  ```

### 3. (Optional) Download Models
- If you want to pre-download the transformer model (for offline use), run:
  ```bash
  python downloa_models.py
  ```
- This will save the model in `models/`.

### 4. Build & Run with Docker Compose
- Build and start the pipeline:
  ```bash
  docker-compose up --build
  ```
- Output will be written to `output/`.

### 5. (Alternative) Run Locally Without Docker
- Ensure Python 3.10+ and pip are installed.
- Install dependencies:
  ```bash
  pip install -r requirements.txt
  ```
- Run the main script:
  ```bash
  python src/main_1b.py
  ```

---

## Usage Instructions

### Using Docker Compose
1. **Add PDFs:** Place your PDF files in the `input/` folder.
2. **Run:**
   ```bash
   docker-compose up --build
   ```
3. **View Output:**
   - Processed results will appear in the `output/` directory as JSON files.
   - Logs are visible in the console and in `/tmp/process.log` inside the container.

### Manual Python Run
1. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```
2. **Run:**
   ```bash
   python src/main_1b.py
   ```
3. **Output:**
   - Results in `output/`

---

## Docker & Docker Compose
- **Dockerfile:** Defines the environment, installs Python and system dependencies, copies code, and sets up the entrypoint.
- **docker-compose.yml:** Mounts `input/` and `output/` as volumes, so files persist on your host.

### Common Docker Commands
- Build & run:
  ```bash
  docker-compose up --build
  ```
- Stop containers:
  ```bash
  docker-compose down
  ```
- View logs:
  ```bash
  docker-compose logs
  ```

---

## Troubleshooting
- **Permission Errors:**
  - If you see permission errors with `input/` or `output/`, ensure you are running as root in Docker (default for this repo).
  - On Windows, avoid using a non-root user in Docker due to volume permission issues.
- **No Output:**
  - Check that your PDFs are in `input/` before starting the container.
  - Check logs for errors (`/tmp/process.log` inside the container).
- **Model Download Issues:**
  - Ensure internet access for downloading models, or pre-download using `downloa_models.py`.
- **Docker Compose Version Warning:**
  - If you see a warning about the `version` attribute, you can safely ignore or remove it from `docker-compose.yml`.

---

## Development & Contribution
- Fork this repository and create a new branch for your feature or bugfix.
- Make your changes and add tests if relevant.
- Submit a pull request with a clear description.
- Follow best practices for Python (PEP8) and Docker.

---

## License
This project is for educational and hackathon purposes only. See LICENSE file if provided.
