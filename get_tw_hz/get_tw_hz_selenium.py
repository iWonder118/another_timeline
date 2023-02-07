from selenium import webdriver
from selenium.webdriver.common.by import By

import os
import re
import csv
import sys
import time
import datetime
import configparser

# 設定値の取得
config = configparser.ConfigParser()
config.read("../conf/twitter_api_key.conf", "UTF-8")
result_path = "result"
file_name = config.get("default", "FileName")
twitter_base = "https://twitter.com"


class TwitterDriver:

    driver = None

    def __init__(self) -> None:
        options = webdriver.ChromeOptions()
        # ヘッドレスモードに
        # options.add_argument("--headless")
        # options.add_argument("--no-sandbox")
        # ブラウザーを起動
        self.driver = webdriver.Chrome(options=options)
        self.driver.set_window_size("1200", "1000")

    # twitterログイン
    def login(self, account, password):

        # ログインページを開く
        self.driver.get(twitter_base + "/login/")
        time.sleep(10)

        # account入力
        element_account = self.driver.find_element(By.NAME, "text")
        element_account.send_keys(account)

        # 次へボタンクリック
        element_login_next = self.driver.find_element(
            By.XPATH,
            "//*[@id='layers']/div/div/div/div/div/div/div[2]/div[2]/div/div/div[2]/div[2]/div/div/div/div[6]")
        # 画像のリンクをクリック
        element_login_next.click()
        time.sleep(5)

        # パスワード入力
        element_pass = self.driver.find_element(By.NAME, "password")
        element_pass.send_keys(password)

        # ログインボタンクリック
        element_login = self.driver.find_element(
            By.XPATH,
            "//*[@id='layers']/div/div/div/div/div/div/div[2]/div[2]/div/div/div[2]/div[2]/div[2]/div/div[1]/div/div/div")

        element_login.click()
        time.sleep(5)

    def search(self, query):
        results = []
        self.driver.get(twitter_base + query)
        time.sleep(10)
        time_line = filter(
            lambda e: e.get_attribute("data-testid") == "tweet",
            self.driver.find_elements(
                By.CLASS_NAME,
                "css-1dbjc4n"))
        for index, tweet in enumerate(time_line):
            result = {
                "id": 0,
                "created_at": "",
                "text": "",
                "favorite_count": 0,
                "retweet_count": 0,
                "reply_count": 0}

            for content in tweet.find_elements(
                    By.CSS_SELECTOR, ".css-901oao,.css-18t94o4,.css-1dbjc4n"):
                if content.get_attribute("data-testid") == "User-Names":
                    try:
                        result["id"] = content.find_element(
                            By.XPATH, ".//div[2]/div/div[3]/a").get_attribute("href")

                        result["created_at"] = content.find_element(
                            By.XPATH, ".//div[2]/div/div[3]/a/time").get_attribute("datetime")
                    except:
                        pass
                    
                elif content.get_attribute("data-testid") == "tweetText":
                    try:
                        result["text"] = content.find_element(
                            By.XPATH, ".//span").text
                    except:
                        pass
                    
                elif content.get_attribute("data-testid") == "like":
                    try:
                        result["favorite_count"] = content.find_element(
                            By.XPATH, ".//div/div[2]/span/span/span").text
                        result["favorite_count"] = int(
                            result["favorite_count"]) if not result["favorite_count"] == "" else 0
                    except:
                        pass

                elif content.get_attribute("data-testid") == "retweet":
                    try:
                        result["retweet_count"] = content.find_element(
                            By.XPATH, ".//div/div[2]/span/span").text
                        result["retweet_count"] = int(
                            result["retweet_count"]) if not result["retweet_count"] == "" else 0
                    except:
                        pass
                    
                elif content.get_attribute("data-testid") == "reply":
                    try:
                        result["reply_count"] = content.find_element(
                            By.XPATH, ".//div/div[2]/span/span/span").text
                        result["reply_count"] = int(
                            result["reply_count"]) if not result["reply_count"] == "" else 0
                    except:
                        pass

            print(
                "now Getting \ncreated_at: {}\nTweet: {}\nfavorite_count: {}\nretweet_count: {}\nreply_count: {}\n({})".format(
                    result["created_at"],
                    result["text"],
                    result["favorite_count"],
                    result["retweet_count"],
                    result["reply_count"],
                    index + 1))
            results.append(result)
        time.sleep(5)
        return results

    def close(self):
        self.driver.close()


def make_directory(dir_name="example"):
    if not os.path.exists(dir_name):
        os.mkdir(dir_name)


def over_write_csv(file_path, tweet_data=[]):
    with open(file_path, "a", newline="", encoding="utf-8") as f:
        writer = csv.writer(f, lineterminator="\n")
        if os.path.getsize(file_path) == 0:
            writer.writerow(["id", "created_at", "text", "fav", "rt", "rep"])
        writer.writerows(tweet_data)


def check_date(input):
    pattern = "\\d{4}-\\d{2}-\\d{2}"
    return re.match(pattern, input)


def main():
    args = sys.argv
    if not check_date(args[1]) and not check_date(args[2]):
        print("not Date format... (ex: yyyy-mm-dd)")
        exit(1)
    start_date = datetime.datetime.strptime(args[1], '%Y-%m-%d')
    end_date = datetime.datetime.strptime(args[2], '%Y-%m-%d')
    # ファイルを保存するディレクトリ作成
    make_directory(result_path)
    result_file = "{}/{}.csv".format(result_path, file_name)
    result_file_no_lf = "{}/{}_no_lf.csv".format(result_path, file_name)
    since_date = start_date
    until_date = since_date + datetime.timedelta(days=1)
    account = config.get("default", "Account")
    password = config.get("default", "Password")
    twitter_driver = TwitterDriver()
    twitter_driver.login(account, password)
    while end_date > since_date:
        tweet_data = []
        tweet_data_no_lf = []
        search_query = "/search?q=from%3Ahirasawa%20since%3A{}%20until%3A{}&src=typed_query&f=live".format(
            since_date.strftime("%Y-%m-%d"), until_date.strftime("%Y-%m-%d"))
        results = twitter_driver.search(search_query)
        since_date = since_date + datetime.timedelta(days=1)
        until_date = since_date + datetime.timedelta(days=1)
        for result in results:
            tweet_data.append([result["id"],
                               result["created_at"],
                               result["text"],
                               result["favorite_count"],
                               result["retweet_count"],
                               result["reply_count"]])
            tweet_data_no_lf.append([result["id"],
                                     result["created_at"],
                                     result["text"],
                                     result["favorite_count"],
                                     result["retweet_count"],
                                     result["reply_count"]])
        over_write_csv(result_file, tweet_data)
        over_write_csv(result_file_no_lf, tweet_data_no_lf)
    twitter_driver.close()


if __name__ == "__main__":
    main()
