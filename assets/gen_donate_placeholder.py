# -*- coding: utf-8 -*-
"""生成打赏二维码占位图 · 微信支付 + 支付宝两种样式。

⚠️ 占位图 — 用户后续应该用真二维码截图覆盖。
"""

from PIL import Image, ImageDraw, ImageFont
import os
import random

OUT = os.path.dirname(os.path.abspath(__file__))

# 微信支付绿
WX_GREEN = "#1aad19"
# 支付宝蓝
ALIPAY_BLUE = "#1677ff"

WHITE = "#ffffff"
DARK = "#1e293b"
GRAY = "#94a3b8"

REG = r"C:\Windows\Fonts\msyh.ttc"
BOLD = r"C:\Windows\Fonts\msyhbd.ttc"


def font(size, bold=False):
    return ImageFont.truetype(BOLD if bold else REG, size)


def rrect(d, xy, r, fill=None, outline=None, width=1):
    d.rounded_rectangle(xy, radius=r, fill=fill, outline=outline, width=width)


def draw_fake_qr(d, x1, y1, x2, y2, seed=42):
    """画一个仿真二维码"""
    random.seed(seed)
    cell = (x2 - x1) // 25
    for i in range(25):
        for j in range(25):
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
                    x1 + j * cell, y1 + i * cell,
                    x1 + (j + 1) * cell, y1 + (i + 1) * cell
                ], fill=DARK)


def gen_wechat_pay():
    """微信支付 · 绿底竖版"""
    W, H = 420, 600
    img = Image.new("RGB", (W, H), WX_GREEN)
    d = ImageDraw.Draw(img)

    # 标题
    d.text((W // 2 - 110, 40), "推荐使用微信支付", font=font(28, bold=True), fill=WHITE)

    # 白卡片
    rrect(d, [40, 110, W - 40, 480], 14, fill=WHITE)

    # QR
    qr_x1, qr_y1 = 70, 140
    qr_x2, qr_y2 = W - 70, 420
    draw_fake_qr(d, qr_x1, qr_y1, qr_x2, qr_y2, seed=42)

    # logo 中心
    logo_s = 56
    lx = W // 2 - logo_s // 2
    ly = (qr_y1 + qr_y2) // 2 - logo_s // 2
    rrect(d, [lx, ly, lx + logo_s, ly + logo_s], 8, fill=WHITE, outline=WX_GREEN, width=3)
    # 微信支付的对勾 logo(简化)
    d.polygon([(lx + 16, ly + 28), (lx + 24, ly + 36), (lx + 40, ly + 20)], outline=WX_GREEN)
    d.line([(lx + 16, ly + 28), (lx + 24, ly + 36)], fill=WX_GREEN, width=4)
    d.line([(lx + 24, ly + 36), (lx + 40, ly + 20)], fill=WX_GREEN, width=4)

    # 名字
    d.text((W // 2 - 55, 440), "Onelong(*隆)", font=font(16, bold=True), fill=DARK)

    # 底部标记
    rrect(d, [80, 520, W - 80, 570], 25, fill=WHITE)
    d.ellipse([95, 530, 130, 565], fill=WX_GREEN)
    d.text((100, 539), "✓", font=font(20, bold=True), fill=WHITE)
    d.text((145, 535), "微信支付", font=font(22, bold=True), fill=DARK)

    img.save(os.path.join(OUT, "wechat-pay-qrcode.png"))
    print("[OK] wechat-pay-qrcode.png (placeholder)")


def gen_alipay():
    """支付宝 · 蓝底竖版"""
    W, H = 420, 600
    img = Image.new("RGB", (W, H), WHITE)
    d = ImageDraw.Draw(img)

    # 顶部 logo 区(白底)
    # 支付宝 logo 简化
    rrect(d, [W // 2 - 30, 30, W // 2 + 6, 80], 6, fill=ALIPAY_BLUE)
    d.text((W // 2 - 22, 38), "支", font=font(24, bold=True), fill=WHITE)
    d.text((W // 2 + 18, 36), "支付宝", font=font(28, bold=True), fill=DARK)

    # 蓝色主区
    d.rectangle([0, 110, W, H], fill=ALIPAY_BLUE)

    # 标题
    d.text((W // 2 - 110, 140), "推荐使用支付宝", font=font(28, bold=True), fill=WHITE)

    # 白卡片
    rrect(d, [40, 220, W - 40, 540], 14, fill=WHITE)

    # QR
    qr_x1, qr_y1 = 70, 245
    qr_x2, qr_y2 = W - 70, 490
    draw_fake_qr(d, qr_x1, qr_y1, qr_x2, qr_y2, seed=99)

    # logo 中心
    logo_s = 50
    lx = W // 2 - logo_s // 2
    ly = (qr_y1 + qr_y2) // 2 - logo_s // 2
    rrect(d, [lx, ly, lx + logo_s, ly + logo_s], 6, fill=ALIPAY_BLUE)
    d.text((lx + 13, ly + 12), "支", font=font(22, bold=True), fill=WHITE)

    # 名字
    d.text((W // 2 - 55, 505), "Onelong(*隆)", font=font(16, bold=True), fill=DARK)

    # 底部
    d.text((W // 2 - 90, 555), "打开支付宝[扫一扫]", font=font(18, bold=True), fill=WHITE)

    img.save(os.path.join(OUT, "alipay-qrcode.png"))
    print("[OK] alipay-qrcode.png (placeholder)")


if __name__ == "__main__":
    gen_wechat_pay()
    gen_alipay()
    print("\n占位图生成完毕 · 请用真实二维码截图覆盖")
