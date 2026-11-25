"""Write the pages of `docs/wiki` as the GitHub wiki of the repository wants
them, in a clone of `kubescope-sdk.wiki.git`.

GitHub keeps a wiki in a repository of its own, whose pages are named by
their file and linked without the `.md`. The sources stay in `docs/wiki`
(they are reviewed with the code); this rewrites their names and links, adds
the `Home` page and the sidebar, and leaves the commit and the push to you:

    git clone git@github.com:dcotecnologia/kubescope-sdk.wiki.git ../kubescope-sdk.wiki
    python tools/sync_wiki.py ../kubescope-sdk.wiki
    cd ../kubescope-sdk.wiki
    git add -A && git commit -m "Update the wiki" && git push
"""

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SOURCE = ROOT / "docs" / "wiki"
REPOSITORY = "https://github.com/dcotecnologia/kubescope-sdk/blob/main"

PAGES = {
    "README.md": "Home",
    "1-pages-and-layouts.md": "Pages-and-layouts",
    "2-tables.md": "Tables",
    "3-buttons-fields-and-texts.md": "Buttons-fields-and-texts",
    "4-dialogs-and-menus.md": "Dialogs-and-menus",
    "5-notices-panels-and-search.md": "Notices-panels-and-search",
    "6-services.md": "Services",
    "7-chat.md": "A-chat-with-an-assistant",
    "8-testing.md": "Testing",
    "9-recipes.md": "Recipes",
    "10-reference.md": "Reference",
}
LINK = re.compile(r"\]\(([^)#\s]+)(#[^)\s]*)?\)")


def convert_link(match: re.Match[str]) -> str:
    """A link to a page of the wiki loses its `.md`; one to the rest of the
    repository becomes an address on GitHub."""
    target, anchor = match.group(1), match.group(2) or ""
    if target.startswith(("http://", "https://", "mailto:")):
        return match.group(0)
    if target in PAGES:  # a page beside this one
        return f"]({PAGES[target]}{anchor})"
    path = (SOURCE / target).resolve()
    try:
        relative = path.relative_to(ROOT)
    except ValueError:
        return match.group(0)
    return f"]({REPOSITORY}/{relative.as_posix()}{anchor})"


def convert(text: str) -> str:
    """The text of a page, with its links as the wiki has them."""
    return LINK.sub(convert_link, text)


def sidebar() -> str:
    lines = ["**KubeScope SDK**", "", "- [Home](Home)"]
    lines += [
        f"- [{name.replace('-', ' ')}]({name})" for name in list(PAGES.values())[1:]
    ]
    return "\n".join(lines) + "\n"


def build(destination: Path) -> list[Path]:
    """Write every page and the sidebar into `destination`."""
    written = []
    for source, name in PAGES.items():
        page = destination / f"{name}.md"
        page.write_text(convert((SOURCE / source).read_text("utf-8")), "utf-8")
        written.append(page)
    side = destination / "_Sidebar.md"
    side.write_text(sidebar(), "utf-8")
    written.append(side)
    return written


def main(arguments: list[str]) -> int:
    if len(arguments) != 1:
        print(__doc__)
        return 2
    destination = Path(arguments[0])
    if not destination.is_dir():
        print(f"{destination} is not a folder: clone the wiki there first.")
        return 1
    for page in build(destination):
        print("wrote", page)
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
