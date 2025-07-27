# Challenge 1A: Universal PDF Outline Extractor

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
- [Extending the Project](#extending-the-project)
- [Contribution Guidelines](#contribution-guidelines)
- [License](#license)

---

## About the Project
This project is part of the Adobe Hackathon Challenge 1A. It provides a robust, containerized pipeline to extract hierarchical outlines (TOC) and titles from PDF documents at scale, saving results as structured JSON files.

## Features
- Batch processing of PDFs in a directory
- Title extraction from first-page text, metadata, or filename
- Hierarchical outline extraction using embedded TOC/bookmarks or heuristics
- Heuristic fallback for PDFs without TOC (font/style analysis)
- JSON output for each PDF
- Progress feedback with `tqdm`
- Fully Dockerized for reproducibility
- Modular codebase for easy extension

---

## Project Structure
```text
challenge-1a/
├── app/
│   ├── main.py            # Main pipeline script
│   ├── pdf_utils.py       # PDF parsing utilities
│   ├── requirements.txt   # Python dependencies
├── input/                 # Place your PDF files here
├── output/                # Extracted outlines as JSON
├── Dockerfile             # Docker build instructions
├── docker-compose.yml     # Compose for easy orchestration
├── .gitignore             # Git ignore rules
├── README.md              # This file
```

---

## Quickstart (TL;DR)
```bash
git clone <your-repo-url>
cd adobe-hackathon/challenge-1a
# Place your PDFs in input/
docker-compose up --build
# Results will appear in output/
```

---

## Step-by-Step Setup Guide

### 1. Clone the Repository
```bash
git clone <your-repo-url>
cd adobe-hackathon/challenge-1a
```

### 2. Prepare Input Files
- Place **all PDF files** you want to process into the `input/` directory.
- Example:
  ```bash
  cp /path/to/your/*.pdf input/
  ```

### 3. Build & Run with Docker Compose
- Build and start the pipeline:
  ```bash
  docker-compose up --build
  ```
- Output will be written to `output/`.

### 4. (Alternative) Run Locally Without Docker
- Ensure Python 3.9+ and pip are installed.
- Install dependencies:
  ```bash
  pip install -r app/requirements.txt
  ```
- Run the main script:
  ```bash
  python app/main.py
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
   - Processed outlines will appear in the `output/` directory as JSON files.
   - Logs are visible in the console and in `/tmp/process.log` inside the container.

### Manual Python Run
1. **Install dependencies:**
   ```bash
   pip install -r app/requirements.txt
   ```
2. **Run:**
   ```bash
   python app/main.py
   ```
3. **Output:**
   - Results in `output/`

### Custom Input/Output Directories
You can specify custom input/output directories using command-line arguments:
```bash
docker run --rm -v $(pwd)/my_pdfs:/input -v $(pwd)/my_json:/output pdf-outline-extractor --input-dir /input --output-dir /output
```

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
- **No PDF files found:**

---

## 🛠️ Troubleshooting
- **No PDFs found:** Ensure files are in the `input/` directory and have `.pdf` extensions.
- **Permission errors:** Check read/write permissions on `input/` and `output/`.
- **Missing dependencies:** Run `pip install -r app/requirements.txt` again.
- **Docker issues:** Ensure Docker is installed and running. Use `sudo` if necessary on Linux/Mac.
- **Logs:** Detailed logs are in `app/process.log`.

---

## 🤝 Contributing
1. Fork this repo and create a feature branch.
2. Follow existing code style and add docstrings/comments.
3. Test your changes locally.
4. Submit a pull request with a clear description.
- Make your changes and add tests if relevant.
- Submit a pull request with a clear description.
- Follow best practices for Python (PEP8) and Docker.

---

## License
This project is provided as-is for educational and research purposes.
