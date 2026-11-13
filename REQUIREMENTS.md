# DiliGen: System Requirements

DiliGen helps people in Germany sort their waste. A user can photograph an item to get a disposal recommendation for their region, ask an AI assistant about recycling, and view statistics about classified waste. The system consists of three services (Classification, AI Assistant, Analytics) and one web frontend.

## Functional requirements

### Photo classification

| ID | Requirement |
|---|---|
| FR-01 | The user can upload a photo of a waste item, or take one with a phone camera. Only JPEG, PNG and WebP images up to 10 MB are accepted; other files are rejected with a clear message. |
| FR-02 | The user selects their region from a list of supported regions, loaded from the regional rules database. |
| FR-03 | A pre-trained computer vision model (ResNet50) predicts the waste class of the item together with a confidence score. |
| FR-04 | The predicted class is mapped to a material used in the regional rules. |
| FR-05 | The system looks up the category (recyclable, compostable or landfill) and the disposal instructions for that material in the selected region, and shows the item, its category and the instructions. |
| FR-06 | If the model's confidence is below 70% or its class cannot be mapped, the image is passed to the AI assistant's model, which suggests a material from the region's rules. If no material can be identified, the user is asked for another photo instead of receiving a guessed recommendation. |
| FR-07 | Every confident classification is recorded (material, category and region) for the statistics. |

### AI assistant

| ID | Requirement |
|---|---|
| FR-08 | The user can type a question and receive an answer in a conversation view, with an indicator while the answer is being generated. An empty chat offers suggested starter questions, such as "What is the circular economy?". |
| FR-09 | The assistant only discusses waste, recycling and sustainability, and politely declines other topics. |
| FR-10 | For local questions the assistant uses the regional rules stored in the database. If the rules do not cover the item or region, it says so and refers the user to the local municipality. |
| FR-11 | If a question is too broad, or the answer depends on a region the user has not named, the assistant asks one clarifying question instead of guessing. |
| FR-12 | The assistant answers in the language of the user's message. |
| FR-13 | The assistant keeps the context of the conversation, so follow-up questions work. |
| FR-14 | The conversation is kept for up to one day within the same browser session, so the user can leave the chat and return to it. The user can clear the conversation at any time. |

### Analytics

| ID | Requirement |
|---|---|
| FR-15 | The dashboard receives a record (material, category and region) for every confident classification. Only requests with the shared secret key can add records; all other requests are rejected. |
| FR-16 | Each record is validated before it is stored: the material and region must not be empty and the category must be recyclable, compostable, landfill or unknown. Invalid records are rejected with a clear error message. Valid records are stored with their date and time. |
| FR-17 | The user can view the statistics for all regions together or for a single region, and for the last 7 days, the last 30 days or all time. The region list contains the regions that have records. |
| FR-18 | The dashboard shows the total number of classified items and their distribution across recyclable, compostable, landfill and unknown waste, as percentages and as a donut chart. |
| FR-19 | The dashboard shows a chart of daily classifications per category. Each point shows its date, category and number of items. |
| FR-20 | The dashboard shows the day with the highest activity in the selected period and the number of items classified on that day. |
| FR-21 | The statistics update automatically as soon as a new record arrives for the selected region, without reloading the page. The page shows whether the live connection is active and reconnects automatically if it drops. |

## Non-functional requirements

| ID | Requirement |
|---|---|
| NFR-01 | **Independence.** The three services run separately and communicate over HTTP. If one service is down, the pages of the other services keep working. |
| NFR-02 | **Extensibility.** New regions and sorting rules are added in the database without changing the source code. Class mappings are stored in a separate file, so rules and mappings can change without retraining the model. |
| NFR-03 | **Replaceable model.** The computer vision model can be replaced without changing the sorting logic or the regional rules; only the class mapping needs updating. |
| NFR-04 | **Privacy.** Uploaded images are not stored. Images are sent to OpenAI only when the computer vision model cannot classify them. For the chat, only the question, the needed regional rules and the recent conversation are sent. No other personal data is collected, and there are no user accounts. |
| NFR-05 | **Security.** API keys and database credentials are kept in environment variables, are never sent to the browser and are never committed to the repository. Writing analytics records requires a shared secret key. The deployed site uses HTTPS. |
| NFR-06 | **Limits and errors.** Chat messages are limited to 500 characters, only the last 20 messages are sent as context, and model calls time out after 20 seconds. If a model call fails, the user sees a clear error message and can retry; other pages are not affected. |
| NFR-07 | **Availability on free hosting.** Each page shows a loading message while its service starts up, locks with a "Try again" option if the service stops responding, and keeps the services awake while the page is open. |
| NFR-08 | **Persistence.** Regional rules, chat history and statistics are stored in a PostgreSQL database and remain available after a restart. |
| NFR-09 | **Robustness.** Missing or invalid data does not crash the system: regions without records show an empty state, and invalid analytics records are rejected. |
| NFR-10 | **Testability.** Each service has its own automated tests (pytest) that run in isolation. The AI tests use a mock client, so they need no API key and cost nothing. |
| NFR-11 | **Usability.** The web interface works on phones and desktops and can be used with the keyboard (Enter sends a chat message). The chat page states that answers are AI-generated and may be inaccurate. |
| NFR-12 | **Deployment.** The whole system starts locally with one command (`python main.py` or `docker compose up --build`). In production, the frontend is hosted on Netlify and each service on Render. |
