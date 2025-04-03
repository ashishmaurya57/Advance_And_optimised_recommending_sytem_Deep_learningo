from transformers import pipeline
import os

# Force Hugging Face to use PyTorch
os.environ["TRANSFORMERS_NO_TF"] = "1"

def analyze_sentiment(product_data):
    # Load a specific pre-trained model for sentiment analysis
    sentiment_analyzer = pipeline('sentiment-analysis', model='distilbert-base-uncased-finetuned-sst-2-english', framework='pt')  # Use PyTorch backend

    # Apply sentiment analysis to the 'pdes' column
    product_data['sentiment'] = product_data['pdes'].apply(lambda x: sentiment_analyzer(x)[0]['label'])
    return product_data