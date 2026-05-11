# -*- coding: utf-8 -*-
"""生成公众号二维码占位图 · 仿微信搜一搜横版风格。

⚠️ 这是占位图 —— 用户后续应该用真实二维码截图覆盖此文件。

真实二维码:用户的实际公众号二维码截图(微信搜一搜横版风格)
"""

from PIL import Image, ImageDraw, ImageFont
import os
import random

OUT = os.path.dirname(os.path.abspath(__file__))
W, H = 1200, 380   # 仿用户提供的横版比例

# 微信官方绿色
WX_GREEN = "#07C160"
BG = "#0a9c4d"     # 微信绿稍深一点更稳
WHITE = "#ffffff"
DARK = "#1e293b"
SUB = "#cbd5e1"
GRAY = "#94a3b8"

REG = r"C:\Windows\Fonts\msyh.ttc"
BOLD = r"C:\Windows\Fonts\msyhbd.ttc"
MONO = r"C:\Windows\Fonts\consola.ttf"


def font(size, bold=False):
    return ImageFont.truetype(BOLD if bold else REG, size)


def rrect(d, xy, r, fill=None, outline=None, width=1):
    d.rounded_rectangle(xy, radius=r, fill=fill, outline=outline, width=width)


def main():
    img = Image.new("RGB", (W, H), WX_GREEN)
    d = ImageDraw.Draw(img)

    # ====== 左侧:白色卡片 + 二维码 ======
    card_x1, card_y1 = 40, 50
    card_x2, card_y2 = 340, 330
    rrect(d, [card_x1, card_y1, card_x2, card_y2], 18, fill=WHITE)

    # 卡片顶部小字:公众号名
    d.text((card_x1 + 16, card_y1 + 14), "公众号「实战复盘」", font=font(13, bold=True), fill=DARK)

    # 二维码区(模拟)
    qr_x1, qr_y1 = card_x1 + 22, card_y1 + 50
    qr_x2, qr_y2 = card_x2 - 22, card_y2 - 50
    qr_size = qr_x2 - qr_x1

    # 模拟二维码方块(seed 固定看着像真的)
    random.seed(2026)
    cell = qr_size // 25
    for i in range(25):
        for j in range(25):
            # 三个角的定位标(真二维码特征)
            corner = ((i < 7 and j < 7) or
                      (i < 7 and j >= 18) or
                      (i >= 18 and j < 7))
            if corner:
                ix = i if i < 7 else i - 18
                jx = j if j < 7 else j - 18
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
                    qr_x1 + j * cell, qr_y1 + i * cell,
                    qr_x1 + (j + 1) * cell, qr_y1 + (i + 1) * cell
                ], fill=DARK)

    # 二维码中心 logo(白底 + "实战")
    logo_s = 50
    lx = qr_x1 + qr_size // 2 - logo_s // 2
    ly = qr_y1 + qr_size // 2 - logo_s // 2
    rrect(d, [lx, ly, lx + logo_s, ly + logo_s], 8, fill=WHITE, outline=DARK, width=2)
    d.text((lx + 13, ly + 14), "实战", font=font(16, bold=True), fill=DARK)

    # 卡片底部小字
    d.text((card_x1 + 16, card_y2 - 42), "⚠ 占位图 · 请用真二维码覆盖此文件",
           font=font(10), fill=GRAY)
    d.text((card_x1 + 16, card_y2 - 24), "微信号:IamOnelong",
           font=font(12, bold=True), fill=DARK)

    # ====== 中间:微信搜一搜图标 + 文字 ======
    # 微信对话气泡(简化版)
    bubble_x, bubble_y = 410, 90
    rrect(d, [bubble_x, bubble_y, bubble_x + 70, bubble_y + 55], 28, fill=WHITE)
    rrect(d, [bubble_x + 35, bubble_y + 15, bubble_x + 105, bubble_y + 70], 28, fill=WHITE)
    # 气泡内的小圆点(代表对话)
    for cx in [bubble_x + 18, bubble_x + 30, bubble_x + 42]:
        d.ellipse([cx - 3, bubble_y + 25, cx + 3, bubble_y + 31], fill=WX_GREEN)
    for cx in [bubble_x + 55, bubble_x + 67, bubble_x + 79]:
        d.ellipse([cx - 3, bubble_y + 40, cx + 3, bubble_y + 46], fill=WX_GREEN)

    # "微信搜一搜" 大字
    d.text((550, 70), "微信搜一搜", font=font(56, bold=True), fill=WHITE)

    # ====== 底部:搜索框 ======
    sb_x1, sb_y1 = 550, 190
    sb_x2, sb_y2 = 1140, 270
    rrect(d, [sb_x1, sb_y1, sb_x2, sb_y2], 14, fill=WHITE)
    # 放大镜 (用圆形 + 线模拟)
    cx, cy = sb_x1 + 30, sb_y1 + 40
    d.ellipse([cx - 12, cy - 12, cx + 8, cy + 8], outline=GRAY, width=3)
    d.line([(cx + 6, cy + 6), (cx + 16, cy + 16)], fill=GRAY, width=3)
    # 公众号搜索词
    d.text((sb_x1 + 60, sb_y1 + 22), "IamOnelong",
           font=font(34, bold=True), fill=DARK)

    # ====== 底部说明 ======
    d.text((550, 290), "扫左侧二维码 · 或在微信搜索 IamOnelong",
           font=font(15), fill=WHITE)
    d.text((550, 320), "每周更新 AI Agent 行业落地实战",
           font=font(13), fill=SUB)

    img.save(os.path.join(OUT, "wechat-qrcode.png"))
    print(f"[OK] wechat-qrcode.png saved ({W}x{H}) · 占位图 · 风格仿用户原图")


if __name__ == "__main__":
    main()
