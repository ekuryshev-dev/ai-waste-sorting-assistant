# Waste Sorting and Recycling Assistant

## Hometask3. Web APIs & Database Access Layers

> The aim of this work is to learn how to create a simple Django or Flask project and use it with MySql for data output.
> 
> To create your first application please follow Django documentation or Flask documentation https://flask.palletsprojects.com/en/stable/quickstart/
> 
> Create your project at the github and apply the link your project. Add your indentification and update the readme file with the project information.
---
### Waste Classification & Sorting Subsystem

**Responsible:** Evgenii Kuryshev

In Hometask 3, the subsystem replaces its JSON file of regional disposal rules with a `classification_recycling_rules` table in Neon/PostgreSQL. `RegionalRulesService` now reads the table to provide the available regions, check the region selected for a request, and find the category and disposal instructions after the CV model identifies a mapped material with at least 70% confidence. The confident CV result can then be sent to the analytics API.

The new FastAPI endpoint accepts an image and region and returns the recommendation as JSON. If the CV result is uncertain, the subsystem sends the original image and region to the AI Assistant API and returns its instructions directly. This path does not read a disposal rule for the predicted material.

#### Classes

**Retained from Hometasks 1 and 2**

- `ImageQuery` holds the image, selected region and image MIME type.
- `ImageProcessor` opens an image and prepares a 224 × 224 RGB image for the CV model.
- `WasteClassifier` loads the pretrained model and predicts a label and confidence.
- `ClassificationResult` holds the identified material, confidence and result source (`cv` or `ai`).
- `ClassMapping` maps a model label to the material name used by the rules.
- `RegionalRulesService` reads available regions and disposal rules from Neon/PostgreSQL.
- `Category` defines `unknown`, `recyclable`, `compostable` and `landfill`.
- `DisposalRecommendation` holds the response status, message, region, category and optional classification.
- `DisposalRecommendationEngine` chooses the CV or AI path and coordinates the recommendation and analytics record.
- `PredictionEvent` holds one image prediction and whether it passes the confidence threshold.
- `StreamProcessor` defines the common abstract `process()` method for stream stages.
- `ImageClassifierProcessor` turns an image path into a prediction event.
- `JsonlWriter` writes prediction events to a JSONL file.
- `ConfidenceFilter` stops low-confidence events from reaching later stages.
- `Pipeline` runs stream processors in sequence.
- `PredictionStream` iterates over images and yields events that pass through the pipeline.

**Added in Hometask 3**

- `RecyclingRule` represents a regional rule in the `classification_recycling_rules` SQLModel table.
- `FallbackResult` holds the category, material and instructions returned by the AI Assistant.
- `AssistantFallbackClient` sends uncertain images and regions to the AI Assistant API.
- `AnalyticsClient` sends confident CV results to the analytics API.

#### Class Diagram

To be added.

#### Model

The subsystem uses [ResNet50 Garbage Classification v1.2](https://huggingface.co/kendrickfff/my_resnet50_garbage_classificationv1.2), which predicts one of 12 waste labels for an image. `ImageProcessor` prepares a 224 × 224 RGB image; `WasteClassifier` applies the normalization used by the included weights. The [model README](classification_subsystem/backend/model/README.md) lists the labels, training-data source and limitations.

#### Run

From the repository root, install the dependencies and start the API:

```powershell
python -m pip install -r classification_subsystem/backend/requirements.txt
python -m uvicorn classification_subsystem.backend.src.main:app --port 8001
```

Open `http://127.0.0.1:8001/docs`. `GET /classification/regions` returns the regions stored in the rules table. `POST /classification/recommend` accepts an image and one of those regions and returns a classification and disposal recommendation.

---

### Waste Analytics & Dashboard Subsystem

**Responsible:** Anastasiia Shovkova

To be added.

#### Classes

To be added.

#### Class Diagram

To be added.

#### Run

To be added.

---

### AI Assistant Subsystem

**Responsible:** Illia Parkhomenko

To be added.

#### Classes

To be added.

#### Class Diagram

To be added.

#### Run

To be added.
