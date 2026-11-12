import re
import pandas as pd

def clean_text(text):
    if not isinstance(text, str):
        return ""
    text = re.sub(r"http\S+", "", text)
    text = re.sub(r"www\.\S+", "", text)
    text = re.sub(r"```.*?```", "", text, flags=re.DOTALL)
    text = re.sub(r"`.*?`", "", text)
    text = re.sub(r"[#*>\-]", "", text)
    text = re.sub(r"\s+", " ", text)
    return text.strip()

def clean_dataframe(df):
    df = df.copy()
    if "content" in df.columns:
        df["content"] = df["content"].apply(clean_text)
        df = df[df["content"].str.len() > 5]
    df = df.drop_duplicates().reset_index(drop=True)
    return df
