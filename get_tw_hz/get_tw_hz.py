import tweepy
from time import sleep
import os
import csv
import datetime
import configparser
import urllib.error
import urllib.request

#設定値の取得
config = configparser.ConfigParser()
config.read("../conf/twitter_api_key.conf", "UTF-8")

#認証
consumer_key = config.get("default", "APIKey")
consumer_secret = config.get("default", "APIKeySecret")
access_token = config.get("default", "AccessToken")
access_token_secret = config.get("default", "AccessTokenSecret")

#Twitterオブジェクトの生成
auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
auth.set_access_token(access_token, access_token_secret)
api = tweepy.API(auth)

result_path = "result"
video_path = "{}/video".format(result_path)
photo_path = "{}/photo".format(result_path)
file_name = config.get("default", "FileName")

def download_file(url, dst_path):
    try: # URLからコンテンツをダウンロード
        with urllib.request.urlopen(url) as web_file:
            data = web_file.read()
            with open(dst_path, mode="wb") as local_file:
                local_file.write(data)
    except urllib.error.URLError as e:
        print(e)

def make_directory(dir_name="example"):
    if not os.path.exists(dir_name):
        os.mkdir(dir_name)

def over_write_csv(file_path, tweet_data=[]):
    with open(file_path, "a", newline="", encoding="utf-8") as f:
        writer = csv.writer(f, lineterminator="\n")
        if not os.path.exists(file_path):
            writer.writerow(["id","created_at","text","fav","RT","rep","place"])
        writer.writerows(tweet_data)

def main():
    #ファイルを保存するディレクトリ作成
    make_directory(result_path)
    make_directory(video_path)
    make_directory(photo_path)
    result_file = "{}/{}.csv".format(result_path, file_name)
    result_file_no_lf = "{}/{}_no_lf.csv".format(result_path, file_name)
    start_date = datetime.datetime(2009, 9, 30)
    end_date = datetime.datetime(2023, 2, 4)
    since_date = start_date
    until_date = since_date + datetime.timedelta(days=1)
    while end_date > since_date:
        tweet_data = []
        tweet_data_no_lf = []
        sratch_str = "from:hirasawa -is_retweet -RT"
        print("検索文字列 : " + sratch_str)
        #ツイート取得   
        results = tweepy.Cursor(api.search_full_archive,
                                label="development",
                                query = sratch_str,
                                fromDate=since_date.strftime("%Y%m%d%H%M"),
                                toDate=until_date.strftime("%Y%m%d%H%M")).items(100)
        since_date = since_date + datetime.timedelta(days=1)
        until_date = since_date + datetime.timedelta(days=1)
        for index, result in enumerate(results):
                try:
                    tweet_data.append([result.id,
                                    result.created_at,
                                    result.text,
                                    result.favorite_count,
                                    result.retweet_count,
                                    result.reply_count,
                                    result.place])
                    tweet_data_no_lf.append([result.id,
                                    result.created_at,
                                    result.text.replace("\n", ""),
                                    result.favorite_count,
                                    result.retweet_count,
                                    result.reply_count,
                                    result.place])
                    
                    #コンテンツ取得
                    # if hasattr(result, "extended_entities"):
                    #     media = result.extended_entities["media"]
                    #     for m in media:
                    #         #動画の時
                    #         if m["type"] == "video":
                    #             origin = [variant["url"] for variant in m["video_info"]
                    #                 ["variants"] if variant["content_type"] == "video/mp4"][0]
                    #             dst_path = "{}/{}.mp4".format(video_path, datetime.datetime.now())
                    #             download_file(origin, dst_path)
                    #         #画像の時
                    #         elif m["type"] == "photo":
                    #             img_url = result.extended_entities["media"][0]["media_url"]
                    #             dst_path = "{}/{}.png".format(photo_path, datetime.datetime.now())
                    #             download_file(img_url, dst_path)
                    #     sleep(1)
                    
                    print("now Getting Tweet: {}({})".format(result.text, index+1))
                    
                except Exception as e:
                    print(e)
        
        over_write_csv(result_file, tweet_data)
        over_write_csv(result_file_no_lf, tweet_data_no_lf)
        sleep(5)
if __name__ == "__main__":
    main()