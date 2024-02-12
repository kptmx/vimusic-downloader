import argparse
import os.path
import sqlite3
from pathlib import Path

from pytube import YouTube


def main():
    parser = argparse.ArgumentParser(
        description=(
            "Vimusic-downloader: download all favorite tracks"
            "from ViMusic database (webm/opus format)"
        )
    )
    parser.add_argument('database', type=str, help='database file')
    args = parser.parse_args()

    if not os.path.isfile(args.database):
        print("File is not exist!")
        exit(1)

    db = sqlite3.connect(args.database)
    db.row_factory = sqlite3.Row
    cursor = db.cursor()

    cursor.execute("SELECT id FROM Song WHERE likedAt <> '' ")
    tracks = cursor.fetchall()

    cursor.execute("SELECT COUNT(likedAt) FROM Song")
    tracks_count = 0
    tracks_count1 = cursor.fetchall()  # костыляем

    # лютий костыль, потому что sqlite3.Row возвращает адрес в памяти,
    # если к нему обращаться напрямую
    for counts in tracks_count1:
        tracks_count = counts[0]

    musicdir = str(Path.home()) + "/Music/"
    if not os.path.exists(musicdir):
        os.mkdir(musicdir)

    print(f"Favorites: {str(tracks_count)} tracks")

    for count, track in enumerate(tracks):
        print("\nFetching info...")

        obj = YouTube.from_id(track[0])
        name = f"{obj.title} - {obj.author}"
        filename = f"{name}.webm"  # todo: выбор формата webm/m4a
        stream = obj.streams.get_by_itag(251)
        size = str(stream.filesize_mb)
        size_bytes = stream.filesize

        print(f"Downloading track: {name} ({count + 1} of {tracks_count})")
        print(f"Size: {str(size)} MB")

        # проверка на то что файл не битый и существует, иначе пропускаем
        if (
            os.path.isfile(musicdir + filename)
            and os.path.getsize(musicdir + filename) == size_bytes
        ):
            print("File exist, skipping...")
            continue

        stream.download(filename=filename, output_path=musicdir)

    db.close()


if __name__ == "__main__":
    main()
