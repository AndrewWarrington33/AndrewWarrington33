import os
import re
from scholarly import scholarly, ProxyGenerator

SCHOLAR_ID = "ijSPbT0AAAAJ"

pg = ProxyGenerator()
pg.ScraperAPI(os.environ["SCRAPER_API_KEY"])
scholarly.use_proxy(pg)
README_PATH = "README.md"
START_MARKER = "<!-- SCHOLAR-START -->"
END_MARKER = "<!-- SCHOLAR-END -->"


def fetch_publications():
    author = scholarly.search_author_id(SCHOLAR_ID)
    author = scholarly.fill(author, sections=["publications"])

    pubs = []
    for pub in author["publications"]:
        bib = pub.get("bib", {})
        title = bib.get("title", "Untitled")
        year = bib.get("pub_year", "")
        venue = bib.get("venue", "") or bib.get("journal", "") or bib.get("conference", "")
        citations = pub.get("num_citations", 0)
        pub_id = pub.get("author_pub_id", "")
        url = f"https://scholar.google.com/citations?view_op=view_citation&user={SCHOLAR_ID}&citation_for_view={pub_id}"
        pubs.append((title, year, venue, citations, url))

    pubs.sort(key=lambda x: (-(int(x[1]) if x[1] else 0), -x[3]))
    return pubs


def format_publications(pubs):
    lines = []
    for title, year, venue, citations, url in pubs:
        parts = [f"[{title}]({url})"]
        if year:
            parts.append(f"({year})")
        if venue:
            parts.append(f"*{venue}*")
        if citations > 0:
            parts.append(f"{citations} citations")
        lines.append("- " + " · ".join(parts))
    return "\n".join(lines)


def update_readme(content):
    with open(README_PATH, "r") as f:
        readme = f.read()

    new_section = f"{START_MARKER}\n{content}\n{END_MARKER}"
    pattern = re.escape(START_MARKER) + r".*?" + re.escape(END_MARKER)
    updated = re.sub(pattern, new_section, readme, flags=re.DOTALL)

    with open(README_PATH, "w") as f:
        f.write(updated)


if __name__ == "__main__":
    print("Fetching publications from Google Scholar...")
    pubs = fetch_publications()
    content = format_publications(pubs)
    update_readme(content)
    print(f"Updated README with {len(pubs)} publications.")
