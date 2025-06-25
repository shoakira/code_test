# Named entity recognition
import spacy

# Load the GiNZA model
nlp = spacy.load("ja_core_news_sm")


def extract_named_entities(text):
    # Process the text
    doc = nlp(text)
    # Extract named entities
    entities = [(ent.text, ent.label_) for ent in doc.ents]
    return entities


# Example usage
if __name__ == "__main__":
    japanese_text = "東京都は日本の首都です。"
    entities = extract_named_entities(japanese_text)
    print("Named Entities:", entities)
