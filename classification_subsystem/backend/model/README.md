# Pretrained waste classification model

The included `resnet50_garbage_classificationv1.2.pth` weights come from [kendrickfff/my_resnet50_garbage_classificationv1.2](https://huggingface.co/kendrickfff/my_resnet50_garbage_classificationv1.2) on Hugging Face. The model page lists an MIT license.

## Architecture and training data

The author fine-tuned a ResNet50 originally pretrained on ImageNet. Its final layer has 12 outputs for waste classes. According to the [model card](https://huggingface.co/kendrickfff/my_resnet50_garbage_classificationv1.2), training used the [Garbage Classification dataset by Mostafa Abla](https://www.kaggle.com/datasets/mostafaabla/garbage-classification/data), containing 15,150 images across 12 classes. The author reports a train/validation split, 20 training epochs, and 98.66% accuracy on the validation set. These figures are the author's report; we have not independently reproduced the evaluation.

## Classes used in this project

The classifier returns one of these labels (in the order expected by `WasteClassifier`):

1. `battery`
2. `biological`
3. `brown-glass`
4. `cardboard`
5. `clothes`
6. `green-glass`
7. `metal`
8. `paper`
9. `plastic`
10. `shoes`
11. `trash`
12. `white-glass`

These are the model's output labels. The model predicts one label for the whole image; it does not locate or classify multiple objects separately.

## Input and limitations

The image should show the item clearly, preferably as the main object with good lighting. For inference with the included weights in this repository, the expected input is a **224 × 224 RGB image**, normalized with the ImageNet mean and standard deviation. The [model card](https://huggingface.co/kendrickfff/my_resnet50_garbage_classificationv1.2) mentions resizing, cropping and normalization during training and validation, but does **not** state an exact mandatory image size or normalization values. The 224 × 224 size and normalization values are the settings of this repository's inference code, not a published hard limit of ResNet50 itself.

The model can only choose among the 12 labels listed above. The model alone does not know local German sorting rules; the application reads those rules separately from its regional-rules database table.
