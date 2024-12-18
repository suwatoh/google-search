"""Google 検索を実行する.

keywords.txt に検索キーワードを入力する.
LIMIT 変数で検索結果の上限が設定される.

結果はキーワードごとに Excel で出力される.
"""

import os
import time

import pandas as pd
from selenium import webdriver
from selenium.common import exceptions
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

LIMIT = 20

SLEEP_TIME = 3
DEBUG = True


def get_driver() -> webdriver.Chrome:
    """WebDriver インスタンスを作成する."""
    options = webdriver.ChromeOptions()
    # 検索結果に影響しないようにシークレットモードとする
    options.add_argument("--incognito")
    if not DEBUG:
        # ヘッドレスモード
        options.add_argument("--headless")
        # ウィンドウサイズを指定しないとヘッドレスモードがうまく動作しない
        options.add_argument("window-size=1400,600")
    return webdriver.Chrome(options=options)


def get_keywords() -> list[str]:
    """検索キーワードを取得する."""
    # ファイル名
    filename = "keywords.txt"
    if os.path.exists(filename):
        filepath = filename
    else:
        # スクリプトのディレクトリを取得
        script_dir = os.path.dirname(os.path.abspath(__file__))
        # フルパスを作成
        filepath = os.path.join(script_dir, filename)

    with open(filepath, "r", encoding="utf-8") as f:
        return [line.strip() for line in f.readlines()]


def get_data(driver: webdriver.Chrome, keyword: str) -> list[dict[str, str]]:
    """検索結果を取得する."""
    # 検索ボックスを見つけてキーワードを入力しEnterを押す
    search_box = driver.find_element(By.ID, "APjFqb")
    search_box.clear()
    search_box.send_keys(keyword)
    search_box.send_keys(Keys.RETURN)

    # ページが完全に読み込まれるまで待機（最大で10秒）
    locator = (By.CLASS_NAME, "MjjYud")
    wait = WebDriverWait(driver, 10)
    wait.until(EC.presence_of_all_elements_located(locator))

    # 検索結果の一覧からタイトルとURLを取得する
    elements = driver.find_elements(*locator)

    ret = []

    for element in elements:
        title = None
        url = None

        try:
            e = element.find_element(By.CSS_SELECTOR, "h3.LC20lb.MBeuO.DKV0Md")
            # テキストを取得できない場合にエラーを出すために .text 属性ではなく get_attribute("textContent") を使う
            title = e.get_attribute("textContent")
            a = e.find_element(By.XPATH, "..")
            url = a.get_attribute("href")
        except exceptions.NoSuchElementException:
            continue
        except exceptions.StaleElementReferenceException:
            continue
        else:
            ret.append({"TITLE": title, "URL": url})

    return ret


def main(keywords: list[str] | None = None, limit: int = LIMIT):
    """Google 検索を実行する."""
    # 出力ディレクトリを作成
    os.makedirs("output", exist_ok=True)

    driver = get_driver()

    if keywords is None:
        keywords = get_keywords()

    for keyword in keywords:
        # URL にアクセス
        target_url = "https://google.co.jp/"
        driver.get(target_url)

        count = 1
        data = []
        data += get_data(driver, keyword)

        while len(data) < limit:
            time.sleep(SLEEP_TIME)
            nav_items = driver.find_elements(By.CLASS_NAME, "NKTSme")
            if len(nav_items) > count:
                nav_item = nav_items[count].find_element(By.TAG_NAME, "a")
                nav_item.click()
                time.sleep(SLEEP_TIME)
                data += get_data(driver, keyword)
            else:
                data.append({"": ""})
            count += 1

        time.sleep(SLEEP_TIME)
        df = pd.DataFrame(data[:limit])
        df.to_excel(f"output/{keyword}.xlsx", index=False)

    driver.quit()


if __name__ == "__main__":
    main()
