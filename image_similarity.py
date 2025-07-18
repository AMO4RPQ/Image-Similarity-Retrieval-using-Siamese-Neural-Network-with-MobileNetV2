# -*- coding: utf-8 -*-
"""Image_Similarity.ipynb

Automatically generated by Colab.

Original file is located at
    https://colab.research.google.com/drive/1TCECWpl77sj_wm2UbnBP5JI2uNiywXRD

**STEP 1: IMPORT LIBRARIES**
"""

# Commented out IPython magic to ensure Python compatibility.
# %matplotlib inline
import tensorflow as tf
import tensorflow_datasets as tfds
import numpy as np
import matplotlib.pyplot as plt
from sklearn.metrics.pairwise import cosine_similarity
import random

"""**STEP 2: LOAD THE DATASET (tf_flowers)**"""

IMG_SIZE = (100, 100)
BATCH_SIZE = 32
AUTOTUNE = tf.data.AUTOTUNE

(ds_raw,), ds_info = tfds.load("tf_flowers", split=["train"], as_supervised=True, with_info=True)

"""**STEP 3: DATA AUGMENTATION + PREPROCESSING**"""

data_augmentation = tf.keras.Sequential([
    tf.keras.layers.RandomFlip("horizontal"),
    tf.keras.layers.RandomRotation(0.1),
    tf.keras.layers.RandomZoom(0.1),
])

def preprocess(image, label):
    image = tf.image.resize(image, IMG_SIZE) / 255.0
    return image, label

def preprocess_aug(image, label):
    image = tf.image.resize(image, IMG_SIZE) / 255.0
    image = data_augmentation(image)
    return image, label

ds_preprocessed = ds_raw.map(preprocess_aug).cache().batch(BATCH_SIZE).prefetch(AUTOTUNE)

"""**STEP 4: EXTRACT IMAGES AND LABELS**"""

images, labels = [], []
for img_batch, lbl_batch in ds_preprocessed:
    images.extend(img_batch.numpy())
    labels.extend(lbl_batch.numpy())

images = np.array(images)
labels = np.array(labels)

print(f"Loaded {len(images)} images.")

"""**STEP 5: CREATE POSITIVE & NEGATIVE PAIRS**"""

def make_pairs(images, labels):
    pair_images, pair_labels = [], []
    label_to_indices = {label: np.where(labels == label)[0] for label in np.unique(labels)}

    for idx, anchor_img in enumerate(images):
        anchor_label = labels[idx]

        # Positive
        pos_idx = idx
        while pos_idx == idx:
            pos_idx = random.choice(label_to_indices[anchor_label])
        positive_img = images[pos_idx]

        # Negative
        neg_label = random.choice([l for l in label_to_indices if l != anchor_label])
        neg_idx = random.choice(label_to_indices[neg_label])
        negative_img = images[neg_idx]

        # Append pairs
        pair_images.append([anchor_img, positive_img])
        pair_labels.append(1)
        pair_images.append([anchor_img, negative_img])
        pair_labels.append(0)

    return np.array(pair_images), np.array(pair_labels)

pairs, pair_labels = make_pairs(images, labels)
print(f"Generated {len(pairs)} image pairs.")

"""**STEP 6: BUILD ENCODER (MobileNetV2)**"""

def build_encoder():
    base_model = tf.keras.applications.MobileNetV2(input_shape=(*IMG_SIZE, 3),
                                                   include_top=False,
                                                   weights='imagenet')
    base_model.trainable = False

    model = tf.keras.Sequential([
        base_model,
        tf.keras.layers.GlobalAveragePooling2D(),
        tf.keras.layers.Dense(128, activation='relu')
    ])
    return model

encoder = build_encoder()

"""**STEP 7: BUILD SIAMESE NETWORK**"""

input_a = tf.keras.Input(shape=(*IMG_SIZE, 3))
input_b = tf.keras.Input(shape=(*IMG_SIZE, 3))

embedding_a = encoder(input_a)
embedding_b = encoder(input_b)

l1_distance = tf.keras.layers.Lambda(lambda tensors: tf.abs(tensors[0] - tensors[1]))([embedding_a, embedding_b])
output = tf.keras.layers.Dense(1, activation='sigmoid')(l1_distance)

siamese_model = tf.keras.Model(inputs=[input_a, input_b], outputs=output)
siamese_model.compile(loss='binary_crossentropy', optimizer='adam', metrics=['accuracy'])
siamese_model.summary()

"""**STEP 8: TRAIN THE MODEL**"""

history = siamese_model.fit(
    [pairs[:, 0], pairs[:, 1]],
    pair_labels,
    batch_size=32,
    epochs=10,
    validation_split=0.2
)

"""**STEP 9: GENERATE NORMALIZED EMBEDDINGS**"""

def get_embeddings(images):
    raw_embeds = encoder.predict(images, batch_size=32)
    norm_embeds = raw_embeds / np.linalg.norm(raw_embeds, axis=1, keepdims=True)
    return norm_embeds

embeddings = get_embeddings(images)

"""**STEP 10: PRECISION@K EVALUATION**"""

def precision_at_k(embeddings, labels, k=5):
    similarity_matrix = cosine_similarity(embeddings)
    num_samples = embeddings.shape[0]
    correct_counts = []

    for idx in range(num_samples):
        true_label = labels[idx]
        similarity_matrix[idx, idx] = -1  # avoid self-match
        top_k_indices = np.argsort(similarity_matrix[idx])[::-1][:k]
        top_k_labels = labels[top_k_indices]
        correct = np.sum(top_k_labels == true_label)
        correct_counts.append(correct / k)

    return np.mean(correct_counts)

k = 5
precision = precision_at_k(embeddings, labels, k)
print(f"Precision@{k}: {precision*100:.2f}%")

"""**STEP 11: VISUALIZATION FUNCTION**"""

def get_top_k_similar(target_idx, k=5):
    target_embedding = embeddings[target_idx:target_idx+1]
    similarities = cosine_similarity(target_embedding, embeddings)[0]
    similarities[target_idx] = -1
    return np.argsort(similarities)[::-1][:k]

def plot_similar_images(query_idx, k=5):
    top_k = get_top_k_similar(query_idx, k=k)
    plt.figure(figsize=(15, 3))

    plt.subplot(1, k + 1, 1)
    plt.imshow(images[query_idx])
    plt.title("Query")
    plt.axis("off")

    for i, idx in enumerate(top_k):
        plt.subplot(1, k + 1, i + 2)
        plt.imshow(images[idx])
        plt.title(f"Rank {i+1}")
        plt.axis("off")

    plt.tight_layout()
    plt.show()

# Show results for a random query
random_idx = random.randint(0, len(images)-1)
plot_similar_images(random_idx)

