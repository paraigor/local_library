import argparse
import json
import math
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path
from urllib import parse

from jinja2 import Environment, FileSystemLoader, select_autoescape
from more_itertools import chunked


class web_server(BaseHTTPRequestHandler):
    def do_GET(self):
        try:
            # Reading the file
            file_to_open = open(self.path[1:]).read()
            self.send_response(200)
        except:
            file_to_open = "File not found"
            self.send_response(404)

        self.end_headers()
        self.wfile.write(bytes(file_to_open, "utf-8"))


def create_parser():
    parser = argparse.ArgumentParser(
        description="""Script for generating local website with downloaded books."""
    )
    parser.add_argument(
        "--books_db",
        type=Path,
        default=Path("books.json"),
        help="Path to json db file with information of downloaded books",
    )

    return parser


def main():
    parser = create_parser()
    args = parser.parse_args()

    file_path = args.books_db
    if file_path.exists():
        with open(file_path, encoding="utf8") as file:
            books = json.load(file)
    else:
        exit("Путь к файлу базы указан неверно")

    pages_folder = Path("pages")
    pages_folder.mkdir(exist_ok=True)
    books_num_on_page = 10
    total_pages = math.ceil(len(books) / books_num_on_page)
    books_by_pages = list(chunked(books, books_num_on_page))

    for page_num, books in enumerate(books_by_pages, 1):
        double_books = list(chunked(books, 2))

        env = Environment(
            loader=FileSystemLoader("template"),
            autoescape=select_autoescape(["html"]),
        )
        template = env.get_template("template.html")

        rendered_page = template.render(
            double_books=double_books,
            total_pages=total_pages,
            curr_page=page_num,
        )

        page_filename = f"index{page_num}.html"
        page_path = pages_folder / page_filename

        with open(page_path, "w", encoding="utf8") as file:
            file.write(rendered_page)

    server = HTTPServer(("localhost", 8080), web_server)
    print("Starting server, use <Ctrl-C> to stop")
    server.serve_forever()


if __name__ == "__main__":
    main()
