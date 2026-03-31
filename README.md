# DECO3801
For project 14

## Backend Machine Learning Architecture: Progressive Multi-modal Random Forest Model Based on WCAG Principles

The backend of this project aims to implement a Hybrid Model, strictly grounded in the cognitive accessibility principles of the **WCAG (Web Content Accessibility Guidelines)**. By extracting both **HTML structural features** and **visual rendering features (screenshots)** of a webpage, it intelligently evaluates compliance and usability using the **Random Forest** algorithm.

To ensure engineering reliability and project delivery, we will adopt a **"Fallback first, Advanced later" v1.0 / v2.0 progressive dual-track implementation plan**.

---

###  Implementation Milestones

#### Milestone 1: v1.0 Pure HTML Structural Baseline (Fallback Solution)
*The goal of this phase is to quickly establish the full end-to-end communication between the frontend and backend, and train a baseline evaluation model using existing rules or lightweight structural trees.*

1. **Backend Infrastructure and Framework**:
   * Use **Python + FastAPI** to build high-performance, asynchronous backend service APIs.
   * Develop the `/api/analyze` routing endpoint to receive frontend requests.
2. **Pure HTML Feature Engineering (Base Dimension)**:
   * Use `requests` + `BeautifulSoup` to fetch the DOM tree and perform structural analysis (evolving from the current `HTML test.py` logic).
   * Extract **WCAG-compliant pure structural text features**:
     * **Understandable (WCAG 3.1 Readable)**: Use basic Natural Language Processing (NLP) to calculate average sentence complexity and baseline reading difficulty vocabulary.
     * **Operable (WCAG 2.4 Navigable)**: Check for non-sequential jumps in heading levels (Heading Jumps) that mapping to cognitive gaps, analyze interactive link density, and contextual navigation structures.
3. **Structured Datasets and Initial Training**:
   * **Data Sourcing (Common Crawl)**: The foundational dataset is derived from the massive, open-source web archive [Common Crawl](https://commoncrawl.org/). By downloading and processing its WARC (Web ARChive) data dumps, we efficiently acquire a highly diverse and representative sample of real-world HTML documents across the global internet.
   * **Data Processing Pipeline**: The raw HTML strings parsed from the Common Crawl archives are fed into our `BeautifulSoup` cleaning pipeline to strip irrelevant scripts and styles. The purified DOM trees are then processed to extract the WCAG structural metrics, concatenating them into a 1D feature vector matrix.
   * **Labeling & Training**: A targeted subset of these websites is labeled for cognitive load scores. We then train a Random Forest **Base Model** (v1 baseline) using `sklearn.ensemble.RandomForestRegressor` to map these structural features to cognitive accessibility levels.
4. **Integration Testing & Data Calling Flow**:
   * Enable the FastAPI backend to execute the scraping and scoring process, returning a JSON response containing the total score and evaluation suggestions to the frontend `DashboardPage.tsx`.
   * **Frontend API Calling Location**: The API request to the backend is made in [`src/App.tsx`](src/App.tsx) inside the `handleCheckWebsite(url)` function. It parses the JSON representation of the scores and passes them to `DashboardPage.tsx` for visual rendering.
   * **Frontend Output Location**: The resolved metrics (`vh_score`, `nav_score`, `lang_score`, `total_score`, and `reasons`) are statically bound and rendered inside [`src/components/DashboardPage.tsx`](src/components/DashboardPage.tsx) across the Radar Chart and Score details. (Missing scores will use a fallback value of 5).
   * **Backend Output Location**: The actual integration endpoint where `total_score` and `reasons` (along with sub-scores) are compiled into JSON is located at [`backend/api/analyze.py`](backend/api/analyze.py). It acts as the routing layer wrapping the original logic of `backend/html_test.py`.

#### Milestone 2: v2.0 Multi-modal (HTML + Computer Vision Screenshots) Advanced Edition
*Building upon the successful and robust v1.0, this phase advances user experience and accuracy. It specifically targets the technical challenge of "cognitive burden caused by chaotic styling and layouts."*

1. **Headless Browser Integration Upgrade**:
   * Upgrade the backend from simple `requests` to launching a **Playwright** headless browser. In addition to retrieving the final rendered dynamic HTML, it takes **full-viewport screenshots** to feed the visual engine.
2. **Additional Visual Screenshot Features (Advanced Dimension)**:
   * Introduce `OpenCV` to compute features on the full panoramic screenshot:
   * *This phase directly quantifies whether the page adheres to the **Perceivable** principles of WCAG:*
   * **White Space Ratio & Layout Density (Extension of WCAG 1.4.12 Text Spacing)**: Calculate the background white space ratio. Visual congestion is a primary cause of Cognitive Overload.
   * **Edge Density**: Use Canny edge detection to calculate the visual clutter of the interface, ensuring avoidance of excessive visual noise interference.
   * **Color Complexity (WCAG 1.4 Distinguishable)**: Calculate color vividness and the high-density distribution of high-contrast areas to prevent potential sensory overload.
3. **Hybrid Model Retraining (Hybrid Training)**:
   * Construct a **multi-modal feature vector matrix**, formed by sequentially concatenating `[HTML Features Array, Vision Features Array]`.
   * Feed the combined data back into the Random Forest for retraining. By integrating both perceptual dimensions (code structure + final rendered vision), this advanced version achieves accuracy and interference-resistance far beyond pure code parsing.
4. **Feature Importance Analysis and Smart Suggestions**:
   * Utilize the built-in **Feature Importance** evaluation of the multi-dimensional model outputs to provide "white-box" interpretations of low scores (e.g., determining if the issue lies in excessive colors or dense, long paragraphs).
   * Package these dynamically analyzed "root causes" into actionable suggestions to dynamically render the frontend radar chart and optimization panel.

---

###  Project Structure

To maintain clarity without complicating the development workflow, the project adopts an "Un-isolated Frontend, Encapsulated Backend" pattern. The frontend remains in the root folder, while the Python backend logic is strictly separated inside the `backend/` directory using a standard 5-layer architecture.

```text
DECO3801/
├── src/                # React Vite Frontend Source Code
│   ├── components/     # UI Components (LandingPage, DashboardPage, etc.)
│   ├── App.tsx         # Main Frontend Logic & View Routing
│   ├── main.tsx        # React Entry Point
│   └── index.css       # Tailwind & Global Styles
├── backend/            # Python FastAPI Backend
│   ├── api/            # API Route Handlers & Endpoints
│   ├── service/        # Core Business Logic (Scraping, Feature Extraction, Model Inference)
│   ├── repository/     # Data Access Layer & Database Integrations
│   ├── schema/         # Pydantic Models for Input/Output Validation
│   ├── model/          # Database ORM Models
│   └── HTML test.py    # Original Prototype Script for ML Analysis
├── index.html          # Vite HTML Templates
├── package.json        # NPM Dependencies & Scripts
└── vite.config.ts      # Vite Bundling Configuration
```
## Temporary Data Evaluation Criteria

To establish a functional baseline model (v1.0), this project adopts a **rule-based scoring system** to approximate cognitive accessibility before integrating machine learning models.

The current evaluation framework transforms webpage features into quantifiable metrics across three dimensions: **Visual Hierarchy**, **Navigation Complexity**, and **Language Simplicity**. These metrics are computed from HTML structure and textual content.

---

### 1. Language Complexity (WCAG 3.1 Readable)

We estimate reading difficulty using three statistical indicators:

- **Average Sentence Length**
  
  AvgSentenceLength = WordCount / SentenceCount

- **Average Word Length**
  
  AvgWordLength = TotalCharacterCount / WordCount

- **Average Paragraph Length**
  
  AvgParagraphLength = WordCount / ParagraphCount

#### Scoring Rules:
- +10 if AvgSentenceLength > 20  
- +10 if AvgSentenceLength > 30  
- +8 if AvgWordLength > 5  
- +7 if AvgParagraphLength > 80  

Maximum Language Score: **35**

---

### 2. Visual Hierarchy (WCAG Structure)

We evaluate the structural clarity of headings:

- **Heading Jump Detection**

  HeadingJump = number of times (h_i - h_{i-1} > 1)

#### Scoring Rules:
- +20 if no `<h1>` is present  
- +15 if more than 2 `<h1>` tags exist  
- +25 if no headings are detected  
- +5 × HeadingJump (capped at 20)

Maximum Visual Hierarchy Score: **40**

---

### 3. Navigation Complexity (WCAG Navigable)

We analyze navigation structure based on link density and orientation cues:

- **Navigation Link Count**

  NavLinks = number of links inside `<nav>`

#### Scoring Rules:
- +10 if NavLinks > 10  
- +10 if NavLinks > 20  
- +5 if no breadcrumb navigation is detected  

Maximum Navigation Score: **25**

---

### 4. Final Cognitive Complexity Score

The total cognitive load score is computed as:

TotalScore = VisualHierarchyScore + NavigationScore + LanguageScore

The final score is bounded within the range [0, 100].

---

### 5. Complexity Level Classification

- **Low Complexity**: Score < 34  
- **Medium Complexity**: 34 ≤ Score < 67  
- **High Complexity**: Score ≥ 67  

---

### 6. Notes on Current Approach

This rule-based system serves as a **temporary evaluation standard** for:

- Rapid prototyping and system integration  
- Providing interpretable baseline results  
- Supporting initial frontend-backend data flow  

In future iterations (v2.0), this heuristic model will be replaced by a **machine learning model (Random Forest)** trained on labeled cognitive accessibility datasets to improve accuracy and adaptability.