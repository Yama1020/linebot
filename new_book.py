import os
import pandas as pd
from azure.storage.blob import BlockBlobService

# 変数定義
accountname = os.environ["STORAGE_NAME"]
accountkey = os.environ["STORAGE_KEY"]
container_name ='testcontainer'
temppath = "/home/"
csvname = "test02.csv"
csvpath = temppath + csvname


def book_add(title, owner):
    # Blobへ接続しCSVをダウンロード
    block_blob_service = BlockBlobService(account_name=accountname, account_key=accountkey)
    block_blob_service.get_blob_to_path(container_name, csvname, csvpath)

    # CSVに新規図書を追加し再アップロード
    w = pd.DataFrame([[title, "0", "0", owner, "0", "0", "1F"]])
    w.to_csv(csvpath, index=False, encoding="utf-8", mode='a', header=False)
    block_blob_service.create_blob_from_path(container_name, csvname, csvpath)

    # ローカルファイルを削除
    os.remove(csvpath)

