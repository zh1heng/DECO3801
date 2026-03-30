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
   * Concatenate the extracted structural features into a 1D feature vector.
   * Manually label cognitive load scores for dozens to hundreds of common websites.
   * Train a Random Forest **Base Model** (v1 baseline) using `sklearn.ensemble.RandomForestRegressor` capable of handling foundational layouts.
4. **Integration Testing**:
   * Enable the FastAPI backend to execute the scraping and scoring process, returning a JSON response containing the total score and evaluation suggestions to the frontend `DashboardPage.tsx`.

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
