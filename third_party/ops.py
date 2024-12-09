import os
import configparser


def get_db_path():
    config = configparser.ConfigParser()
    if os.getcwd().endswith("db_handlers"):
        path_to_config = os.path.join("..", "config", "cfg_file.ini")
    else:
        path_to_config = os.path.join("config", "cfg_file.ini")
    with open(path_to_config) as cfg_file:
        config.read_file(cfg_file)
        db_path = config["admin.db"]["db_path"]
    return db_path


def parse_pic_name_from_query_data(query_data, shape):
    if "]=[" not in query_data:
        return query_data
    L = []
    if shape == "shaped":
        L = ["type", "subtype", "filename"]
    elif shape == "common":
        L = ["type", "matirial", "color", "filename"]
    D = dict(zip(L, [filename[1:-1] for filename in query_data.split("=")]))
    return D['filename']


def gen_picture_path(filename: str, balloon_type="shaped"):
    config = configparser.ConfigParser()
    # os.chdir("..")
    cwd = os.getcwd()
    if not cwd.endswith("/balls_seller"):
        cwd = os.path.join(cwd, "balls_seller")
    cfg_path = os.path.join(cwd, "config")
    cfg_path = os.path.join(cfg_path, "cfg_file.ini")
    with open(cfg_path) as cfg_file:
        config.read_file(cfg_file)
        pictures_dir_path = os.path.join(cwd, config["balloon.pictures"]["pictures_dirname"])
        if balloon_type == "shaped":
            return os.path.join(
                os.path.join(pictures_dir_path, config["balloon.pictures"]["shaped_balls_dirname"]),
                filename
            )
        else:
            return os.path.join(
                os.path.join(pictures_dir_path, config["balloon.pictures"]["common_balls_dirname"]),
                filename
            )


def remove_last_segment_in_path(path: str):
    return path[:path.rfind(os.sep)]


if __name__ == "__main__":
    path = remove_last_segment_in_path('/home/user/dir/programming/python/Gleb/balls_seller/pictures/trash/cat4.png')
