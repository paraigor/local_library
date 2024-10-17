import json

from jinja2 import Environment, FileSystemLoader, select_autoescape
from livereload import Server
from more_itertools import chunked


def on_reload():
    with open("books.json", encoding="utf8") as file:
        books_json = file.read()

    books = json.loads(books_json)
    double_books = list(chunked(books, 2))

    env = Environment(
        loader=FileSystemLoader("template"),
        autoescape=select_autoescape(["html"]),
    )
    template = env.get_template("template.html")

    rendered_page = template.render(double_books=double_books)

    with open("index.html", "w", encoding="utf8") as file:
        file.write(rendered_page)


def main():
    on_reload()

    server = Server()
    server.watch("template/template.html", on_reload)
    server.serve(root=".")


if __name__ == "__main__":
    main()
