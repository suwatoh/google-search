# google-search

Google 検索の結果から上位 20 のリンクを取得します。

検索キーワードは、 googlesearch.py と同じディレクトリにある keywords.txt から読み取ります。

出力結果は、カレントディレクトリ下の output サブディレクトリに Excel ファイルに出力されます。
ファイル名は <検索キーワード>.xlsx となります。

実行方法は次のとおりです。

```shell-session
$ python app/googlesearch.py
```
