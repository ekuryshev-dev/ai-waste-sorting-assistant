# Waste Sorting and Recycling Assistant

## Hometask4. Exception Handling and Unit tests

> The aim of this work is to learn how to handle error in your application and  testing princples in Django/Flask.
> 
> Please learn the principles of error handling https://docs.python.org/3/tutorial/errors.html
> 
> Create an error-handling class for each subsystem.
> 
> Create 15 different tests for your application.
---
### Waste Classification & Sorting Subsystem

**Responsible:** Evgenii Kuryshev

In Hometask 4, the subsystem adds error handling and automated tests to the classification, regional-rules and API workflow built in Hometasks 1–3. Invalid image data and missing disposal rules now raise `ClassificationError`. The FastAPI endpoint returns a clear HTTP error: `400` for an invalid image or region and `422` for a missing rule.

Fifteen tests cover image preparation, class mapping, regional rules, confidence filtering, CV and AI recommendation paths, and API responses.

#### Tests

1. A valid photo is prepared as a 224 × 224 RGB image.
2. Invalid image data raises `ClassificationError`.
3. A model label is mapped to a material; an unknown label has no mapping.
4. An existing regional rule returns its category and instructions.
5. A missing regional rule raises `ClassificationError` with status `422`.
6. A confidence threshold outside the range from 0 to 1 is rejected.
7. A confident CV prediction uses the regional rule and is sent to analytics.
8. An uncertain CV prediction uses the AI recommendation and is not sent to analytics.
9. An AI response without instructions asks the user for another photo.
10. An uncertain prediction without an AI fallback asks for another photo.
11. An unsupported region is rejected.
12. The confidence filter removes low-confidence prediction events.
13. The API handler returns a recommendation for a valid image and region.
14. The API handler returns status `400` for invalid image data.
15. The API handler returns status `422` when a regional rule is missing.

#### Model

The subsystem uses [ResNet50 Garbage Classification v1.2](https://huggingface.co/kendrickfff/my_resnet50_garbage_classificationv1.2), which predicts one of 12 waste labels for an image. `ImageProcessor` prepares a 224 × 224 RGB image; `WasteClassifier` applies the normalization used by the included weights. The [model README](classification_subsystem/backend/model/README.md) lists the labels, training-data source and limitations.

#### Run

From the repository root, install the dependencies and run the 15 tests:

```powershell
python -m pip install -r classification_subsystem/backend/requirements.txt
python -m pytest classification_subsystem/backend/tests/test_subsystem.py -q
```

The tests use temporary local data and do not require service credentials.

---

### Waste Analytics & Dashboard Subsystem

**Responsible:** Anastasiia Shovkova

To be added.

#### Classes

To be added.

#### Class Diagram

To be added.

#### Model

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

#### Model

To be added.

#### Run

To be added.

---
