import numpy as np
from sqlalchemy import create_engine

from parse_utils import make_jigyosyo, set_index, to_narrow

# DB接続
SQLALCHEMY_DATABASE_URL = "sqlite:///../../fastapi/zipcode.db"
engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)

# DF作成
jigyosyo = make_jigyosyo("../crawler/csv/JIGYOSYO.CSV")

# インデックス追加
set_index(jigyosyo)

# 全角 -> 半角
# NaNはいったん文字列にしてから戻す（to_narrowのエラー回避）
jigyosyo.fillna("NaN", inplace=True)
for column_name, _ in jigyosyo.items():
    jigyosyo[column_name] = jigyosyo[column_name].apply(to_narrow)
jigyosyo.replace("NaN", np.nan, inplace=True)

# idはintにしてDBに書き込み（上書き）
jigyosyo["id"] = jigyosyo["id"].astype(int)
jigyosyo.to_sql("jigyosyo", con=engine, if_exists="replace", index=False)

print("done: parse jigyosyo")
