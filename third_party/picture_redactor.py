from PIL import Image
from PIL import ImageDraw
from PIL import ImageFont

import configparser, os


def add_sign_to_picture_and_save_to_trash(path: str, sign: str):
    config = configparser.ConfigParser()
    img = Image.open(path)
    I1 = ImageDraw.Draw(img)
    myFont = ImageFont.truetype('FreeMono.ttf', 90)
    I1.text((20, 30), sign, font=myFont, fill=(255, 0, 0), stroke_width=4, stroke_fill="black")
    cwd = os.getcwd()
    cfg_path = os.path.join(cwd, "config", "config.ini")
    with open(cfg_path) as cfg_file:
        config.read_file(cfg_file)
        trash_dir = os.path.join(*config["balloon.tmp_trash"]["shaped_balls_trash"].split("/"))
        trash_path = os.path.join(cwd, trash_dir, path.split(os.sep)[-1])
        img.save(trash_path)
    return trash_path


if __name__ == "__main__":
    add_sign_to_picture("/home/user/dir/programming/python/Gleb/balls_seller/pictures/tests/cat.jpg", "[1]")