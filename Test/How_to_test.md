##  Testing & Verification

Follow the steps below to run and verify the system:

---

### 1. Start the Backend Service

Open a terminal and activate your Python environment (make sure required packages are installed, such as `fastapi`, `requests`, `selenium`, `beautifulsoup4`).

Run the following commands:

```bash
cd ./backend
pip install fastapi uvicorn pydantic requests
python -m uvicorn main:app
#Then
*Click index.html in the Test folder
*Enter a URL in the input field
*Click the Analyze button
*Check the results