import os
import numpy as np
import tensorflow as tf
from tensorflow.keras.applications import ResNet50
from tensorflow.keras.preprocessing.image import load_img, img_to_array
from tensorflow.keras.applications.resnet50 import preprocess_input
from object_detection.utils import ops as utils_ops
from PIL import Image
import faiss

# Patch TensorFlow v1 ops
utils_ops.tf = tf.compat.v1
tf.gfile = tf.io.gfile

RESNET_INPUT_SHAPE = (224, 224, 3)
RESNET_MODEL = ResNet50(weights='imagenet', include_top=False, input_shape=RESNET_INPUT_SHAPE)
RESNET_MODEL.trainable = False

def load_image(image_path, target_size):
    """Load and preprocess an image."""
    img = load_img(image_path, target_size=target_size)
    img_array = img_to_array(img)
    img_array = np.expand_dims(img_array, axis=0) 
    return preprocess_input(img_array)

def run_inference_for_single_image(model, image_path):
    image = np.array(Image.open(image_path))
    input_tensor = tf.convert_to_tensor(image)[tf.newaxis, ...] 
    model_fn = model.signatures['serving_default']
    output_dict = model_fn(input_tensor)

    num_detections = int(output_dict.pop('num_detections'))
    output_dict = {key: value[0, :num_detections].numpy() for key, value in output_dict.items()}
    output_dict['detection_classes'] = output_dict['detection_classes'].astype(np.int64)

    if 'detection_masks' in output_dict:
        detection_masks_reframed = utils_ops.reframe_box_masks_to_image_masks(
            output_dict['detection_masks'], output_dict['detection_boxes'],
            image.shape[0], image.shape[1])
        output_dict['detection_masks_reframed'] = tf.cast(detection_masks_reframed > 0.5, tf.uint8).numpy()

    return output_dict

def detect_clothes(model, image_path):
    """Detect clothing in an image and crop it based on bounding box."""
    output_dict = run_inference_for_single_image(model, image_path)
    image = np.array(Image.open(image_path))

    scores = output_dict['detection_scores']
    if len(scores) == 0 or max(scores) < 0.5:
        raise ValueError("No bounding box with sufficient confidence found.")

    highest_score_idx = np.argmax(scores)
    box = output_dict['detection_boxes'][highest_score_idx]
    x1, y1, x2, y2 = (
        int(box[1] * image.shape[1]),
        int(box[0] * image.shape[0]),
        int(box[3] * image.shape[1]),
        int(box[2] * image.shape[0]),
    )
    return image[y1:y2, x1:x2]

def extract_image_features(image_path):
    img_array = load_image(image_path, target_size=RESNET_INPUT_SHAPE[:2])
    features = RESNET_MODEL.predict(img_array).flatten()
    features = features / np.linalg.norm(features)
    return features

def search_similar_images(image_path, index_file, top_k=20):
    if not os.path.exists(index_file):
        raise FileNotFoundError(f"Faiss index file '{index_file}' not found.")

    index = faiss.read_index(index_file)

    features = extract_image_features(image_path).astype(np.float32)
    features = features / np.linalg.norm(features)
    features = features.reshape(1, -1)

    distances, indices = index.search(features, top_k)

    similarity_scores = distances 
    
    return similarity_scores, indices
