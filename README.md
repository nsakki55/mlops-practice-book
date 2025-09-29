# 「実践MLOps 作って理解する機械学習システムの構築と運用」

本レポジトリはオーム社出版「実践MLOps 作って理解する機械学習システムの構築と運用」のサンプルコードです。

| 項目 |                               |
|------|-------------------------------|
| 書籍 | 実践MLOps 作って理解する機械学習システムの構築と運用 |
| URL | https://www.ohmsha.co.jp/book/9784274233982/           |
| ISBN | 978-4-274-23398-2           |
| 正誤表 | [errata.md](https://github.com/nsakki55/mlops-practice-book/blob/main/errata.md) |


## 本書で作成する機械学習システム

本書ではインターネット広告のクリック率予測を行う機械学習システムをAWSで作成します。  
リアルタイム推論を提供する推論サービスを作成し、継続的学習によるモデルの定期的更新を行います。  
実験基盤、CI/CD、特徴量ストア、モデルレジストリ、監視機能を提供します。


## データセット

Kaggleデータセットの[Context Ad Clicks Dataset](https://www.kaggle.com/datasets/arashnic/ctrtest/data)を一部改変したデータセット使用します。  
本レポジトリの[data.zip](./data.zip)を使用します。本書で使用するデータには、`impression_log.csv`、`view_log.csv`、`mst_item.csv`の3つのcsvファイルが含まれます。

## 事前準備
本書執筆時の各ツールのバージョン・実行環境は以下となっています。

| ツール名 | バージョン |
| --- | --- |
| OS | macOS Sequoia 15 |
| Python | 3.12.5 |
| Docker | 28.3.3 |
| Docker Desktop | 4.45.0 |
| Terraform | 1.13.2 |
| AWS CLI | 2.30.1 |

**サンプルコードの取得**  
```zsh
$ git clone https://github.com/nsakki55/mlops-practice-book
$ cd mlops-practice-book
```


**Docker**  
参考: [Install Docker Desktop on Mac](https://docs.docker.com/desktop/setup/install/mac-install/)

```zsh

$ docker --version
Dcker version 28.3.3, build 980b856
```

**uv**  
参考: [Installing uv](https://docs.astral.sh/uv/getting-started/installation/)  

```zsh
$ uv --version
uv 0.6.12 (e4e03833f 2025-04-02)
```

本書はPython 3.12を使用します。  
以下はuvでPythonをインストールする例です。
```zsh
$ uv python install 3.12
$ uv python pin 3.12
```

**Terraform**  
<details>
<summary>asdfでのインストール例</summary>

```zsh
$ asdf plugin add terraform
$ asdf install terraform 1.13.2
$ asdf local terraform 1.13.2
```
</details>

```zsh
$ terraform --version
Terraform v1.13.2
on darwin_amd64
```


**AWS CLI**  
<details>
<summary>asdfでのインストール例</summary>

```zsh
$ asdf plugin add awscli
$ asdf install awscli 2.30.1
$ asdf local awscli 2.30.1
```
</details>

```zsh
$ aws --version
aws-cli/2.30.1 Python/3.13.7 Darwin/24.2.0 exe/x86_64
```

## 動作確認
本書で実行するコマンドをMakefileにまとめています。
```
$ make help
format                  Run ruff format
lint                    Run ruff check
mypy                    Run mypy
test                    Run pytest
train                   Run train
feature                 Run feature extraction
build-push              Push ml pipeline image to ECR
train-docker            Run ml Pipeline
up                      Docker compose up
predict                 Request prediction to localhost
predict-ecs             Request prediction to ECS
healthcheck             Request health check to localhost
healthcheck-ecs         Request health check to ECS
request-test            Request prediction with test date
run-crawl-train-data    Run glue crawler for train_data
run-crawl-predict-log   Run glue crawler for predict_log
run-crawl-train-log     Run glue crawler for train_log
run-crawl-feature-store Run glue crawler for feature_store
help                    Show options
```

## リソース削除
### 1. S3バケットのファイルを削除する
AWSマネジメントコンソール画面からS3のページを開き、ファイルを削除したいS3バケットを選択し【空にする】を実行します。  
本書のTerraformで作成した、tfstateを保存するバケット以外を空にしてください。  
筆者の環境での本書のTerraformで作成したS3バケットの一覧です。
- mlops-athena-output-20250903144044649000000001
- mlops-data-20250903144046588400000005
- mlops-feature-store-20250903144046734200000006
- mlops-model-20250903144044650200000002
- mlops-predict-api-20250903144044654800000003

### 2. ECRのイメージを削除する
AWSマネジメントコンソール画面からECRのページを開き、本書で作成したリポジトリのイメージを全て削除します。  
本書で作成するリポジトリは、以下2つのリポジトリです。
- fluentbit
- mlops-practice

### 3. Athenaのワークグループを削除する
AWSマネジメントコンソール画面からAthenaのページを開き、本書で作成したワークグループを削除します。
ページ左側【ワークグループ】タブから「mlops」ワークグループを選択し、削除します。

### 4. Terraform Destroyを実行
本書のTerraformで作成したAWSリソースを削除するには、terraform destroy コマンドを実行します。  
```
$ terraform destroy
```

### 5. tfstate保存用のS3バケットを削除する
本書のTerraformのtfstate保存用に手動作成したS3バケットを削除します。  
本書ではmlops-terraform-tfstate-{suffix}という名前で、tfstate保存用のS3バケットを作成しています。


## 正誤表
本書の正誤表は[errata.md](https://github.com/nsakki55/mlops-practice-book/blob/main/errata.md)で公開しています。


## お問い合わせ
コードに関するお問い合わせは本レポジトリの[Discussions](https://github.com/nsakki55/mlops-practice-book/discussions)で受け付けています。
