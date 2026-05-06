import requests
from bs4 import BeautifulSoup
from urllib.parse import urlparse


def analyze_url(url):
    """
    Analiza una URL y devuelve datos SEO básicos.
    Esta función NO guarda en base de datos.
    Solo devuelve información limpia.
    """

    result = {
        "status_code": None,
        "title": "",
        "title_length": 0,
        "meta_description": "",
        "meta_description_length": 0,
        "h1": "",
        "h1_count": 0,
        "h2_count": 0,
        "images_total": 0,
        "images_without_alt": 0,
        "internal_links": 0,
        "external_links": 0,
        "canonical": "",
        "has_schema": False,
        "error_message": "",
    }

    try:
        response = requests.get(
            url,
            timeout=15,
            headers={
                "User-Agent": "ADBWebDesignSEOBot/1.0"
            }
        )

        result["status_code"] = response.status_code

        soup = BeautifulSoup(response.text, "html.parser")

        # Title
        title_tag = soup.find("title")
        if title_tag and title_tag.text:
            title = title_tag.text.strip()
            result["title"] = title
            result["title_length"] = len(title)

        # Meta description
        meta_description = soup.find("meta", attrs={"name": "description"})
        if meta_description and meta_description.get("content"):
            description = meta_description.get("content").strip()
            result["meta_description"] = description
            result["meta_description_length"] = len(description)

        # H1
        h1_tags = soup.find_all("h1")
        result["h1_count"] = len(h1_tags)

        if h1_tags:
            result["h1"] = h1_tags[0].get_text(strip=True)

        # H2
        h2_tags = soup.find_all("h2")
        result["h2_count"] = len(h2_tags)

        # Images
        images = soup.find_all("img")
        result["images_total"] = len(images)
        result["images_without_alt"] = len([
            img for img in images
            if not img.get("alt") or img.get("alt").strip() == ""
        ])

        # Links
        domain = urlparse(url).netloc
        links = soup.find_all("a", href=True)

        internal_links = 0
        external_links = 0

        for link in links:
            href = link.get("href")

            if href.startswith("#") or href.startswith("mailto:") or href.startswith("tel:"):
                continue

            parsed_href = urlparse(href)

            if parsed_href.netloc == "" or parsed_href.netloc == domain:
                internal_links += 1
            else:
                external_links += 1

        result["internal_links"] = internal_links
        result["external_links"] = external_links

        # Canonical
        canonical = soup.find("link", rel="canonical")
        if canonical and canonical.get("href"):
            result["canonical"] = canonical.get("href").strip()

        # Schema JSON-LD
        schema_tags = soup.find_all("script", type="application/ld+json")
        result["has_schema"] = len(schema_tags) > 0

    except requests.RequestException as error:
        result["error_message"] = str(error)

    return result