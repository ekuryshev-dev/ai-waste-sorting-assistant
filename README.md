# AI-Powered Waste Sorting & Recycling Assistant

**Platform name:** DiliGen

**Subtopic:** CV- and LLM-Based Waste Awareness Assistant for German Citizens

### Team Overview

|       Member        | Matr. No. |          Subsystem         |
| ------------------- | --------- | -------------------------- |
| Anastasiia Shovkova | 7219229   | `dashboard_subsystem`      |
| Evgenii Kuryshev    | 7227176   | `classification_subsystem` |
| Illia Parkhomenko   | 7219649   | `assistant_subsystem`      |

---

### Presentation

[Watch the team video review](https://www.youtube.com/)

[Watch the team presentation slides](https://www.youtube.com/)

---

### How to Run the System

There are three ways of how you can interact with the product.

1) Open the link to the hosted website:
[ADD LINK LATER]

On Render each backend service is deployed separately from its own folder with its own `requirements.txt`, and its variables are set in the Render dashboard. Frontend is deployed on Netlify.

2) Run locally (Python 3.12, Node 22.12 or newer), starting in the repository root:

1. Install the requirements of all three services (torch is the CPU-only build):
   ```
   pip install -r requirements.txt
   ```
2. Install the frontend packages once, then go back to the root:
   ```
   cd frontend
   npm install
   cd ..
   ```
3. Copy `.env.example` to `.env` in the repository root and fill in the values.
4. Start everything from the root:
   ```
   python main.py
   ```

This starts the assistant on port 8000, classification on 8001, the dashboard on 8002 and the frontend on http://localhost:5173. Press Ctrl+C to stop all of them.

3) Run with Docker (only Docker Desktop is needed), from the repository root:

1. Copy `.env.example` to `.env` and fill in the values.
2. Build and start all four containers:
   ```
   docker compose up --build
   ```
3. Open http://localhost:5173. Press Ctrl+C to stop, then `docker compose down` to remove the containers.

The first build takes several minutes because of torch. Inside Docker the services reach each other by name (for example `http://assistant:8000`), which `docker-compose.yml` sets, so the URLs in `.env` are only used by `python main.py`.

---

### Assistant Subsystem

An educational chat about waste, recycling and the circular economy for German citizens, plus a one-shot image fallback. When the CV model cannot classify an image, the fallback asks an LLM and returns a category with disposal instructions. The chat uses the regional recycling rules stored in the database and keeps its history for a limited time, per browser session, with no accounts.

**Class diagram:**
![Class diagram](docs/assistant_class_diagram_final.png)

### Classification Subsystem

The subsystem accepts a waste photo and a city. A pretrained ResNet50 classifies the image into one of 12 model labels, which are mapped to the materials used by our regional rules. DisposalRecommendationEngine retrieves the category and disposal instruction from our separate Neon table. If CV confidence is too low, the subsystem can ask the assistant service to return a material from the list available for that city. If no material can be identified, it asks the user for another photo. When analytics is configured, it receives the material, category and region, without the recommendation text.

**Class diagram:**
![Class diagram](docs/classification_class_diagram_HW2.png)

### Dashboard Subsystem

The dashboard block provides statistics for municipalities and responsible for collecting, processing, and presenting waste classification statistics for different regions. It reads the stored waste data and shows clear metrics and visualisations about waste composition as well as recycling-related rates.

**Class diagram:**
![Class diagram](dashboard_subsystem/docs/uml_class_diagram.png)

---

### Tech Stack and Rationale

* **Backend: Python and FastAPI.** Asynchronous by design, with built-in support for WebSockets and streaming responses, which leaves room to stream AI answers later. We chose it over Django, which bundles user accounts, an admin panel and templates that we don't need, since the project has no logins. Flask is just as light, but it needs extra libraries for input validation and API documentation. FastAPI provides both out of the box: Pydantic checks every request (for example the 500-character limit on chat messages), and it generates an interactive API page (/docs) automatically.
* **Database: Neon.tech (serverless PostgreSQL).** Neon offers PostgreSQL with a free tier, so the team gets a hosted database with no server to maintain. We chose PostgreSQL over MySQL because it gives reliable transactions and is strong at the analytical queries the dashboard needs (grouping and aggregating waste records by region and time).
* **ORM: SQLModel.** Table models and API schemas use the same Python classes. It works the same with either database, so the application code does not depend on the PostgreSQL choice. Protects the platform from SQL injection attacks.
* **Data processing: Pandas.** It aggregates the raw logs on the backend into compact JSON for the dashboard. Plotting libraries stay out of the backend to save server resources.
* **Frontend and charts: React (Vite) with Recharts or Chart.js.** React handles the live chat state. Charts are drawn in the browser from the backend's JSON, so no static images are sent over the network.
* **AI model: OpenAI gpt-6-luna.** Our chat answers are short and our fallback only needs 1-3 values as a response, so this new lightweight model is enough, and it also keeps the API cost small for a student project. The model name is set in one place, so we can switch to a stronger model without changing much code.
* **Deployment: Netlify and Render.** The frontend and backend are deployed separately. Netlify hosts the React build, and Render runs the FastAPI service. Both deploy automatically when we push to GitHub.
* **Version control and CI/CD: GitHub.** One repository holds all three subsystems. Each task has its own branch, and pushes trigger the deployments.
* **Testing: Pytest and HTTPX.** Pytest fixtures give each test a clean in-memory database. HTTPX and FastAPI's built-in test client exercise the endpoints without running a server, and the OpenAI client is replaced by a mock, so tests need no API key and cost nothing.
* **CV Model: ResNet50 Garbage Classification v1.2.** This pre-trained model is used to predict one of 12 waste labels for an image. The system prepares a 224 × 224 RGB image and applies the normalization used by the included weights. The model README in classification_subsystem lists the labels, training-data source and limitations.

---

### Repository Organization

Branch **main** holds the final version of the platform which is hosted on Render and Netlify via CI/CD.

Files and descriptions for each separate homework task can be found across the 4 branches:
* **Homeworkassignment001**
* **Homeworkassignment002**
* **Homeworkassignment003**
* **Homeworkassignment004**
  
Branch **dev** was used during the development process and does not hold the final version of the platform.

Branch **capstone-integration** was used for subsystem merging during the final stage of the project.

---
