from transformers import AutoTokenizer, AutoModelForSequenceClassification
import os

def download_model():
    model_name = "ealvaradob/bert-finetuned-phishing"
    print(f"Downloading model: {model_name}...")
    
    # This will download and cache the model in ~/.cache/huggingface
    tokenizer = AutoTokenizer.from_pretrained(model_name)
    model = AutoModelForSequenceClassification.from_pretrained(model_name)
    
    print("Model downloaded and cached successfully.")
    
    # Save to a specific local directory
    local_path = "./models/bert_phishing"
    tokenizer.save_pretrained(local_path)
    model.save_pretrained(local_path)
    print(f"Model saved to {local_path}")

if __name__ == "__main__":
    download_model()
