import os
from datetime import datetime

import PIL
from PIL import Image, ImageDraw, ImageFont
import sys
import numpy as np
import json


class ImageGenerator:
    font_huge = ImageFont.load_default()
    font_large = ImageFont.load_default()
    font_medium = ImageFont.load_default()
    font_small = ImageFont.load_default()

    def __init__(self):
        # Config-Datei importieren und auf Grundvariablen anwenden
        try:
            with open('config.json', 'r') as config_file:
                config_data = json.load(config_file)
                self.cfg = config_data['config']['image_generator']
        except OSError as e:
            print("Configfile not found - Please check the File!", e)
            return sys.exit()

        cfg = self.cfg
        # Bildparameter
        self.size = (cfg['image_size'][0], cfg['image_size'][1])
        self.image_path = cfg['image_path']
        self.maintenance_path = cfg['maintenance_path']

        self.background_color = cfg['background_color']  # Weiß

        # Standard-Font in Variable übertragen:
        self.font = cfg['standard_font']

        # Lesson rect config
        self.lesson_rect_color = cfg['lesson_rect_color']
        self.lesson_rect_background_color = cfg['lesson_rect_background_color']
        self.lesson_rect_height = cfg['lesson_rect_height']
        self.upper_margin = cfg['upper_margin']
        self.bottom_margin = cfg['bottom_margin']
        self.outside_margin = cfg['outside_margin']
        self.lesson_rect_spacing = cfg['lesson_rect_spacing']
        self.lesson_rect_corner_radius = cfg['lesson_rect_corner_radius']
        self.lesson_rect_outline_color = cfg['lesson_rect_outline_color']
        self.lesson_default_color = cfg['lesson_default_color']
        self.lesson_rect_outline_width = cfg['lesson_rect_outline_width']
        self.double_lesson_multiplier = cfg['double_lesson_multiplier']

        # battery status
        self.battery_status_height = cfg['battery_status_height']
        self.battery_status_width = cfg['battery_status_width']

        # general config
        self.bottom_text = cfg['bottom_text']
        self.irregular_code = cfg['irregular_code']
        self.cancelled_code = cfg['cancelled_code']
        self.lesson_cancelled_color = cfg['lesson_cancelled_color']
        self.lesson_irregular_color = cfg['lesson_irregular_color']
        self.inMaintenanceMode = cfg['inMaintenanceMode']

        # Schriftart laden
        try:
            self.font_huge = ImageFont.truetype(self.font, 72)  # Riesenschrift
            self.font_large = ImageFont.truetype(self.font, 52)  # Große Schrift für Fächer
            self.font_medium = ImageFont.truetype(self.font, 40)  # Mittlere Schrift für Klassen und Lehrer
            self.font_small = ImageFont.truetype(self.font, 26)  # Kleine Schrift für "generiert um" und Zeiten
        except IOError as e:
            print("Fonts konnten nicht geladen werden.", e)

    def get_logo_image(self):
        # Logo laden und positionieren
        path = self.cfg['tbz_logo_path']
        try:
            logo = Image.open(path).convert('L')  # Logo in Graustufen laden
            return logo.resize(
                (self.cfg['logo_size'][0], self.cfg['logo_size'][1]))  # Logo auf gewünschte Größe skalieren
        except FileNotFoundError:
            print(f"Logo-Datei in {path} nicht gefunden. Überspringe das Logo.")
            return Image.new('L', (0, 0), 0)

    @staticmethod
    def get_hour_and_minutes(time):
        hour = time[:-2]
        minutes = time[2:]

        return hour, minutes

    """formats the raw time depending on start or endtime"""

    def format_time(self, time, is_start_time):
        hour, minutes = self.get_hour_and_minutes(time)

        formatted_time = f'{hour}:{minutes}'
        if is_start_time:
            formatted_time += ' -'

        return formatted_time

    def get_lesson_duration_in_minutes(self, lesson):
        start_time = lesson['start']
        end_time = lesson['end']

        start_hour, start_minutes = self.get_hour_and_minutes(start_time)
        start_duration = start_hour * 60 + start_minutes

        end_hour, end_minutes = self.get_hour_and_minutes(end_time)
        end_duration = end_hour * 60 + end_minutes

        return end_duration - start_duration

    def generate_image(self, room, lessons, bottom_text=None):
        image = Image.new('L', self.size, self.background_color)
        draw = ImageDraw.Draw(image)

        # draw logo
        image.paste(self.get_logo_image(), (int(self.outside_margin), int(self.outside_margin)))

        # draw room and day
        if len(lessons) > 0:
            self.draw_room_and_day(lessons[0]['date'], draw, room, self.font_huge, 0)

        # draw bottom text
        if bottom_text is None:
            bottom_text = self.bottom_text

        #draw.text((self.outside_margin, self.size[1] - self.outside_margin), bottom_text, font=self.font_small,
         #         anchor="lm")

        # draw battery status
        image.paste(self.draw_battery_status(50), (self.outside_margin + self.lesson_rect_corner_radius//2, int(self.size[1] - self.battery_status_height - (self.outside_margin - self.battery_status_height/2))))

        # draw generated text
        self.draw_date_generated(draw, self.font_small, 0)

        # draw lesson rects
        if len(lessons) == 0:
            # keine stunden zum Anzeigen
            draw.text((image.width//2, 240), "Heute kein weiterer Unterricht", font=self.font_large, fill=0, anchor="mm")
            draw.text((image.width//2, 320), "in diesem Raum", font=self.font_large, fill=0, anchor="mm")
        elif len(lessons) > 6:
            # keine stunden zum Anzeigen
            draw.text((image.width//2, 240), "Mehr als 6 Stunden können", font=self.font_large, fill=0, anchor="mm")
            draw.text((image.width//2, 320), "nicht angezeigt werden.", font=self.font_large, fill=0, anchor="mm") 
        else:
            # check if dummy lessons need to be created
            if len(lessons) < 3:
                dummys_to_create = 3 - len(lessons)

                for _ in range(dummys_to_create):
                    lessons.append({
                        "is_dummy": True,
                        "anzahl": 2,
                    })
            previous_lesson_image_height = 0
            double_lesson_amount = 0
            lesson_amount = len(lessons)

            for lesson in lessons:
                if lesson["anzahl"] == 4:
                    double_lesson_amount += 1
                    lesson_amount += self.double_lesson_multiplier - 1

            for i, lesson in enumerate(lessons):
                """
                change spacing according to amount of lessons
                <= 4 -> spacing[0]
                > 4 -> spacing[1]
                >= 6 -> spacing[2]
                """
                spacing = self.lesson_rect_spacing[0]
                if lesson_amount <= 4:
                    spacing = self.lesson_rect_spacing[0]
                if lesson_amount > 4:
                    spacing = self.lesson_rect_spacing[1]
                if lesson_amount >= 6:
                    spacing = self.lesson_rect_spacing[2]


                if not 'is_dummy' in lesson:
                    # change color according to state (cancelled or not)
                    color = self.lesson_default_color

                    # change appearance if irregular lesson
                    if lesson['code'] == self.irregular_code:
                        color = self.lesson_irregular_color

                # generate lesson image
                lesson_image = self.generate_lesson_image(lesson, lesson_amount, double_lesson_amount, spacing, color)

                # paste lesson image on top of total image with offset depending on spacing and previous position of the lesson images
                image.paste(lesson_image,
                            (self.outside_margin, self.upper_margin + previous_lesson_image_height + spacing * i))
                previous_lesson_image_height += lesson_image.height

        self.save_image(image, room)


    def save_image(self, image, room):
        # Überprüfen, ob der Wartungsmodus false oder true ist:
        # Bild nach Raumname in ROMMIMAGES speichern
        path = self.image_path.replace("%ROOM%", room)

        if self.inMaintenanceMode:
            path = self.maintenance_path

        # create directories if needed
        directories = os.path.dirname(path)
        if not os.path.exists(directories):
            os.mkdir(directories)

        image.save(path)

    def generate_lesson_image(self, lesson, lesson_amount, double_lesson_amount, spacing, color):
        width = self.size[0] - self.outside_margin * 2

        # total image height - height of text above - the needed spacing between the lessons
        height = int((self.size[1] - self.bottom_margin - self.upper_margin) / lesson_amount)

        # subtract spacing from height so the lessons dont move up once spacing is added
        height -= spacing

        # adjust for remaining spacing at the bottom and the extra spacing of the double lessons
        height += int(spacing / lesson_amount) + int(((spacing * self.double_lesson_multiplier) - spacing) * double_lesson_amount / lesson_amount)

        # check if lesson is double
        if lesson["anzahl"] == 4:
            height = int(height * self.double_lesson_multiplier)

        # create image
        image = Image.new('L', (width, height), self.background_color)
        draw = ImageDraw.Draw(image)

        # dont draw dummy
        if 'is_dummy' in lesson:
            return image

        draw.rounded_rectangle([0, 0, width-1, height-1], fill=self.lesson_rect_background_color, outline=color, radius=self.lesson_rect_corner_radius,
                       width=self.lesson_rect_outline_width)

        # draw lesson texts
        self.draw_lesson_texts(lesson, draw, width, height, color)

        if lesson['code'] == self.cancelled_code:
            radius = self.lesson_rect_corner_radius//2
            draw.line([radius,radius, width-radius, height-radius], width=self.lesson_rect_outline_width, fill=self.lesson_rect_color)
            draw.line([width-radius, radius, radius, height-radius], width=self.lesson_rect_outline_width, fill=self.lesson_rect_color)

        return image

    def draw_lesson_texts(self, lesson, draw, lesson_rect_width, lesson_rect_height, color):
        # draw lesson texts
        start_time = self.format_time(lesson['start_time'], True)
        end_time = self.format_time(lesson['end_time'], False)

        # change data of lesson text in here if needed
        lesson_text_data = [
            {
                'text': f'{start_time}\n{end_time}',
                'font': self.font_small,
                'color': color,
                'align': 'left',
                'stroke_width': 0
            },
            {
                'text': lesson["klasse"],
                'font': self.font_medium,
                'color': color,
                'align': 'left',
                'stroke_width': 0
            },
            {
                'text': lesson["subject"],
                'font': self.font_large,
                'color': color,
                'align': 'left',
                'stroke_width': 0
            },
            {
                'text': lesson["teacher"],
                'font': self.font_medium,
                'color': color,
                'align': 'left',
                'stroke_width': 0
            }
        ]

        # add room change
        if lesson['room_changed']:
            lesson_text_data.insert(2, {
                'text': f'{lesson['classroom'].split('->')[1]}',
                'font': self.font_medium,
                'color': color,
                'align': 'center',
                'stroke_width': 1
        })

        text_amount = len(lesson_text_data)
        for i, lesson_text in enumerate(lesson_text_data):
            text = lesson_text['text']
            font = lesson_text['font']
            color = lesson_text['color']

            # align on x axis and center y axis
            x = lesson_rect_width - (lesson_rect_width // text_amount * (text_amount - i)) + (
                        lesson_rect_width // text_amount // 2)
            y = lesson_rect_height // 2

            # check for multiline
            if '\n' in lesson_text['text']:
                draw.multiline_text((x, y), text, font=font, fill=color, anchor="mm", align=lesson_text['align'], stroke_width=lesson_text['stroke_width'])
            else:
                draw.text((x, y), text, font=font, fill=color, anchor="mm", align=lesson_text['align'], stroke_width=lesson_text['stroke_width'])

    def draw_room_and_day(self, date, draw, room, font, color):
        current_day_num = datetime.strptime(date, '%Y-%m-%d').weekday()
        days = ["Montag", "Dienstag", "Mittwoch", "Donnerstag", "Freitag", "Samstag",
                "Sonntag"]

        room_day_text = f'{room} - {days[current_day_num]}'

        draw.text((self.size[0] - self.outside_margin, self.upper_margin // 2), room_day_text, font=font, fill=color,
                  anchor='rm')

    def draw_battery_status(self, charge):
        image = Image.new('L', (self.battery_status_width, self.battery_status_height), self.background_color)

        draw = ImageDraw.Draw(image)
        draw.rectangle([0,0, self.battery_status_width-1, self.battery_status_height-1], width=2, outline=2)

        draw.rectangle([3, 3, self.battery_status_width * (charge / 100) - 4, self.battery_status_height - 4], fill=0)

        return image

    def draw_date_generated(self, draw, font, color):
        # Aktuelle Zeit für den unteren Text
        current_time = datetime.now().strftime("%d.%m.%Y %H:%M Uhr")

        # Text in der untersten Zeile
        footer_text = f"Generiert: {current_time}"

        # align with bottom right
        draw.text((self.size[0] - self.outside_margin - self.lesson_rect_corner_radius/2, self.size[1] - self.outside_margin), footer_text, font=font,
                  fill=color, anchor='rm')

    @staticmethod
    def image_to_hex_string(image_path):
        with Image.open(image_path) as img:
            img = img.resize((400, 300)) 
            # convert image to black and white with threshhold
            thresh = 200
            fn = lambda x : 0 if x < thresh else 255
            gray_image = img.convert('L').point(fn, mode='1')
            gray_image.save("room_images/gray_image.png") 
            pixel_array = np.array(gray_image, dtype=np.uint8)
            pixel_array = (pixel_array > 0).astype(np.uint8)
            packed = np.packbits(pixel_array.flatten())
        return ', '.join('0x{:02x}'.format(byte) for byte in bytes(packed))

    @staticmethod
    def reduce_pixel_count(pixel_array):
        """Reduziert die Pixelanzahl um die Hälfte."""
        # Neues Array erstellen, das die Hälfte der Pixelanzahl hat
        reduced_array = pixel_array[::2]  # Nur jeden zweiten Pixel nehmen
        return reduced_array

    def get_image_path(self, room):
        return f'{os.path.dirname(self.image_path)}/{room}.png'
