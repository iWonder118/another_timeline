import MeCab
import pandas as pd
import markovify


df = pd.read_csv("./result/tw_hz_no_lf.csv")

mecab = MeCab.Tagger("-Owakati")

owakati_tweet = ""
for tweet in df["text"]:
    owakati_tweet += " ".join(mecab.parse(tweet).split()) + "\n"

model = markovify.NewlineText(owakati_tweet)
sentence = model.make_sentence()

# 文章は分かち書きで出力されるのでスペースをトリミング
print(sentence.replace(" ", ""))
