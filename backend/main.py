from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from PIL import Image
import io
import base64
import torch
from efficientnet_pytorch import EfficientNet
import torchvision.transforms as transforms
import torch.nn.functional as F

app = FastAPI()

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class ImageData(BaseModel):
    image: str  # Base64-encoded image

# Load model
device = torch.device('cpu')
model = EfficientNet.from_name('efficientnet-b0')
model._fc = torch.nn.Linear(model._fc.in_features, 4)
model.load_state_dict(torch.load('model/sign_language_model (1).pth', map_location=torch.device('cpu')))
model = model.to(device)
model.eval()

# Define transforms
transform = transforms.Compose([
    transforms.Resize((224, 224)),
    transforms.ToTensor(),
    transforms.Normalize([0.485, 0.456, 0.406], [0.229, 0.224, 0.225])
])

# Class names (assumed order from ImageFolder)
class_names = ['Dhanyabaad', 'Ghar', 'Ma', 'Namaskaar']

@app.post("/predict")
async def predict_sign(data: ImageData):
    try:
        # Decode base64 image
        image_data = base64.b64decode(data.image.split(",")[1])
        image = Image.open(io.BytesIO(image_data)).convert('RGB')
        
        # Preprocess image
        input_tensor = transform(image).unsqueeze(0).to(device)
        
        # Run inference
        with torch.no_grad():
            outputs = model(input_tensor)
            probabilities = F.softmax(outputs, dim=1)[0]  # Get probabilities
            confidence, predicted = torch.max(probabilities, 0)
            confidence_score = confidence.item() * 100  # Convert to percentage
            
            # Check confidence threshold
            if confidence_score < 80:
                return {"sign": "", "message": "Sign not recognized—please try one of the supported signs!"}
            
            pred_class = class_names[predicted.item()]
            return {"sign": pred_class, "message": "Prediction successful!"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error processing image: {str(e)}")

@app.get("/")
async def root():
    return {"message": "Sign Language Recognition Backend"}