## 開発環境

### フロントエンド

### バックエンド

言語：Python
フレームワーク：FastAPI

## commit メッセージ制約

```
<gitmoji><Prefix>：<内容><#issue番号>
```

### gitmoji と prefix の種類

| 絵文字 | prefix   | 内容                                                 |
| ------ | -------- | ---------------------------------------------------- |
| ✨     | feat     | 新機能の実装                                         |
| ⚡️    | perf     | パフォーマンスの改善                                 |
| 🔥     | fire     | 機能・ファイルの削除                                 |
| 🐛     | fix      | バグの修正                                           |
| 🩹     | typo     | ちょっとした修正(小さなミス・誤字など)               |
| 📝     | docs     | コードと関係ない部分(Readme・コメントなど)           |
| 💄     | style    | スタイル関係のファイル(CSS・UI のみの変更など）      |
| ♻️     | refactor | コードのリファクタリング                             |
| 🎨     | art      | コードのフォーマットを整える(自動整形されたのも含む) |
| 🔧     | config   | 設定ファイルの追加・更新(linter など)                |
| ✅     | test     | テストファイル関連(追加・更新など)                   |
| 🚚     | move     | ファイルやディレクトリの移動                         |
| 🎉     | start    | プロジェクトの開始                                   |
| 🚀     | deploy   | デプロイする                                         |

## ブランチルール

Git flow を参考に、以下のルールで行う</br>
流れとしては

1. issue を立てる
2. issue に紐づく feature ブランチを作成する
3. PR を作成する
4. develop ブランチに merge する

### main

本番環境のブランチ

### develop

feature ブランチの変更を反映し merge して動作の確認を行う。

```
develop/{version}
```

例：最初のバージョンのリリース

```
develop/1.0
```

### feature

develop ブランチから派生させる
全ての開発はこのブランチで行う。
基本的に新機能の場合は feature/{#issue 番号}

##### (カテゴリ)

| name        | description                    |
| ----------- | ------------------------------ |
| environment | 環境構築・設定周りの作業       |
| refactoring | コードのリファクタリングを行う |
| improvement | 実装済みの機能改善を行う       |

新機能開発の場合

```
feature/#<issue番号>
```

例：issue：全体のレイアウト構成の作成 #2

```
feature/#2
```

カテゴリを含む場合

```
feature/<category>/#<issue番号>
```

例：issue：環境構築 #1

```
feature/environment/#1
```

### release

(TBD)
develop から merge する
main ブランチに merge する前に確認する作業を行う

### hotfix

(TBD)
main ブランチから派生する
リリース後に起きた緊急のバグ対応を行う
