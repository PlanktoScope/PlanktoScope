#!/usr/bin/python
# -*- coding:utf-8 -*-
import sys
import os
import time
import logging
from PIL import Image, ImageDraw, ImageFont

# Configuration des chemins
picdir = os.path.join(os.path.dirname(os.path.dirname(os.path.realpath(__file__))), 'pic')
libdir = os.path.join(os.path.dirname(os.path.dirname(os.path.realpath(__file__))), 'lib')
if os.path.exists(libdir):
    sys.path.append(libdir)

from waveshare_epd import epd2in9_V2

logging.basicConfig(level=logging.DEBUG)

try:
    logging.info("epd2in9 V2 - Affichage heure centrée")

    epd = epd2in9_V2.EPD()
    epd.init()
    epd.Clear(0xFF)

    font24 = ImageFont.truetype(os.path.join(picdir, 'Font.ttc'), 24)

    image = Image.new('1', (epd.height, epd.width), 255)  # Mode 1-bit, fond blanc
    draw = ImageDraw.Draw(image)

    while True:
        current_time = time.strftime('%H:%M:%S')

        # Efface l'image (remplir en blanc)
        draw.rectangle((0, 0, epd.height, epd.width), fill=255)

        # Calculer taille du texte avec textbbox (Pillow 10+ friendly)
        bbox = draw.textbbox((0, 0), current_time, font=font24)
        text_w = bbox[2] - bbox[0]
        text_h = bbox[3] - bbox[1]

        # Centrer le texte
        x = (epd.height - text_w) // 2
        y = (epd.width - text_h) // 2

        draw.text((x, y), current_time, font=font24, fill=0)

        epd.display_Partial(epd.getbuffer(image))

        time.sleep(0.5)

except IOError as e:
    logging.error(e)

except KeyboardInterrupt:
    logging.info("Arrêt demandé par utilisateur")
    epd2in9_V2.epdconfig.module_exit(cleanup=True)
    sys.exit()
