import re
import unicodedata
from typing import Any, List

import pandas as pd

# --------------------------------------------------- #
# General                                             #
# --------------------------------------------------- #


def to_narrow(row: Any) -> str:
    """全角 -> 半角
    Args:
        row(Pandas): 半角に変換したいテキスト
    Returns:
        row(str): 半角変換後のテキスト
    """
    return unicodedata.normalize("NFKC", row)


def set_index(df: pd.DataFrame) -> pd.DataFrame:
    """1から始まるインデックス列（str型）を先頭に作成
    Args:
        df(DataFrame): インデックスを付したいdf
    Returns:
        df(DataFrame): インデックスを付したdf
    """
    id = range(1, len(df.index) + 1)
    df.insert(0, column="id", value=id)
    df["id"] = df["id"].astype(str)

    return df


# --------------------------------------------------- #
# KEN_ALL                                             #
# --------------------------------------------------- #


def make_ken_all(file_path: str) -> pd.DataFrame:
    """KEN_ALLのDF作成
    Args:
        file_path(str): KEN_ALL.CSVのファイルパス
    Returns:
        ken_all(DataFrame): KEN_ALL.CSVのDataFrame
    """
    names = [
        "全国地方公共団体コード",
        "旧郵便番号",  # 5桁
        "郵便番号",  # 7桁
        "都道府県名カナ",  # ｶﾅ
        "市区町村名カナ",  # ｶﾅ
        "町域名カナ",  # ｶﾅ
        "都道府県名",  # 漢字
        "市区町村名",  # 漢字
        "町域名",  # 漢字
        "一町域が二以上の郵便番号で表される場合の表示",  # 0…該当せず、1…該当
        "小字毎に番地が起番されている町域の表示",  # 0…該当せず、1…該当
        "丁目を有する町域の場合の表示",  # 0…該当せず、1…該当
        "一つの郵便番号で二以上の町域を表す場合の表示",  # 0…該当せず、1…該当
        "更新の表示",  # 0…変更なし、1…変更あり、2…廃止（廃止データのみ使用）
        # 0…変更なし、1…市政・区政・町政・分区・政令指定都市施行、
        # 2…住居表示の実施、3…区画整理、4…郵便区調整等、5…訂正、6…廃止（廃止データのみ使用）
        "変更理由",
    ]

    dtype = {
        "全国地方公共団体コード": str,
        "旧郵便番号": str,
        "郵便番号": str,
        "都道府県名カナ": str,
        "市区町村名カナ": str,
        "町域名カナ": str,
        "都道府県名": str,
        "市区町村名": str,
        "町域名": str,
        "一町域が二以上の郵便番号で表される場合の表示": str,
        "小字毎に番地が起番されている町域の表示": str,
        "丁目を有する町域の場合の表示": str,
        "一つの郵便番号で二以上の町域を表す場合の表示": str,
        "更新の表示": str,
        "変更理由": str,
    }

    ken_all = pd.read_csv(
        file_path, encoding="shift_jis", header=None, names=names, dtype=dtype
    )

    # 必要な列だけ残す
    ken_all = ken_all[["郵便番号", "都道府県名", "市区町村名", "町域名"]]

    return ken_all


def create_merged_list(ken_all: pd.DataFrame, column_name: str) -> List[str]:
    """町域名が複数行にまたがっている場合、1行にマージしたリストを返す。
    Args:
        ken_all(DataFrame): KEN_ALL.CSVのDataFrame
        column(str): 町域名の列名
    Returns:
        lst(list): 町域名を統合したリスト
    """
    lst = []
    cnt = 0
    town = ""
    for _, row in ken_all.iterrows():
        if row["is_even_paren"] is False:
            cnt += 1

        if cnt == 0:
            # 単一行で完結
            lst.append(row[column_name])
        elif cnt == 1:
            # 次の行へ続く
            town += row[column_name]
            lst.append("NEXT")
        elif cnt == 2:
            # 結合後の町域名
            town += row[column_name]
            lst.append(town)

            # 初期化
            cnt = 0
            town = ""

    return lst


def merge_lines(ken_all: pd.DataFrame) -> pd.DataFrame:
    """町域名が複数行にまたがっている場合、1行にマージしたDFを返す。
    Args:
        ken_all(DataFrame): KEN_ALL.CSVのDataFrame
    Returns:
        ken_all(DataFrame): 町域名マージ後のDataFrame
    """
    # 町域名が複数行にまたがっていないかを（）で判定
    ken_all["is_even_paren"] = ken_all["町域名"].str.count(r"\(") == ken_all[
        "町域名"
    ].str.count(r"\)")

    ken_all["町域名"] = create_merged_list(ken_all, "町域名")

    # 町域名が「NEXT」の行は削除
    ken_all = ken_all[ken_all["町域名"] != "NEXT"]

    # is_even_paren列を削除
    ken_all.drop("is_even_paren", axis=1, inplace=True)

    return ken_all


def add_prefix_and_suffix(row: Any) -> str:
    """'()'内の記載で必要なものを展開
    # 例) 〒0580343 東洋(油駒、南東洋、132〜156、158〜354、366、367番地)
    # -> 東洋、東洋油駒、東洋南東洋、東洋366番地、東洋367番地
    Args:
        row(Pandas): 町域名
    Returns:
        result(str): prefix...（）前の町域名、suffix...番地or丁目を付したテキスト
    """
    # '('か'、'で分割
    lst = re.split(r"[\(、]", row)

    # '()'内の〜でつながっている部分は削除
    lst = [s for s in lst if "〜" not in s]

    if re.match(r".*番地\)$", row):
        with_suf = [s + "番地" if re.match(r".*[\d−]+$", s) else s for s in lst]
    elif re.match(r".*丁目\)$", row):
        with_suf = [s + "丁目" if re.match(r".*[\d−]+$", s) else s for s in lst]
    else:
        with_suf = lst

    with_pre_suf_list = [with_suf[0] + s for s in with_suf[1:]]
    with_pre_suf_list.insert(0, with_suf[0])
    with_pre_suf = "、".join(with_pre_suf_list)

    if with_pre_suf:
        result = re.sub(r"\)$", "", with_pre_suf)
    else:
        result = "、".join(lst)

    return result


def preproc_ken_all(ken_all: pd.DataFrame) -> pd.DataFrame:
    """KEN_ALLの全体的な前処理
    Args:
        ken_all(DataFrame): KEN_ALL.CSVのDataFrame（前処理前）
    Returns:
        ken_all(DataFrame): KEN_ALL.CSVのDataFrame（前処理後）
    """
    # '以下に掲載がない場合'を削除
    ken_all["町域名"].replace("以下に掲載がない場合", "", inplace=True)

    # 'の次に番地がくる場合'を削除
    ken_all["町域名"].replace(r".*の次に番地がくる場合", "", regex=True, inplace=True)

    # 'の次に(n〜n)番地(以降)がくる場合'を含む'()'とかっこ内を削除
    # 例) 〒7660001 琴平町の次に1〜426番地がくる場合(川東) -> ''
    ken_all["町域名"].replace(r".*の次に[\d〜−]+番地(以降)?がくる場合.*", "", regex=True, inplace=True)

    # '～一円'となっている場合のみ'一円'を削除
    # 例1) 〒3994511 南箕輪村一円 -> 南箕輪村
    # 例2) 〒5220317 一円 -> 一円
    ken_all["町域名"] = ken_all["町域名"].apply(
        lambda x: re.sub(r"一円", "", x) if "一円" in x and len(x) > 2 else x
    )

    # '(第)n地割〜(第)n地割'を削除
    # 例1) 〒0295523 越中畑64地割〜越中畑66地割 -> 越中畑
    # 例2) 〒0295523 桂子沢75地割、桂子沢76地割 -> 桂子沢
    # 例3) 〒0287917 種市第50地割〜第70地割(大沢、城内、滝沢) -> 種市(大沢、城内、滝沢)
    ken_all["町域名"].replace(r"第?\d+地割(〜|、).*地割", "", regex=True, inplace=True)

    # n地割を削除
    ken_all["町域名"].replace(r"第?\d+地割", "", regex=True, inplace=True)

    # '(全域)'を削除
    ken_all["町域名"].replace(r"\(全域\)", "", regex=True, inplace=True)

    # '(丁目)'を削除
    ken_all["町域名"].replace(r"\(丁目\)", "", regex=True, inplace=True)

    # '(各町)'を削除
    ken_all["町域名"].replace(r"\(各町\)", "", regex=True, inplace=True)

    # '（大字、番地）'を削除
    ken_all["町域名"].replace(r"\(大字、番地\)", "", regex=True, inplace=True)

    # '(番地)'を削除
    ken_all["町域名"].replace(r"\(番地\)", "", regex=True, inplace=True)

    # '無番地'を削除
    ken_all["町域名"].replace(r"無番地", "", regex=True, inplace=True)

    # '無番のみ'を削除
    ken_all["町域名"].replace(r"番地のみ", "", regex=True, inplace=True)

    # '(無番地)'を削除
    ken_all["町域名"].replace(r"\(無番地\)", "", regex=True, inplace=True)

    # '(○○屋敷)'を削除
    ken_all["町域名"].replace(r"\(○○屋敷\)", "", regex=True, inplace=True)

    # '(地階・階層不明)'を削除
    ken_all["町域名"].replace(r"\(地階・階層不明\)", "", regex=True, inplace=True)

    # '(高層棟)'を削除
    ken_all["町域名"].replace(r"\(高層棟\)", "", regex=True, inplace=True)

    # '(n階)'から'()'を削除
    # 例) 〒1076001 赤坂赤坂アークヒルズ・アーク森ビル(1階) -> 赤坂赤坂アークヒルズ・アーク森ビル1階
    ken_all["町域名"] = ken_all["町域名"].apply(
        lambda x: re.sub(r"\(|\)", " ", x).strip() if re.match(r".*\(\d+階\)", x) else x
    )

    # '（成田国際空港）'を削除
    ken_all["町域名"].replace(r"\(成田国際空港内\)", "", regex=True, inplace=True)

    # '仙台空港関係施設'を削除
    ken_all["町域名"].replace(r"仙台空港関係施設", "", regex=True, inplace=True)

    # '(～を除く)'を削除
    ken_all["町域名"].replace(r"\(.*を除く\)$", "", regex=True, inplace=True)

    # '「～を除く」'を削除
    ken_all["町域名"].replace(r"「.*を除く」", "", regex=True, inplace=True)

    # 'を含む'を含む'(～)'を削除
    ken_all["町域名"] = ken_all["町域名"].apply(
        lambda x: re.sub(r"\(.*\)", "", x) if "を含む" in x else x
    )

    # '以上'を含む'(～)'を削除
    ken_all["町域名"] = ken_all["町域名"].apply(
        lambda x: re.sub(r"\(.*\)", "", x) if "以上" in x else x
    )

    # '以下'を含む'(～)'を削除
    ken_all["町域名"] = ken_all["町域名"].apply(
        lambda x: re.sub(r"\(.*\)", "", x) if "以下" in x else x
    )

    # '以内'を含む'(～)'を削除
    ken_all["町域名"] = ken_all["町域名"].apply(
        lambda x: re.sub(r"\(.*\)", "", x) if "以内" in x else x
    )

    # '以降'を含む'(～)'を削除
    ken_all["町域名"] = ken_all["町域名"].apply(
        lambda x: re.sub(r"\(.*\)", "", x) if "以降" in x else x
    )

    # '～以外)'で終わる'(～)'を削除
    ken_all["町域名"] = ken_all["町域名"].apply(
        lambda x: re.sub(r"\(.*\)", "", x) if re.match(r".*以外\)$", x) else x
    )

    # '中一里山「9番地の4、12番地」'を分解
    # 例) 〒6520071 山田町下谷上（菊水山、高座川向、中一里山「9番地の4、12番地」、...
    # -> 山田町下谷上（菊水山、高座川向、中一里山9番地の4、中一里山12番地、...
    ken_all["町域名"].replace(
        r"中一里山「9番地の4、12番地」", "中一里山9番地の4番地、中一里山12番地", regex=True, inplace=True
    )

    # '「～」'or'「～」以外'を削除
    # 例) 〒9996652 添川渡戸沢「筍沢温泉」 -> 添川渡戸沢
    # 例) 〒0482402 大江(1丁目、2丁目「651、662、668番地」以外、... -> 大江(1丁目、2丁目、...
    ken_all["町域名"].replace(r"「.*」(以外)?", "", regex=True, inplace=True)

    # 'その他'を含む'(～)'を削除
    ken_all["町域名"] = ken_all["町域名"].apply(
        lambda x: re.sub(r"\(.*\)", "", x) if "その他" in x else x
    )

    # '()'内の記載で必要なものを展開
    # 例) 〒0580343 東洋(油駒、南東洋、132〜156、158〜354、366、367番地) -> 東洋、東洋油駒、東洋南東洋、東洋366番地、東洋367番地
    ken_all["町域名"] = ken_all["町域名"].apply(add_prefix_and_suffix)

    # '()'を削除(かっこ内が空)
    ken_all["町域名"].replace(r"\(\)", "", inplace=True)

    """
    ・が入ってる町域名のうち、修正が必要なものは個別対応
    """
    # 〒0350003 野牛稲崎平302番地・315番地 -> 野牛稲崎平302番地、野牛稲崎平315番地
    ken_all["町域名"].replace(
        r"野牛稲崎平302番地・315番地", "野牛稲崎平302番地、野牛稲崎平315番地", regex=True, inplace=True
    )

    # 〒1690052 戸山3丁目18・21番 -> 戸山3丁目18、戸山3丁目21番
    ken_all["町域名"].replace(
        r"戸山3丁目18・21番", "戸山3丁目18番、戸山3丁目21番", regex=True, inplace=True
    )

    # 〒2820011 御料牧場・成田国際空港内 -> 御料牧場
    ken_all["町域名"].replace(r"御料牧場・成田国際空港内", "御料牧場", regex=True, inplace=True)

    # 〒9420083 大豆4の2・4・6番地 -> 大豆4の2番地、大豆4の4番地、大豆4の6番地
    ken_all["町域名"].replace(
        r"大豆4の2・4・6番地", "大豆4の2番地、大豆4の4番地、大豆4の6番地", regex=True, inplace=True
    )

    # 〒4310423 新所・岡崎・梅田入会地 -> 新所、岡崎、梅田入会地
    ken_all["町域名"].replace(r"新所・岡崎・梅田入会地", "新所、岡崎、梅田入会地", regex=True, inplace=True)

    # 〒8920876 岡之原町832の2・4 -> 岡之原町832の2、岡之原町832の4
    ken_all["町域名"].replace(
        r"岡之原町832の2・4", "岡之原町832の2、岡之原町832の4", regex=True, inplace=True
    )

    # 〒9498316 結東逆巻・前倉・結東 -> 結東逆巻、結東前倉、結東
    ken_all["町域名"].replace(r"結東逆巻・前倉・結東", "結東逆巻、結東前倉、結東", regex=True, inplace=True)

    # 〒3910212 北山渋御殿湯・渋の湯 -> 北山渋御殿湯、北山渋の湯
    ken_all["町域名"].replace(r"北山渋御殿湯・渋の湯", "北山渋御殿湯、北山渋の湯", regex=True, inplace=True)

    # 〒7913203 中山町出渕豊岡・東町 -> 中山町出渕豊岡、中山町出渕東町
    ken_all["町域名"].replace(r"中山町出渕豊岡・東町", "中山町出渕豊岡、中山町出渕東町", regex=True, inplace=True)

    # 〒7850163 浦ノ内東分鳴無・坂内 -> 浦ノ内東分鳴無、浦ノ内東分坂内
    ken_all["町域名"].replace(r"浦ノ内東分鳴無・坂内", "浦ノ内東分鳴無、浦ノ内東分坂内", regex=True, inplace=True)

    # 〒9401172 釜ケ島土手畑・藤場 -> 釜ケ島土手畑、釜ケ島藤場
    ken_all["町域名"].replace(r"釜ケ島土手畑・藤場", "釜ケ島土手畑、釜ケ島藤場", regex=True, inplace=True)

    # 〒8700924 牧白滝B・C -> 牧白滝B、牧白滝C
    ken_all["町域名"].replace(r"牧白滝B・C", "牧白滝B、牧白滝C", regex=True, inplace=True)

    # 〒7811606 土居甲・乙 -> 土居甲、土居乙
    ken_all["町域名"].replace(r"土居甲・乙", "土居甲、土居乙", regex=True, inplace=True)

    """
    仕上げ
    """
    # ハイフンを半角に変換
    ken_all["町域名"].replace(r"−", "-", regex=True, inplace=True)

    # '、'区切りの町域名を行分割
    # 例) 〒7614104 甲、乙(吉ケ浦)
    ken_all = ken_all.assign(町域名=ken_all["町域名"].str.split("、")).explode("町域名")

    # 完全重複行を削除
    ken_all.drop_duplicates(inplace=True)

    # 列名リネーム
    ken_all = ken_all.rename(
        columns={
            "郵便番号": "zipcode",
            "都道府県名": "prefecture",
            "市区町村名": "city",
            "町域名": "town",
        }
    )

    # 住所を結合した列を追加
    ken_all["address"] = ken_all["prefecture"] + ken_all["city"] + ken_all["town"]

    return ken_all


# --------------------------------------------------- #
# JIGYOSYO                                            #
# --------------------------------------------------- #


def make_jigyosyo(file_path: str) -> pd.DataFrame:
    """JIGYOSYOのDF作成
    Args:
        file_path(str): JIGYOSYO.CSVのファイルパス
    Returns:
        jigyosyo(DataFrame): JIGYOSYO.CSVのDataFrame
    """
    names = [
        "大口事業所の所在地のJISコード",  # 4桁
        "大口事業所名（カナ）",  # ｶﾅ
        "大口事業所名",  # 漢字
        "都道府県名",  # 漢字
        "市区町村名",  # 漢字
        "町域名",  # 漢字
        "小字名、丁目、番地等",  # 漢字
        "大口事業所個別番号",  # 6桁
        "旧郵便番号",
        "取扱局",  # 漢字
        "個別番号の種別の表示",  # 0…該当せず、1…該当
        "複数番号の有無",  # 0…該当せず、1…該当
        "修正コード",  # 0…該当せず、1…該当
    ]

    dtype = {
        "大口事業所の所在地のJISコード": str,
        "大口事業所名（カナ）": str,
        "大口事業所名": str,
        "都道府県名": str,
        "市区町村名": str,
        "町域名": str,
        "小字名、丁目、番地等": str,
        "大口事業所個別番号": str,
        "旧郵便番号": str,
        "取扱局": str,
        "個別番号の種別の表示": str,
        "複数番号の有無": str,
        "修正コード": str,
    }

    jigyosyo = pd.read_csv(
        file_path, encoding="cp932", header=None, names=names, dtype=dtype
    )

    # 必要な列だけ残す
    jigyosyo = jigyosyo[["大口事業所名", "大口事業所個別番号", "都道府県名", "市区町村名", "町域名", "小字名、丁目、番地等"]]

    # 列名リネーム
    jigyosyo = jigyosyo.rename(
        columns={
            "大口事業所名": "company",
            "大口事業所個別番号": "zipcode",
            "都道府県名": "prefecture",
            "市区町村名": "city",
            "町域名": "town",
            "小字名、丁目、番地等": "chome",
        }
    )

    # 住所を結合した列を追加
    jigyosyo["address"] = (
        jigyosyo["prefecture"] + jigyosyo["city"] + jigyosyo["town"] + jigyosyo["chome"]
    )

    return jigyosyo
