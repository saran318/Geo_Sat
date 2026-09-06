import torch
import torch.nn as nn
from torchvision.models import resnet50, ResNet50_Weights

class BaselineCNN(nn.Module):
    """
    A simple baseline Convolutional Neural Network for 6-channel satellite imagery.
    """
    def __init__(self, num_classes=10):
        super(BaselineCNN, self).__init__()
        
        self.features = nn.Sequential(
            # Block 1
            nn.Conv2d(6, 32, kernel_size=3, padding=1),
            nn.BatchNorm2d(32),
            nn.ReLU(inplace=True),
            nn.MaxPool2d(2, 2),
            
            # Block 2
            nn.Conv2d(32, 64, kernel_size=3, padding=1),
            nn.BatchNorm2d(64),
            nn.ReLU(inplace=True),
            nn.MaxPool2d(2, 2),
            
            # Block 3
            nn.Conv2d(64, 128, kernel_size=3, padding=1),
            nn.BatchNorm2d(128),
            nn.ReLU(inplace=True),
            nn.MaxPool2d(2, 2),
            
            # Block 4
            nn.Conv2d(128, 256, kernel_size=3, padding=1),
            nn.BatchNorm2d(256),
            nn.ReLU(inplace=True),
            nn.MaxPool2d(2, 2)
        )
        
        self.global_avg_pool = nn.AdaptiveAvgPool2d((1, 1))
        
        self.classifier = nn.Sequential(
            nn.Linear(256, 128),
            nn.ReLU(inplace=True),
            nn.Dropout(0.5),
            nn.Linear(128, num_classes)
        )

    def forward(self, x):
        x = self.features(x)
        x = self.global_avg_pool(x)
        x = torch.flatten(x, 1)
        x = self.classifier(x)
        return x

def get_resnet50(num_classes=10):
    """
    Loads a pretrained ResNet50 model, modifies the input layer to accept 6 channels
    (initializing the new channels with the mean of the pretrained RGB channels),
    and replaces the final classifier. Early layers are frozen.
    """
    # Load pretrained model
    model = resnet50(weights=ResNet50_Weights.DEFAULT)
    
    # 1. Modify the first convolutional layer
    # Original: Conv2d(3, 64, kernel_size=(7, 7), stride=(2, 2), padding=(3, 3), bias=False)
    original_conv1 = model.conv1
    new_conv1 = nn.Conv2d(6, 64, kernel_size=7, stride=2, padding=3, bias=False)
    
    with torch.no_grad():
        # Copy the original RGB weights to the first 3 channels
        new_conv1.weight[:, :3, :, :] = original_conv1.weight
        
        # Initialize the next 3 channels (NIR, NDVI, NDWI) with the mean of the RGB weights
        # This provides a stable initialization based on the learned filters
        mean_weight = original_conv1.weight.mean(dim=1, keepdim=True) # shape: [64, 1, 7, 7]
        new_conv1.weight[:, 3:, :, :] = mean_weight.repeat(1, 3, 1, 1)
        
    model.conv1 = new_conv1
    
    # 2. Freeze early layers
    # We will train only the last two residual blocks (layer3 and layer4) and the classifier
    for name, param in model.named_parameters():
        if not ("layer3" in name or "layer4" in name or "fc" in name or "conv1" in name):
            param.requires_grad = False
            
    # Note: We keep conv1 trainable as it has newly initialized weights
    
    # 3. Replace the classifier
    in_features = model.fc.in_features
    model.fc = nn.Linear(in_features, num_classes)
    
    return model

def get_model(model_name="resnet50", num_classes=10):
    if model_name.lower() == "cnn":
        return BaselineCNN(num_classes=num_classes)
    elif model_name.lower() == "resnet50":
        return get_resnet50(num_classes=num_classes)
    else:
        raise ValueError(f"Unknown model name: {model_name}")
