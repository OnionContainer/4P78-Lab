import os
import cv2
import numpy as np
import tensorflow as tf
from tensorflow import keras
from tensorflow.keras.preprocessing.image import ImageDataGenerator

# Define dataset path
dataset_dir = "tetris_shapes_dataset"
image_size = (64, 64)  # Resize all images to 64x64
batch_size = 32

# Data Augmentation to improve recognition
datagen = ImageDataGenerator(
    rescale=1.0/255, 
    validation_split=0.2  # 80% training, 20% validation
)

# Load Training Data
train_data = datagen.flow_from_directory(
    dataset_dir,
    target_size=image_size,
    batch_size=batch_size,
    class_mode='categorical',
    subset='training'
)

# Load Validation Data
val_data = datagen.flow_from_directory(
    dataset_dir,
    target_size=image_size,
    batch_size=batch_size,
    class_mode='categorical',
    subset='validation'
)
