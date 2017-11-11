# coding=utf-8

"""
アナログ時計
"""

import codecs
import datetime
import math

import pytz
import six.moves


class MainWindow(six.moves.tkinter.Tk):
    """
    メインウィンドウ
    """

    def __init__(self, *args, **kwargs):
        six.moves.tkinter.Tk.__init__(self, *args, **kwargs)

        # ヘッダーフレーム
        self._header = six.moves.tkinter.Frame(self)
        self._header.pack()

        # ボタンフレーム
        self._buttons = six.moves.tkinter.Frame(self._header)
        self._buttons.pack()

        # 日付ラベル
        self._date = DateLabel(self._header)
        self._date.pack()

        # 時計
        self._clock = Clock(self, self._date)
        self._clock.pack(expand=True, fill=six.moves.tkinter.BOTH)

        # タイムゾーン切り替えボタン
        TimezoneChangeButton(self._buttons, self._clock).pack()

        # ウィンドウサイズが変更されたとき、ウィンドウサイズを調整する
        self.bind('<Configure>', self._resize)

        # 時計を描画
        self._clock.update()

    def title(self, timezone):
        """
        タイトルをセットする
        :param timezone: タイムゾーン
        """
        six.moves.tkinter.Tk.title(self, 'アナログ時計 ({})'.format(timezone))

    def _resize(self, event):
        """
        ウィンドウサイズを調整する
        """
        # キャンパスサイズ (縦横共通)
        clock_size = min(self._clock.winfo_width(), self._clock.winfo_height())

        # 実際の高さ
        height = clock_size + self._header.winfo_height()

        # ウィンドウサイズを調整
        self.geometry('{}x{}'.format(clock_size, height))


class TimeZone:
    """
    タイムゾーン
    """

    def __init__(self):
        # タイムゾーンリスト
        self._timezones = list()

        with codecs.open('timezone.txt', 'r') as timezone_file:
            for timezone in timezone_file:
                self._timezones.append(pytz.timezone(timezone.strip()))

        # 現在のタイムゾーン
        self._n = 0

    def change(self):
        """
        タイムゾーンを変更する
        :return: 変更後のタイムゾーン
        """
        self._n = (self._n + 1) % len(self._timezones)
        return self.get()

    def get(self):
        """
        現在のタイムゾーンを取得する
        :return: 現在のタイムゾーン
        """
        return self._timezones[self._n]


class TimezoneChangeButton(six.moves.tkinter.Button):
    """
    タイムゾーン切り替えボタン
    """

    # タイムゾーン
    _timezone = TimeZone()

    def __init__(self, master=None, clock=None, cnf=None, **kw):
        if cnf is None:
            cnf = dict()

        six.moves.tkinter.Button.__init__(self, master, cnf, **kw)
        self.configure(command=self._change_timezone, text='タイムゾーン切り替え')

        # 時計
        self._clock = clock
        self._clock.timezone(self._timezone.get())

    def _change_timezone(self):
        """
        タイムゾーンを切り替える
        """
        self._clock.timezone(self._timezone.change())


class DateLabel(six.moves.tkinter.Label):
    """
    日付ラベル
    """

    # 曜日一覧
    _weekdays = ['日', '月', '火', '水', '木', '金', '土']

    def set(self, now):
        """
        日付をセット
        :param now: 今日の日付 (datetime)
        """
        self.configure(text=now.strftime('%Y年%m月%d日')
                       + ' ({})'.format(self._weekdays[now.weekday()]))


class Clock(six.moves.tkinter.Canvas):
    """
    時計
    """

    # 上下左右のマージン
    _margin = 10

    # タイムゾーン
    _timezone = None

    # 初期サイズ
    _default_size = None

    # 倍率
    _scale = 1

    def __init__(self, master=None, date_label=None, cnf=None, **kw):
        if cnf is None:
            cnf = dict()

        six.moves.tkinter.Canvas.__init__(self, master, cnf, **kw)

        # サイズが変更されたとき、倍率をセットする
        self.bind('<Configure>', self._set_scale)

        # 日付ラベル
        self._date = date_label

    def timezone(self, timezone):
        """
        タイムゾーンをセットする
        :param timezone: タイムゾーン
        """
        self._timezone = timezone
        self.master.title(self._timezone)

    def update(self):
        """
        時計を更新する
        """
        # 針の中心座標
        # axis[0] : x座標
        # axis[1] : y座標
        axis = [self.winfo_width() / 2, self.winfo_height() / 2]

        # 針の長さ
        hand_len = self._margin - axis[1]

        # 現在時刻
        now = datetime.datetime.now(self._timezone)

        # 日付をセット
        self._date.set(now)
        self._date.configure(font=('FixedSys', int(14 * self._scale)))

        # キャンパスを初期化
        self.create_rectangle(0, 0, self.winfo_width(),
                              self.winfo_height(), fill='white')

        # プレート部を描画
        self._draw_plate(hand_len, axis, now)

        # 針を描画
        self._draw_hand(hand_len, axis, now)

        # 枠を描画
        self.create_oval(self._margin, self._margin,
                         self.winfo_width() - self._margin, self.winfo_height() - self._margin,
                         outline='black', width=6 * self._scale)

        # 30ミリ秒後にupdate関数を呼び出す
        self.master.after(30, self.update)

    def _set_scale(self, event):
        """
        倍率をセットする
        :param event: イベント
        """
        # 時計が正方形になっているとき
        if event.width == event.height:
            if self._default_size is None:  # 初期サイズがセットされていないとき、初期サイズとメインウィンドウの最小サイズをセットする
                self._default_size = event.width
                self.master.minsize(self.master.winfo_width(),
                                    self.master.winfo_height())
            else:  # 初期サイズがセットされているとき、倍率を更新する
                self._scale = float(event.width) / self._default_size

    def _draw_plate(self, hand_len, axis, now):
        """
        プレート部を描画する
        :param hand_len: 針の長さ
        :param axis: 針の中心座標
        :param now: 現在時刻
        """
        for hour in six.moves.xrange(60):
            # 現在見ている時刻の角度 (ラジアン)
            radian = (hour + 1) * math.pi / 30

            # 針の長さ (ベクトル)
            hand_len_vec = [hand_len * math.sin(radian),
                            hand_len * math.cos(radian)]

            if (hour + 1) % 5:  # 現在見ている時刻が5の倍数でないとき、短めの線を描画
                self._draw_line(hand_len_vec, axis, 0)
            else:  # 現在見ている時刻が5の倍数であるとき
                # 時刻の下駄
                hour_padding = 12 if 11 < now.hour else 0

                # 時刻を描画
                self._draw_number(hand_len_vec, axis,
                                  hour_padding + (hour + 1) // 5)

                # 長めの線を描画
                self._draw_line(hand_len_vec, axis, 1)

    def _draw_line(self, hand_len_vec, axis, kind):
        """
        線を描画する
        :param hand_len_vec: 針の長さ (ベクトル)
        :param axis: 針の中心座標
        :param kind: 線の種類 (0: 短め, 1: 長め)
        """
        self.create_line(axis[0] - (0.875 - 0.125 * kind) * hand_len_vec[0],
                         axis[1] + (0.875 - 0.125 * kind) * hand_len_vec[1],
                         axis[0] - hand_len_vec[0],
                         axis[1] + hand_len_vec[1],
                         fill='black', width=2 * (kind + 1) * self._scale)

    def _draw_number(self, hand_len_vec, axis, hour):
        """
        時刻を描画する
        :param hand_len_vec: 針の長さ (ベクトル)
        :param axis: 針の中心座標
        :param hour: 時刻 (時)
        """
        self.create_text(axis[0] - 0.6 * hand_len_vec[0],
                         axis[1] + 0.6 * hand_len_vec[1],
                         text=hour, font=('FixedSys', int(16 * self._scale)))

    def _draw_hand(self, hand_len, axis, now):
        """
        針を描画する
        :param hand_len: 針の長さ
        :param axis: 針の中心座標
        :param now: 現在時刻
        """
        for hour, scale, color, weight in [[now.minute, 2, 'green', 2],
                                           [now.second, 2, 'red', 1],
                                           [5 * now.hour, 1, 'blue', 2]]:
            # 現在見ている針の角度 (ラジアン)
            radian = hour * math.pi / 30

            # 針の長さ (倍率調整済み)
            scaled_hand_len = hand_len * scale

            # 針を描画
            self.create_line(axis[0], axis[1],
                             axis[0] - scaled_hand_len * math.sin(radian) / 2,
                             axis[1] + scaled_hand_len * math.cos(radian) / 2,
                             fill=color, width=2 * weight * self._scale)


# メイン処理
if __name__ == '__main__':
    MainWindow().mainloop()
