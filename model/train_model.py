# train_model.py
# This script trains a T5 model to generate SQL queries.

import pandas as pd
import torch
from torch.utils.data import Dataset, DataLoader
from transformers import T5ForConditionalGeneration, T5Tokenizer
from torch.optim import AdamW

device = "cuda" if torch.cuda.is_available() else "cpu"
print(f"Using device: {device}")

# --- 1. Load Data and Tokenizer ---
try:
    df = pd.read_csv("training_data.csv")
    print("✅ Training data loaded.")
except FileNotFoundError:
    print("❌ Error: 'training_data.csv' not found. Please run 'generate_training_data.py' first.")
    exit()

# Load a pre-trained T5 model and its tokenizer from Hugging Face
try:
    tokenizer = T5Tokenizer.from_pretrained("t5-small")
    model = T5ForConditionalGeneration.from_pretrained("t5-small").to(device)
    print("✅ T5-small model and tokenizer loaded.")
except Exception as e:
    print(f"❌ Error loading model or tokenizer: {e}")
    print("Please ensure you have an active internet connection to download the model.")
    exit()

# --- 2. Tokenize the Data ---
# The tokenizer will convert our text data into numerical IDs that the model understands.
tokenized_inputs = tokenizer(list(df['input']), return_tensors="pt", padding=True, truncation=True)
tokenized_outputs = tokenizer(list(df['output']), return_tensors="pt", padding=True, truncation=True)

# Set the labels for the model. We use the output tokens as the target.
labels = tokenized_outputs.input_ids
labels[labels == tokenizer.pad_token_id] = -100 # Important: tell the model to ignore padding in the loss calculation

# --- 3. Prepare for Training ---
# Create a custom dataset class to handle our data format.
class SQLDataset(Dataset):
    def __init__(self, encodings, labels):
        self.encodings = encodings
        self.labels = labels
    def __getitem__(self, idx):
        item = {key: val[idx] for key, val in self.encodings.items()}
        item['labels'] = self.labels[idx]
        return item
    def __len__(self):
        return len(self.labels)

# Create the dataset and dataloader
dataset = SQLDataset(tokenized_inputs, labels)
# ⚙️ IMPORTANT CHANGE: We've reduced the batch size to 2 to solve the memory error.
dataloader = DataLoader(dataset, batch_size=2)
print(f"Using a batch size of {dataloader.batch_size} to conserve memory.")

# Set up the optimizer. AdamW is a standard choice.
optimizer = AdamW(model.parameters(), lr=1e-4)

# --- 4. The Training Loop ---
model.train() # Set the model to training mode
print("🚀 Starting training...")

for epoch in range(3):  # Train for 3 full passes over the dataset
    print(f"--- Epoch {epoch + 1}/{3} ---")

    # Use enumerate to get a count of the batches processed
    for batch_num, batch in enumerate(dataloader):
        optimizer.zero_grad() # Clear previous gradients
        input_ids = batch['input_ids'].to(device)
        attention_mask = batch['attention_mask'].to(device)
        labels = batch['labels'].to(device)
        
        # Forward Pass: The model makes a prediction
        outputs = model(input_ids=input_ids, attention_mask=attention_mask, labels=labels)
        
        # Calculate Loss: The loss tells us how wrong the model's prediction was
        loss = outputs.loss
        
        # Backward Pass: The loss is sent back through the model to figure out what to adjust
        loss.backward()
        
        # Optimizer Step: The optimizer adjusts the model's weights to reduce the loss
        optimizer.step()
        
        # Print a progress update every 500 batches
        if (batch_num + 1) % 500 == 0:
            print(f"Processed batch {batch_num + 1}/{len(dataloader)}. Current Loss: {loss.item():.4f}")

    print(f"🎉 Epoch {epoch + 1} complete. Final loss for this epoch: {loss.item():.4f}")

# --- 5. Save the Trained Model ---
# This is a critical step! It saves your trained model and its tokenizer to a folder.
print("✅ Saving trained model...")
model.save_pretrained("./trained_sql_model")
tokenizer.save_pretrained("./trained_sql_model")

print("✨ Training successful! Model saved to the 'trained_sql_model' directory.")
print("You can now proceed to run 'api_with_model.py'.")
