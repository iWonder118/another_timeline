import MeCab
import pandas as pd
import markovify

import json


def generate_tw_hz(event, context):
    try:
        # base_csv = "./get_tw_hz/result/tw_hz_no_lf.csv"  # local
        base_csv = "./tw_hz_no_lf.csv"  # dev
        df = pd.read_csv(base_csv)

        mecab = MeCab.Tagger("-Owakati")

        owakati_tweet = ""
        for tweet in df.iloc[:9900, 2]:
            owakati_tweet += " ".join(mecab.parse(tweet).split()) + "\n"

        model = markovify.NewlineText(owakati_tweet)
        sentence = model.make_sentence()

        # 文章は分かち書きで出力されるのでスペースをトリミング
        return {
            "statusCode": 200,
            "headers": {
                "Content-Type": "application/json",
                "Access-Control-Allow-Origin": "*"
            },
            "body": json.dumps({"text": sentence.replace(" ", "")}),
            "isBase64Encoded": False
        }
    except Exception as e:
        print(e)
