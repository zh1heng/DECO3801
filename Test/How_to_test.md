##  Testing & Verification

Follow the steps below to run and verify the system:

---

### 1. Install Dependencies & Start the Backend Service

Open a terminal and activate your Python environment. You need to install the required Python packages and the Playwright browser binaries.

Run the following commands from the project root (`DECO3801` folder):

```bash
# Install backend dependencies
pip install fastapi uvicorn pydantic requests beautifulsoup4 playwright

# Install Playwright browser binaries (required for web scraping)
playwright install

# Start the FastAPI backend service
python -m uvicorn backend.main:app --reload --port 8000
```

### 2. Run the Frontend

* Go to the `Test` folder and open `index.html` in your browser.
* Enter a URL in the input field.
* Click the Analyze button.
* Wait patiently for the progress bar to finish (the backend is running Playwright headlessly to crawl and analyze the page, which may take about 10-15 seconds).
* View the final cognitive accessibility report and scores!