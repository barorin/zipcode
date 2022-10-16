import datetime
import os
import shutil
import urllib.error
import urllib.request
from typing import List

import requests
from bs4 import BeautifulSoup
from tenacity import retry, stop_after_attempt, wait_fixed

# retry設定
wait = wait_fixed(30)  # リトライ間隔
stop = stop_after_attempt(5)  # リトライ回数


@retry(wait=wait, stop=stop)
def get_soup(url: str) -> BeautifulSoup:
    """soup取得
    Args:
        url(str): url
    Returns:
        soup(BeautifulSoup): HTML
    """
    res = requests.get(url)
    res.encoding = res.apparent_encoding  # 文字化け修正
    soup = BeautifulSoup(res.text, "html.parser")

    return soup


@retry(wait=wait, stop=stop)
def check_update() -> List[str]:
    """今日>更新日かチェック
    Args:
        None
    Returns:
        result(list[str]): update_ken_allとupdate_jigyosoが入る
    """
    # KEN_ALL
    ken_all_soup = get_soup("https://www.post.japanpost.jp/zipcode/dl/kogaki-zip.html")
    ken_all_updated_at = (
        ken_all_soup.find("div", class_="arrange-r").get_text().replace("\n", "")
    )
    ken_all_updated_at = datetime.datetime.strptime(ken_all_updated_at, "%Y年%m月%d日更新")

    # JIGYOSYO
    jigyosyo_soup = get_soup(
        "https://www.post.japanpost.jp/zipcode/dl/jigyosyo/index-zip.html"
    )
    jigyosyo_updated_at = jigyosyo_soup.select("div.pad p small")[0].get_text()
    jigyosyo_updated_at = datetime.datetime.strptime(
        jigyosyo_updated_at, "%Y年%m月%d日更新版"
    )

    # 更新チェック
    now = datetime.datetime.now()
    result = []
    if now > ken_all_updated_at:
        result.append("update_ken_all")
    if now > jigyosyo_updated_at:
        result.append("update_jigyosyo")

    return result


def make_folder(folder_path: str) -> None:
    """フォルダ作成
    Args:
        folder_path(str): フォルダパス
    Returns:
        None
    """
    # 既にある場合は、先に丸ごと削除する
    if os.path.exists(folder_path):
        shutil.rmtree(folder_path)

    # 保存先ディレクトリ作成
    os.mkdir(folder_path)


@retry(wait=wait, stop=stop)
def download_zip(file_url: str, save_file_name: str) -> None:
    """ZIPダウンロード
    Args:
        file_url(str): ダウンロードURL
        save_file_name(str): ダウンロードファイル名
    Returns:
        None
    """
    try:
        with urllib.request.urlopen(file_url) as download_file:
            data = download_file.read()
            with open(f"./zip/{save_file_name}", mode="wb") as save_file:
                save_file.write(data)
        print(f"download conmplete: {save_file_name}")
    except urllib.error.URLError as e:
        print(e)
