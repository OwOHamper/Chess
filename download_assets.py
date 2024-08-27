import requests, os
from alive_progress import alive_bar
import time
from InquirerPy import prompt

base_url = "https://images.chesscomfiles.com/"
board_url = base_url + "chess-themes/boards/{set}/150.png"
pieces_url = base_url + "chess-themes/pieces/{set}/150/{color}{piece}.png"
audio_url = base_url + "chess-themes/sounds/_{file_type_upper}_/default/{sound}.{file_type}"


pieces_sets = ["8-Bit", "Alpha", "Bases", "Blindfold", "Book", "Bubblegum", "Cases", "Classic", "Club", "Condal", "Dash", "Game Room", "Glass", "Gothic", "Graffiti", "Icy Sea", "Light", "Lolz", "Marble", "Maya", "Metal", "Modern", "Nature", "Neon", "Neo", "Neo-Wood", "Newspaper", "Ocean", "Sky", "Space", "Tigers", "Tournament", "Vintage", "Wood"]
board_sets = ["8-Bit", "Bases", "Blue", "Brown", "Bubblegum", "Burled Wood", "Dark Wood", "Dash", "Glass", "Graffiti", "Green", "Icy Sea", "Light", "Lolz", "Marble", "Metal", "Neon", "Newspaper", "Orange", "Overlay", "Parchment", "Purple", "Red", "Sand", "Sky", "Stone", "Tan", "Tournament", "Translucent", "Walnut"]
sounds = ["game-start", "game-end", "capture", "castle", "premove", "move-self", "move-check", "move-opponent", "promote", "notify", "tenseconds", "illegal"]

pieces_sets = [i.lower().replace(" ", "_").replace("-", "_") for i in pieces_sets]
board_sets = [i.lower().replace(" ", "_").replace("-", "_") for i in board_sets]

def create_folder(path):
    if not os.path.exists(path):
        os.makedirs(path)



def download_board_assets():
    create_folder(f"./assets/boards")
    with alive_bar(len(board_sets)) as bar:
        for board_set in board_sets:
            url = board_url.format(set=board_set)
            r = requests.get(url)
            if not r.ok:
                print(f"Error: {url} - {r.status_code} - {r.reason}")
                time.sleep(5)
                r = requests.get(url)
            with open(f"./assets/boards/{board_set}.png", "wb") as f:
                f.write(r.content)
            bar()

def download_piece_assets():
    create_folder(f"./assets/pieces")
    for piece_set in pieces_sets:
        create_folder(f"./assets/pieces/{piece_set}")

    with alive_bar(len(pieces_sets) * 12) as bar:
        for piece_set in pieces_sets:
            for color in ["w", "b"]:
                for piece in ["k", "q", "p", "n", "b", "r"]:
                    url = pieces_url.format(set=piece_set, color=color, piece=piece)
                    r = requests.get(url)
                    if not r.ok:
                        print(f"Error: {url} - {r.status_code} - {r.reason}")
                        time.sleep(5)
                        r = requests.get(url)
                    with open(f"./assets/pieces/{piece_set}/{color}{piece}.png", "wb") as f:
                        f.write(r.content)
                    bar()

def download_sound_assets(file_type):
    create_folder(f"./assets/audio")

    with alive_bar(len(sounds)) as bar:
        for sound in sounds:
            url = audio_url.format(file_type_upper=file_type.upper(), sound=sound, file_type=file_type)
            r = requests.get(url)
            if not r.ok:
                print(f"Error: {url} - {r.status_code} - {r.reason}")
                time.sleep(5)
                r = requests.get(url)
            with open(f"./assets/audio/{sound}.{file_type}", "wb") as f:
                f.write(r.content)
            bar()



def download_assets():
    print("Downloading board assets...")
    download_board_assets()
    print("Downloading pieces assets...")
    download_piece_assets()
    file_type = input("What file type do you want to download? (mp3, ogg, wav): ")
    print("Downloading sound assets...")
    download_sound_assets(file_type=file_type)


questions = [{
    "type": "list",
    "name": "action",
    "message": "What do you want to do?",
    "choices": [
        "Download board assets",
        "Download pieces assets",
        "Download sound assets",
        "Download all assets",
        "Exit"
    ]
}]

try:
    while True:
        answer = prompt(questions)
        if answer["action"] == "Download board assets":
            print("Downloading board assets...")
            download_board_assets()
        elif answer["action"] == "Download pieces assets":
            print("Downloading pieces assets...")
            download_piece_assets()
        elif answer["action"] == "Download sound assets":
            file_type = input("What file type do you want to download? (mp3, ogg, wav): ")
            print("Downloading sound assets...")
            download_sound_assets(file_type)
        elif answer["action"] == "Download all assets":
            print("Downloading all assets...")
            download_assets()
        elif answer["action"] == "Exit":
            print("Exiting...")
            exit()
except KeyboardInterrupt:
    print("Exiting...")
    exit()