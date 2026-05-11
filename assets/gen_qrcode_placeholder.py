# -*- coding: utf-8 -*-
"""生成公众号二维码占位图。

⚠️ 这是占位图 —— 用户后续应该用真实二维码截图覆盖此文件。

真实二维码获取方法:
1. 打开微信公众平台 → 设置与开发 → 公众号设置 → 二维码
2. 或者在公众号文章里截取「长按识别」二维码
3. 保存为 wechat-qrcode.png · 放到 assets/ 目录覆盖此占位
"""

from PIL import Image, ImageDraw, ImageFont
import os
import random

OUT = os.path.dirname(os.path.abspath(__file__))
SIZE = 400

# 颜色
BG = "#ffffff"
DARK = "#1e293b"
ACCENT = "#fbbf24"
LIGHT = "#94a3b8"

REG = r"C:\Windows\Fonts\msyh.ttc"
BOLD = r"C:\Windows\Fonts\msyhbd.ttc"
MONO = r"C:\Windows\Fonts\consola.ttf"


def font(size, bold=False):
    return ImageFont.truetype(BOLD if bold else REG, size)


def main():
    img = Image.new("RGB", (SIZE, SIZE), BG)
    d = ImageDraw.Draw(img)

    # 边框
    d.rectangle([0, 0, SIZE - 1, SIZE - 1], outline=DARK, width=3)

    # 顶部标题区
    d.rectangle([0, 0, SIZE, 60], fill=DARK)
    d.text((20, 18), "公众号「实战复盘」", font=font(20, bold=True), fill=ACCENT)

    # 中间二维码区(随机方块模拟)
    qr_size = 240
    qr_x = (SIZE - qr_size) // 2
    qr_y = 90
    # QR 外框
    d.rectangle([qr_x - 4, qr_y - 4, qr_x + qr_size + 4, qr_y + qr_size + 4],
                outline=DARK, width=2)

    # 随机黑白方块模拟二维码(seed 固定 = 看起来像真二维码)
    random.seed(42)
    cell = qr_size // 30
    for i in range(30):
        for j in range(30):
            # 三个定位角(像真二维码)
            corner = (i < 7 and j < 7) or (i < 7 and j >= 23) or (i >= 23 and j < 7)
            if corner:
                # 模拟定位标
                ix, jx = i, j
                if i >= 23: ix = i - 23
                if j >= 23: jx = j - 23
                if ix == 0 or ix == 6 or jx == 0 or jx == 6:
                    is_dark = True
                elif 2 <= ix <= 4 and 2 <= jx <= 4:
                    is_dark = True
                else:
                    is_dark = False
            else:
                is_dark = random.random() < 0.5
            if is_dark:
                d.rectangle([
                    qr_x + j * cell, qr_y + i * cell,
                    qr_x + (j + 1) * cell, qr_y + (i + 1) * cell
                ], fill=DARK)

    # 中心 logo 区
    logo_size = 50
    lx = SIZE // 2 - logo_size // 2
    ly = qr_y + qr_size // 2 - logo_size // 2
    d.rectangle([lx, ly, lx + logo_size, ly + logo_size], fill="#fff", outline=DARK, width=2)
    d.text((lx + 14, ly + 14), "实战", font=font(18, bold=True), fill=DARK)

    # 占位说明文字(让用户知道这是 placeholder)
    d.text((20, qr_y + qr_size + 15),
           "⚠ 此为占位图 · 请用真实二维码覆盖",
           font=font(11), fill=LIGHT)

    # 底部信息
    d.text((20, qr_y + qr_size + 36), "微信号:iamonelong",
           font=font(14, bold=True), fill=DARK)
    d.text((20, qr_y + qr_size + 58), "每周更新 AI Agent 实战",
           font=font(12), fill=LIGHT)

    img.save(os.path.join(OUT, "wechat-qrcode.png"))
    print(f"[OK] wechat-qrcode.png saved (placeholder, please replace with real QR)")


if __name__ == "__main__":
    main()
