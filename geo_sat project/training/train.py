import os
import gc
import json
import logging
import random
import numpy as np
os.environ["KMP_DUPLICATE_LIB_OK"] = "TRUE"
import torch
import torch.nn as nn
import torch.optim as optim
from torch.amp import GradScaler, autocast
from torch.optim.lr_scheduler import CosineAnnealingLR

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Import configurations
import training.config as cfg
from training.model import get_model
from training.dataset import get_data_loaders

def set_seed(seed):
    random.seed(seed)
    np.random.seed(seed)
    torch.manual_seed(seed)
    if torch.cuda.is_available():
        torch.cuda.manual_seed_all(seed)

def save_checkpoint(model, optimizer, scheduler, epoch, best_val_loss, history, model_name, path):
    checkpoint = {
        'epoch': epoch,
        'model_state_dict': model.state_dict(),
        'optimizer_state_dict': optimizer.state_dict(),
        'scheduler_state_dict': scheduler.state_dict() if scheduler else None,
        'best_val_loss': best_val_loss,
        'history': history,
        'model_name': model_name
    }
    torch.save(checkpoint, path)
    logger.info(f"Checkpoint saved to {path}")

def load_checkpoint(path, model, optimizer=None, scheduler=None):
    if not os.path.exists(path):
        logger.warning(f"No checkpoint found at {path}")
        return 0, float('inf'), []
    
    checkpoint = torch.load(path, map_location=cfg.DEVICE)
    model.load_state_dict(checkpoint['model_state_dict'])
    if optimizer and 'optimizer_state_dict' in checkpoint:
        optimizer.load_state_dict(checkpoint['optimizer_state_dict'])
    if scheduler and checkpoint.get('scheduler_state_dict'):
        scheduler.load_state_dict(checkpoint['scheduler_state_dict'])
        
    logger.info(f"Loaded checkpoint from {path} (Epoch {checkpoint['epoch']})")
    return checkpoint['epoch'], checkpoint['best_val_loss'], checkpoint.get('history', [])

def train_epoch(model, dataloader, criterion, optimizer, scaler, device):
    model.train()
    running_loss = 0.0
    correct = 0
    total = 0
    
    for inputs, labels in dataloader:
        inputs, labels = inputs.to(device), labels.to(device)
        
        optimizer.zero_grad()
        
        # Mixed Precision
        with autocast('cuda', enabled=device=="cuda"):
            outputs = model(inputs)
            loss = criterion(outputs, labels)
            
        if scaler:
            scaler.scale(loss).backward()
            # Gradient clipping
            scaler.unscale_(optimizer)
            torch.nn.utils.clip_grad_norm_(model.parameters(), max_norm=1.0)
            scaler.step(optimizer)
            scaler.update()
        else:
            loss.backward()
            torch.nn.utils.clip_grad_norm_(model.parameters(), max_norm=1.0)
            optimizer.step()
            
        running_loss += loss.item() * inputs.size(0)
        _, predicted = outputs.max(1)
        total += labels.size(0)
        correct += predicted.eq(labels).sum().item()
        
        # Aggressive memory management for Colab Free
        del inputs, labels, outputs, loss
        
    epoch_loss = running_loss / total
    epoch_acc = correct / total
    return epoch_loss, epoch_acc

def validate_epoch(model, dataloader, criterion, device):
    model.eval()
    running_loss = 0.0
    correct = 0
    total = 0
    
    with torch.no_grad():
        for inputs, labels in dataloader:
            inputs, labels = inputs.to(device), labels.to(device)
            
            with autocast('cuda', enabled=device=="cuda"):
                outputs = model(inputs)
                loss = criterion(outputs, labels)
                
            running_loss += loss.item() * inputs.size(0)
            _, predicted = outputs.max(1)
            total += labels.size(0)
            correct += predicted.eq(labels).sum().item()
            
            del inputs, labels, outputs, loss
            
    epoch_loss = running_loss / total
    epoch_acc = correct / total
    return epoch_loss, epoch_acc

def train_model(data_dir, model_name="resnet50", resume_from=None):
    set_seed(cfg.SEED)
    device = cfg.DEVICE
    logger.info(f"Using device: {device}")
    
    # 1. Load Data
    # Dataset.py logic automatically assigns pin_memory if torch.cuda.is_available()
    train_loader, val_loader, _ = get_data_loaders(
        dataset_path=data_dir,
        batch_size=cfg.BATCH_SIZE,
        num_workers=cfg.NUM_WORKERS
    )
    
    # 2. Setup Model
    model = get_model(model_name, num_classes=cfg.NUM_CLASSES).to(device)
    
    # 3. Setup Loss, Optimizer, Scheduler, Scaler
    criterion = nn.CrossEntropyLoss()
    optimizer = optim.AdamW(model.parameters(), lr=cfg.LEARNING_RATE, weight_decay=cfg.WEIGHT_DECAY)
    scheduler = CosineAnnealingLR(optimizer, T_max=cfg.EPOCHS)
    scaler = GradScaler() if device == "cuda" else None
    
    # Optional TensorBoard
    writer = None
    if getattr(cfg, 'USE_TENSORBOARD', False):
        from torch.utils.tensorboard import SummaryWriter
        writer = SummaryWriter(log_dir=os.path.join(cfg.MODELS_DIR, 'runs'))
    
    start_epoch = 0
    best_val_loss = float('inf')
    history = []
    
    # Checkpoint logic
    checkpoint_path = os.path.join(cfg.MODELS_DIR, f"{model_name}_best.pt")
    if resume_from:
        start_epoch, best_val_loss, history = load_checkpoint(resume_from, model, optimizer, scheduler)
        
    patience = 5
    patience_counter = 0
    
    # 4. Training Loop
    for epoch in range(start_epoch, cfg.EPOCHS):
        logger.info(f"Epoch {epoch+1}/{cfg.EPOCHS}")
        
        train_loss, train_acc = train_epoch(model, train_loader, criterion, optimizer, scaler, device)
        val_loss, val_acc = validate_epoch(model, val_loader, criterion, device)
        
        if scheduler:
            scheduler.step()
            
        logger.info(f"Train Loss: {train_loss:.4f} | Train Acc: {train_acc:.4f} | Val Loss: {val_loss:.4f} | Val Acc: {val_acc:.4f}")
        
        epoch_stats = {
            'epoch': epoch + 1,
            'train_loss': train_loss, 'train_acc': train_acc,
            'val_loss': val_loss, 'val_acc': val_acc
        }
        history.append(epoch_stats)
        
        if writer:
            writer.add_scalar('Loss/Train', train_loss, epoch)
            writer.add_scalar('Loss/Val', val_loss, epoch)
            writer.add_scalar('Accuracy/Train', train_acc, epoch)
            writer.add_scalar('Accuracy/Val', val_acc, epoch)
            
        # Checkpointing (save ONLY best model)
        if val_loss < best_val_loss:
            best_val_loss = val_loss
            patience_counter = 0
            save_checkpoint(model, optimizer, scheduler, epoch + 1, best_val_loss, history, model_name, checkpoint_path)
        else:
            patience_counter += 1
            
        # Memory Management
        if device == "cuda":
            torch.cuda.empty_cache()
        gc.collect()
        
        # Early Stopping
        if patience_counter >= patience:
            logger.info("Early stopping triggered!")
            break
            
    if writer:
        writer.close()
        
    # Save training history
    with open(os.path.join(cfg.MODELS_DIR, f"{model_name}_history.json"), 'w') as f:
        json.dump(history, f, indent=4)
        
    return checkpoint_path

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Train Phase 3 Model")
    parser.add_argument("--data_dir", type=str, required=True, help="Path to preprocessed dataset")
    parser.add_argument("--model", type=str, default="resnet50", choices=["resnet50", "cnn"], help="Model architecture")
    parser.add_argument("--resume", type=str, default=None, help="Path to checkpoint to resume from")
    
    args = parser.parse_args()
    train_model(args.data_dir, args.model, args.resume)
