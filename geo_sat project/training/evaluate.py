import os
import json
import logging
import numpy as np
import matplotlib.pyplot as plt
os.environ["KMP_DUPLICATE_LIB_OK"] = "TRUE"
import torch
from sklearn.metrics import accuracy_score, precision_recall_fscore_support, classification_report, confusion_matrix, roc_curve, auc
from sklearn.preprocessing import label_binarize
import seaborn as sns

import training.config as cfg
from training.model import get_model
from training.dataset import get_data_loaders

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def plot_history(history_file, save_dir):
    if not os.path.exists(history_file):
        logger.warning(f"History file {history_file} not found.")
        return
        
    with open(history_file, 'r') as f:
        history = json.load(f)
        
    epochs = [x['epoch'] for x in history]
    train_loss = [x['train_loss'] for x in history]
    val_loss = [x['val_loss'] for x in history]
    train_acc = [x['train_acc'] for x in history]
    val_acc = [x['val_acc'] for x in history]
    
    plt.figure(figsize=(12, 5))
    
    # Loss plot
    plt.subplot(1, 2, 1)
    plt.plot(epochs, train_loss, label='Train Loss')
    plt.plot(epochs, val_loss, label='Val Loss')
    plt.title('Training and Validation Loss')
    plt.xlabel('Epoch')
    plt.ylabel('Loss')
    plt.legend()
    
    # Acc plot
    plt.subplot(1, 2, 2)
    plt.plot(epochs, train_acc, label='Train Acc')
    plt.plot(epochs, val_acc, label='Val Acc')
    plt.title('Training and Validation Accuracy')
    plt.xlabel('Epoch')
    plt.ylabel('Accuracy')
    plt.legend()
    
    plt.tight_layout()
    plt.savefig(os.path.join(save_dir, 'training_history.png'))
    plt.close()

def evaluate_model(model_path, data_dir, model_name="resnet50"):
    device = cfg.DEVICE
    logger.info(f"Evaluating on {device}")
    
    # Load data
    _, _, test_loader = get_data_loaders(
        dataset_path=data_dir,
        batch_size=cfg.BATCH_SIZE,
        num_workers=cfg.NUM_WORKERS
    )
    
    classes = test_loader.dataset.dataset.classes
    num_classes = len(classes)
    
    # Setup model
    model = get_model(model_name, num_classes=num_classes)
    checkpoint = torch.load(model_path, map_location=device)
    model.load_state_dict(checkpoint['model_state_dict'])
    model.to(device)
    model.eval()
    
    all_preds = []
    all_labels = []
    all_probs = []
    
    with torch.no_grad():
        for inputs, labels in test_loader:
            inputs = inputs.to(device)
            outputs = model(inputs)
            probs = torch.softmax(outputs, dim=1)
            
            _, preds = torch.max(outputs, 1)
            
            all_preds.extend(preds.cpu().numpy())
            all_labels.extend(labels.cpu().numpy())
            all_probs.extend(probs.cpu().numpy())
            
            del inputs, outputs, probs
            
    # Metrics
    all_labels = np.array(all_labels)
    all_preds = np.array(all_preds)
    all_probs = np.array(all_probs)
    
    acc = accuracy_score(all_labels, all_preds)
    precision, recall, f1, _ = precision_recall_fscore_support(all_labels, all_preds, average='weighted', zero_division=0)
    
    logger.info(f"Accuracy: {acc:.4f}")
    logger.info(f"Precision: {precision:.4f} | Recall: {recall:.4f} | F1: {f1:.4f}")
    
    # Classification Report
    report = classification_report(all_labels, all_preds, labels=range(len(classes)), target_names=classes, zero_division=0)
    with open(os.path.join(cfg.MODELS_DIR, 'classification_report.txt'), 'w') as f:
        f.write(report)
        
    # Confusion Matrix
    cm = confusion_matrix(all_labels, all_preds)
    plt.figure(figsize=(10, 8))
    sns.heatmap(cm, annot=True, fmt='d', cmap='Blues', xticklabels=classes, yticklabels=classes)
    plt.title('Confusion Matrix')
    plt.xlabel('Predicted')
    plt.ylabel('True')
    plt.tight_layout()
    plt.savefig(os.path.join(cfg.MODELS_DIR, 'confusion_matrix.png'))
    plt.close()
    
    # ROC Curve (One-vs-Rest)
    labels_bin = label_binarize(all_labels, classes=range(num_classes))
    plt.figure(figsize=(10, 8))
    for i in range(num_classes):
        fpr, tpr, _ = roc_curve(labels_bin[:, i], all_probs[:, i])
        roc_auc = auc(fpr, tpr)
        plt.plot(fpr, tpr, lw=2, label=f'Class {classes[i]} (AUC = {roc_auc:.2f})')
        
    plt.plot([0, 1], [0, 1], color='navy', lw=2, linestyle='--')
    plt.xlim([0.0, 1.0])
    plt.ylim([0.0, 1.05])
    plt.xlabel('False Positive Rate')
    plt.ylabel('True Positive Rate')
    plt.title('ROC Curve (One-vs-Rest)')
    plt.legend(loc="lower right")
    plt.tight_layout()
    plt.savefig(os.path.join(cfg.MODELS_DIR, 'roc_curve.png'))
    plt.close()
    
    # Plot history if exists
    history_file = os.path.join(cfg.MODELS_DIR, f"{model_name}_history.json")
    plot_history(history_file, cfg.MODELS_DIR)

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Evaluate Phase 3 Model")
    parser.add_argument("--model_path", type=str, required=True, help="Path to best checkpoint .pt file")
    parser.add_argument("--data_dir", type=str, required=True, help="Path to preprocessed dataset")
    parser.add_argument("--model", type=str, default="resnet50", choices=["resnet50", "cnn"], help="Model architecture")
    
    args = parser.parse_args()
    evaluate_model(args.model_path, args.data_dir, args.model)
