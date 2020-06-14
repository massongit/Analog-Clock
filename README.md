# Analog-Clock
[![MIT License](https://img.shields.io/badge/license-MIT-blue.svg?style=flat)](LICENSE) [![Maintainability](https://api.codeclimate.com/v1/badges/dfad59652e59c0009ff4/maintainability)](https://codeclimate.com/github/massongit/Analog-Clock/maintainability)

## 概要
PythonのTkinterによるアナログ時計です。

## 開発環境
* Python 3.7

## 機能
* タイムゾーンの切り替え

## 環境構築手順
1. [Ubuntuの場合]<br>以下のコマンドを実行し、必要なパッケージをインストールします。

```bash
$ sudo apt install tk-dev
```

2. 以下のコマンドを実行し、必要なライブラリをインストールします。

```bash
$ pipenv install
```

## ファイル構成
* `analog_clock.py` プログラム本体
* `timezone.txt` アナログ時計で表示するタイムゾーン一覧
