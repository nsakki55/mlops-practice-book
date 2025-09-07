# 「実践MLOps 作って理解する機械学習システムの構築と運用」

本レポジトリはオーム社出版「実践MLOps 作って理解する機械学習システムの構築と運用」のサンプルコードです。

| 項目 |                               |
|------|-------------------------------|
| 書籍 | 実践MLOps 作って理解する機械学習システムの構築と運用 |
| URL | TODO: add url link            |
| ISBN | TODO: add ISBN link           |
| 正誤表 | TODO: add fixed record        |


## 本書で作成する機械学習システム

本書ではインターネット広告のクリック率予測を行う機械学習システムをAWSで作成します。  
リアルタイム推論を提供する推論サービスを作成し、継続的学習によるモデルの定期的更新を行います。  
実験基盤、CI/CD、特徴量ストア、モデルレジストリ、監視機能を提供します。


## データセット

Kaggleデータセットの[Context Ad Clicks Dataset](https://www.kaggle.com/datasets/arashnic/ctrtest/data)を一部改変したデータセット使用します。  
本レポジトリのdata.zipを使用します。本書で使用するデータには、`impression_log.csv`、`view_log.csv`、`mst_item.csv`の3つのcsvファイルが含まれます。

## 事前準備

**サンプルコードの取得**  
```zsh
$ git clone https://github.com/nsakki55/mlops-practice-book
$ cd mlops-practice-book
```


**Docker**  
参考: [Install Docker Desktop on Mac](https://docs.docker.com/desktop/setup/install/mac-install/)

```zsh

$ docker --version
Docker version 28.0.4, build b8034c0
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
$ asdf install terraform 1.11.3
$ asdf local terraform 1.11.3
```
</details>

```zsh
$ terraform --version
Terraform v1.11.3
on darwin_amd64
```


**AWS CLI**  
<details>
<summary>asdfでのインストール例</summary>

```zsh
$ asdf plugin add awscli
$ asdf install awscli 2.27.35
$ asdf local awscli 2.27.35 
```
</details>

```zsh
$ aws --version
aws-cli/2.9.2 Python/3.9.11 Darwin/24.2.0 exe/x86_64 prompt/off
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
本書のTerraformで作成したAWSリソースを削除する場合、terraform destroy コマンドを実行します。  
terraform destroyコマンドを実行する場合、S3バケットにファイル・ECRのイメージが存在するとエラーとなるため、AWSコンソールから事前に削除しておきます。
```
$ terraform destroy
```


## 正誤表
本書の正誤表は[errata.md](https://github.com/nsakki55/mlops-practice-book/blob/main/errata.md)で公開しています。


## お問い合わせ
コードに関するお問い合わせは本レポジトリの[Discussions](https://github.com/nsakki55/mlops-practice-book/discussions)で受け付けています。
