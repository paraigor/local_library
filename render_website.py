import json

from jinja2 import Environment, FileSystemLoader, select_autoescape


def main():
    with open("books.json", "r", encoding="utf8") as file:
        books_json = file.read()

    books = json.loads(books_json)

    env = Environment(
        loader=FileSystemLoader("template"),
        autoescape=select_autoescape(["html"]),
    )
    template = env.get_template("index.html")

    rendered_page = template.render(books=books)

    with open("index.html", "w", encoding="utf8") as file:
        file.write(rendered_page)


if __name__ == "__main__":
    main()
