import argparse
import csv
import logging
import random
import time
from datetime import datetime

import requests
from bs4 import BeautifulSoup

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


def generate_url(domain: str, page: int, all_languages: bool) -> str:
    """
    Generate the URL for the given domain and page number.
    :param domain: The domain to get the reviews for.
    :param page: The page number.
    :param all_languages: Whether to get reviews in all languages.
    :return: The URL for the given domain and page number.
    """
    url = f"https://www.trustpilot.com/review/{domain}?page={page}"
    if all_languages:
        url += "&languages=all"
    return url


def get_html(url: str) -> BeautifulSoup:
    """
    Get the HTML content of the given URL.
    :param url: The URL to get the HTML content from.
    :return: BeautifulSoup object containing the HTML content.
    """
    headers = {
        "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko)"
    }
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        return BeautifulSoup(response.content, "lxml")
    response.raise_for_status()


def get_reviews(html: BeautifulSoup) -> list[dict]:
    """
    Get the reviews from the BeautifulSoup object containing the HTML content.
    :param html: BeautifulSoup object containing the HTML content.
    :return: List of dictionaries containing the review details.
    """
    page_reviews = []
    for review_div in html.find_all(
        "div",
        class_="styles_cardWrapper__LcCPA styles_show__HUXRb styles_reviewCard__9HxJJ",
    ):
        review = {}

        # Get name of the reviewer
        rating_span = review_div.find("span", {"data-consumer-name-typography": True})
        if rating_span:
            review["name"] = rating_span.text

        # Get the review count of the reviewer
        review_count_div = review_div.find("div", {"data-consumer-reviews-count": True})
        if review_count_div:
            review["review_count"] = int(
                review_count_div["data-consumer-reviews-count"]
            )

        # Get the country of the reviewer
        country_element = review_div.find(
            "div", {"data-consumer-country-typography": "true"}
        )
        if country_element:
            # The country code or name might be in the next span element after the SVG
            country_code_span = country_element.find_next("span")
            if country_code_span:
                review["country"] = country_code_span.text.strip()

        # Get the rating of the review
        rating_div = review_div.find("div", {"data-service-review-rating": True})
        if rating_div:
            review["rating"] = int(rating_div["data-service-review-rating"])

        # Get the review date
        review_date_time = review_div.find(
            "time", {"data-service-review-date-time-ago": True}
        )
        if review_date_time:
            review["review_date"] = datetime.fromisoformat(review_date_time["datetime"])

        # Get the title of the review
        title_h2 = review_div.find("h2", {"data-service-review-title-typography": True})
        if title_h2:
            review["title"] = title_h2.text.strip()

        # Get the content of the review
        content_p = review_div.find("p", {"data-service-review-text-typography": True})
        if content_p:
            review["content"] = content_p.text.strip()

        # Get the date of the experience
        date_of_experience_p = review_div.find(
            "p", {"data-service-review-date-of-experience-typography": True}
        )
        if date_of_experience_p:
            date_of_experience_str = date_of_experience_p.text.split(":")[-1].strip()
            review["date_of_experience"] = datetime.strptime(
                date_of_experience_str, "%B %d, %Y"
            )

        page_reviews.append(review)

    return page_reviews


def write_reviews_to_csv(reviews: list[dict], filename: str):
    """
    Write the reviews to a CSV file.
    :param reviews: List of dictionaries containing the review details.
    :param filename: The name of the CSV file to write the reviews to.
    """
    with open(filename, "w", newline="") as file:
        writer = csv.DictWriter(
            file,
            fieldnames=[
                "name",
                "review_count",
                "country",
                "rating",
                "review_date",
                "title",
                "content",
                "date_of_experience",
            ],
        )
        writer.writeheader()
        writer.writerows(reviews)


def main():
    parser = argparse.ArgumentParser(description="Scrape reviews from Trustpilot for a given domain.")
    parser.add_argument("domain", help="The domain to scrape reviews for.", type=str)
    args = parser.parse_args()

    domain = args.domain
    page = 1
    reviews = []
    all_languages = True

    while True:
        try:
            url = generate_url(domain, page, all_languages)
            html = get_html(url)
            page_reviews = get_reviews(html)
            logger.info(f"Found {len(page_reviews)} reviews on page {page}")
            reviews.extend(page_reviews)
            page += 1
            time.sleep(random.randint(5, 10) / 10)
        except requests.exceptions.HTTPError:
            logger.info(f"Reached the last page for {domain}")
            break

    write_reviews_to_csv(reviews, f"reviews_{domain}.csv")
    logger.info(f"Scraped {len(reviews)} reviews for {domain}")


if __name__ == "__main__":
    main()
