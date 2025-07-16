# Image-Similarity-Retrieval-using-Siamese-Neural-Network-with-MobileNetV2
A deep learning project using a Siamese Network with MobileNetV2 to retrieve and rank visually similar images from the `tf_flowers` dataset. Trained on image pairs with contrastive loss and evaluated using Precision\@5, the model achieves 70–85% accuracy in visual similarity search.

🔍 Siamese Network for Image Similarity Retrieval
This project implements an end-to-end image similarity search engine using a Siamese Neural Network architecture trained on the tf_flowers dataset from TensorFlow. Given a target image, the model retrieves and ranks visually similar images based on learned image embeddings.

📌 Problem Statement
Build a machine learning model that can identify and retrieve similar images from a large dataset (1,000–5,000+ images), ranking them by visual closeness.

🎯 Objectives
Learn a similarity function using Siamese Network architecture.

Generate feature embeddings for each image using a shared CNN encoder.

Rank and retrieve images based on cosine similarity.

Evaluate retrieval accuracy using Precision@K.

📁 Dataset
Source: TensorFlow Datasets - tf_flowers [https://www.tensorflow.org/datasets/catalog/tf_flowers]

Size: ~3,600 images across 5 flower categories

Task: Find similar images (e.g., daisies ↔ daisies, roses ↔ roses)

🏗️ Model Architecture
Encoder: Pretrained MobileNetV2 (frozen) as a feature extractor.

Siamese Network: Takes two images as input, computes L1 distance between their embeddings, and predicts similarity score (0 or 1).

Distance Metric: L1 distance between feature vectors

Embedding Similarity: Cosine similarity for retrieval

🧪 Evaluation Metric
Precision@K: Measures the fraction of top-K retrieved images that belong to the same class as the query.

Example: Precision@5 = 0.80 → 4 of top 5 are same-class images

📊 Results
Metric	Value
Precision@5	70–85%
Epochs	10
Optimizer	Adam

📌 Key Features
✅ Uses pretrained MobileNetV2 for fast and accurate feature extraction

✅ Data augmentation to improve generalization

✅ Cosine similarity-based retrieval

✅ Visual and metric-based evaluation

✅ Easily extendable to other datasets
