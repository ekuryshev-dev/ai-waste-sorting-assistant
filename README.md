# Waste Sorting and Recycling Assistant

## Hometask 1. Object Oriented Concepts
> 
>The primary goal of this assignment is to translate the high-level architecture designed in your Capstone Project UML diagrams into concrete Object-Oriented Programming (OOP) class implementations.
> 
> ### Requirements & Technical Specifications. Code Implementation
> 
> - Per Team Member Requirement: Every student in the team must implement at least 3 unique classes corresponding to their assigned subsystem.
> - Class Requirements: Each class must include:
>   1. Constructor (`__init__`): Proper state initialization.
>   2. Initialization Methods: Setup or configuration logic where applicable.
>   3. Encapsulation (Getters & Setters): Accessor and mutator methods for class attributes.
---
### Waste Classification & Sorting Subsystem

**Responsible:** Evgenii Kuryshev

At this stage, the subsystem classifies photos of waste with a pretrained CV model and looks up sorting instructions for the selected region in a local JSON file. For a prediction with at least 70% confidence, it returns the material, disposal category and recommendation; otherwise, it asks for another photo.

#### Classes

- `ImageQuery` holds the image bytes and selected region for one request.
- `ImageProcessor` opens an image, converts it to RGB and pads it to 224 × 224 pixels.
- `WasteClassifier` loads the pretrained ResNet50 weights and predicts a waste label with its confidence.
- `ClassificationResult` holds the predicted waste label and confidence.
- `ClassMapping` converts a model label to a material name used by the regional rules.
- `RegionalRulesService` reads the rules from a JSON file and finds a category and instruction for a material in a region.
- `Category` defines the four disposal categories: `unknown`, `recyclable`, `compostable` and `landfill`.
- `DisposalRecommendation` holds the status, recommendation message, classification result and category returned to the user.
- `DisposalRecommendationEngine` coordinates image preparation, classification, label mapping and the regional rule lookup. Predictions below 70% confidence return a request for another photo.

#### Class Diagram

![Waste Classification & Sorting Subsystem — Hometask 1 UML Class Diagram](docs/classification_class_diagram_HW1.png)

#### Model

The subsystem uses the pretrained [ResNet50 Garbage Classification v1.2](https://huggingface.co/kendrickfff/my_resnet50_garbage_classificationv1.2) model. It predicts one of 12 waste labels. The demo accepts JPEG, PNG and WebP images; `ImageProcessor` converts each image to a 224 × 224 RGB input for the classifier. See the [model README](classification_subsystem/backend/model/README.md) for the training data, complete label list and limitations.

#### Run

From the repository root:

```powershell
cd classification_subsystem/backend
python -m pip install -r requirements.txt
python demo.py
```

By default, `demo.py` processes every supported image in `examples` using the Dortmund rules. To process one image or select another region:

```powershell
python demo.py examples/cardboard.jpg --region Bochum
```
---
### AI Assistant Subsystem

**Responsible:** Illia Parkhomenko

#### Classes

To be added.

#### Class Diagram

To be added.

#### Run

To be added.
---
### Waste Analytics & Dashboard Subsystem

**Responsible:** Anastasiia Shovkova

At this stage, the subsystem collects and analyzes classified waste records using object-oriented Python classes. It calculates waste category distribution, recyclable share, overall statistics, and daily trends for a selected region.

For Hometask 1, the subsystem uses an in-memory repository and displays the results in a console-based Dashboard. 

#### Classes

- `Category` defines four waste categories: recyclable, compostable, landfill, and unknown.

- `WasteRecord` represents a classified waste item with its category, region code, unique ID, and creation timestamp.

- `WasteRepository` stores waste records in memory and provides methods to add, retrieve, and filter records by region.

- `WasteAnalyticsService` calculates category distribution, recycling statistics, and daily trends.

- `StatisticsSummary` stores the total number of records, category percentages, and recycling rate.

- `TrendPoint` stores daily counts for the four waste categories.

- `AnalyticsController` connects the Dashboard to the analytics service and provides access to statistics and trends.

- `Dashboard` displays waste statistics, category distribution, recycling rate, and trends in the console.

#### Object-Oriented Concepts

**Constructors (__init__):** Initialize class attributes and dependencies.

**Encapsulation:** Class attributes are accessed and modified through getter and setter methods.

**Dependency Injection:** Repository, Service, and Controller objects are provided through constructors.

**Separation of Responsibilities:** Data storage, analytics calculations, application control, and presentation are handled by separate classes.

The recycling rate represents the percentage of recognized items classified as recyclable, not the actual municipal recycling rate.

#### Class Diagram

![Waste Analytic & Dashboard Subsystem — Hometask 1 UML Class Diagram](docs/dashboard_hometask_1_class_diagram.png)

#### Model 

The Waste Analytics Subsystem does not use a machine learning model. It processes waste classification results provided by the Waste Classification & Sorting Subsystem.

The subsystem uses object-oriented data models such as WasteRecord, StatisticsSummary, and TrendPoint to represent waste records and analytical results. WasteAnalyticsService calculates category distribution, recyclable share, and daily trends.

For Hometask 1, the data is stored in an in-memory WasteRepository.

#### Run

From the repository root, install the dependencies:

```python -m pip install -r dashboard_subsystem/requirements.txt```

Run the console demonstration:
```
cd dashboard_subsystem
python -m waste_analytics.main
```
The demonstration creates a waste record for a recyclable bottle in Dortmund and displays the calculated statistics.

**Tests**

From the dashboard_subsystem directory:

```python -m pytest tests/test_waste_analytics.py -v```

All 7 unit tests passed, covering category distribution, statistics, region filtering, trends, empty data, and repository operations.
