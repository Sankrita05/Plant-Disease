import os
from PIL import Image, ImageStat
import torch
from torchvision import transforms
from PIL import Image
import json
from core.model_architecture import ResNet9
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
classes = ['Apple___Apple_scab', 'Apple___Black_rot', 'Apple___Cedar_apple_rust', 'Apple___healthy', 'Blueberry___healthy', 'Cherry_(including_sour)___healthy', 'Cherry_(including_sour)___Powdery_mildew', 'Corn_(maize)___Cercospora_leaf_spot Gray_leaf_spot', 'Corn_(maize)___Common_rust_', 'Corn_(maize)___healthy', 'Corn_(maize)___Northern_Leaf_Blight', 'Grape___Black_rot', 'Grape___Esca_(Black_Measles)', 'Grape___healthy', 'Grape___Leaf_blight_(Isariopsis_Leaf_Spot)', 'Orange___Haunglongbing_(Citrus_greening)', 'Peach___Bacterial_spot', 'Peach___healthy', 'Pepper,_bell___Bacterial_spot', 'Pepper,_bell___healthy', 'Potato___Early_blight', 'Potato___healthy', 'Potato___Late_blight', 'Raspberry___healthy', 'Soybean___healthy', 'Squash___Powdery_mildew', 'Strawberry___healthy', 'Strawberry___Leaf_scorch', 'Tomato___Bacterial_spot', 'Tomato___Early_blight', 'Tomato___healthy', 'Tomato___Late_blight', 'Tomato___Leaf_Mold', 'Tomato___Septoria_leaf_spot', 'Tomato___Spider_mites Two-spotted_spider_mite', 'Tomato___Target_Spot', 'Tomato___Tomato_mosaic_virus', 'Tomato___Tomato_Yellow_Leaf_Curl_Virus'] # example class names

def is_image_quality_sufficient(image_path, min_resolution=(224, 224), min_brightness=40):
    try:
        img = Image.open(image_path)
        
        # Check resolution
        if img.size[0] < min_resolution[0] or img.size[1] < min_resolution[1]:
            return False

        # Check brightness
        stat = ImageStat.Stat(img.convert('L'))  # convert to grayscale
        brightness = stat.mean[0]
        if brightness < min_brightness:
            return False

        return True
    except Exception:
        return False



# Load model
def load_model():
    model = ResNet9(3, len(classes))
    base_dir = os.path.dirname(os.path.abspath(__file__))  # This gives the path to core/
    model_path = os.path.join(base_dir, 'model', 'plant-disease-model.pth')  # adjust if needed

    model.load_state_dict(torch.load(model_path, map_location=device))
    model.to(device)
    model.eval()
    return model

# Preprocess image
def preprocess_image(image_file):
    transform = transforms.Compose([
        transforms.Resize((256, 256)),
        transforms.ToTensor(),
    ])
    image = Image.open(image_file).convert("RGB")
    return transform(image).unsqueeze(0)  # Add batch dimension

# Predict function
def predict_image(image_tensor, model):
    image_tensor = image_tensor.to(device)
    outputs = model(image_tensor)
    _, predicted = torch.max(outputs, 1)
    return classes[predicted.item()]


def parse_prediction(prediction):
        """Helper function to parse prediction result like 'Apple___Black_rot'"""
        if not prediction:
            return {"crop": "-", "disease": "-"}
        
        # Split prediction string into crop and disease
        parts = prediction.split("___")
        crop = parts[0] if parts[0] else "-"
        disease_raw = parts[1] if len(parts) > 1 else "-"
        
        # Format disease (capitalize the first letter of each word and replace underscores)
        disease = disease_raw.replace("_", " ").title() if disease_raw != "-" else "-"
        
        return {
            "crop": crop,
            "disease": disease
        }
