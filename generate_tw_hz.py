import MeCab
import pandas as pd
import markovify


df = pd.read_csv("./get_tw_hz/result/tw_hz_no_lf.csv")

mecab = MeCab.Tagger("-Owakati")

owakati_tweet = ""
for tweet in df.iloc[:9900, 2]:
    owakati_tweet += " ".join(mecab.parse(tweet).split()) + "\n"

model = markovify.NewlineText(owakati_tweet)
sentence = model.make_sentence()

# 文章は分かち書きで出力されるのでスペースをトリミング
print(sentence.replace(" ", ""))
