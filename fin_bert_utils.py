from transformers import AutoTokenizer, AutoModelForSequenceClassification
import torch
import os
device = "cuda:0" if torch.cuda.is_available() else "cpu"
from transformers import pipeline
tokenizer = AutoTokenizer.from_pretrained("ProsusAI/finbert")
model = AutoModelForSequenceClassification.from_pretrained("ProsusAI/finbert").to(device)
labels = ["positive", "negative", "neutral"]
os.environ["TOKENIZERS_PARALLELISM"] = "false"

def estimate_sentiment_batch(news):
    """
    Estimates the sentiment of a batch of news articles.

    Parameters:
    - news (list): A list of news articles.

    Returns:
    - probability (float): The probability of the estimated sentiment.
    - sentiment (str): The estimated sentiment.

    If the input list is empty, the function returns 0 as the probability and the last label as the sentiment.
    """
    if news:
        tokens = tokenizer(news, return_tensors="pt", padding=True).to(device)

        result = model(tokens["input_ids"], attention_mask=tokens["attention_mask"])[
            "logits"
        ]
        result = torch.nn.functional.softmax(torch.sum(result, 0), dim=-1)
        probability = result[torch.argmax(result)]
        sentiment = labels[torch.argmax(result)]
        return probability, sentiment
    else:
        return 0, labels[-1]

def estimate_sentiment_single(news):
    if news:
        pipe = pipeline("text-classification", model="ProsusAI/finbert")
        sentiment  = pipe(news)
        return sentiment[0]['label']
    else:
        return 'neutral'


if __name__ == "__main__":
    tensor, sentiment = estimate_sentiment_batch(['markets responded negatively to the news!','traders were displeased!'])
    print(tensor, sentiment)
    print(estimate_sentiment_single('markets responded negatively to the news!'))