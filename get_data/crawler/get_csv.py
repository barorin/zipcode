import shutil

from crawler_utils import check_update, download_zip, make_folder

# フォルダ初期化
make_folder("./zip")
make_folder("./csv")

# 更新チェック
check = check_update()
if "update_ken_all" in check:
    # KEN_ALL
    download_zip(
        "https://www.post.japanpost.jp/zipcode/dl/kogaki/zip/ken_all.zip", "ken_all.zip"
    )
    shutil.unpack_archive("./zip/ken_all.zip", "./csv")  # ZIP解凍
if "update_jigyosyo" in check:
    # JIGYOSYO
    download_zip(
        "https://www.post.japanpost.jp/zipcode/dl/jigyosyo/zip/jigyosyo.zip",
        "jigyosyo.zip",
    )
    shutil.unpack_archive("./zip/jigyosyo.zip", "./csv")  # ZIP解凍
