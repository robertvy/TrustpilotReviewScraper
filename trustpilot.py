import argparse
import csv
import json
import logging
import random
import sys
import time
from datetime import datetime
from urllib.parse import parse_qs, urlparse
from urllib.robotparser import RobotFileParser

import requests
from bs4 import BeautifulSoup
from fake_useragent import UserAgent

logging.basicConfig(
    level=logging.DEBUG, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

session = requests.Session()


def parse_arguments() -> argparse.Namespace:
    """
    Parses command-line arguments.
    :return: Namespace object with parsed command-line arguments.
    """
    parser = argparse.ArgumentParser(
        description="Scrape reviews from Trustpilot for a given domain."
    )
    parser.add_argument("domain", help="The domain to scrape reviews for.", type=str)
    parser.add_argument(
        "--stars",
        nargs="*",
        help="Filter reviews by stars. Accept multiple values (e.g., --stars 4 5).",
        type=int,
    )
    parser.add_argument(
        "--date",
        help="Filter reviews by date (e.g., last30days, last3months, last6months).",
        type=str,
    )
    parser.add_argument("--search", help="Filter reviews by search keyword.", type=str)
    parser.add_argument(
        "--languages",
        help="Filter reviews by language (e.g., es for Spanish, all for all languages).",
        type=str,
        default="all",
    )
    parser.add_argument(
        "--verified",
        action="store_true",
        help="Filter reviews to show only verified reviews.",
    )
    parser.add_argument(
        "--replies",
        action="store_true",
        help="Filter reviews to show only reviews with replies.",
    )
    parser.add_argument(
        "--sort-by",
        help="Sort reviews by a specified field (e.g., 'rating', 'date').",
        type=str,
        default="published_date",
    )
    parser.add_argument(
        "--sort-order",
        choices=["asc", "desc"],
        default="asc",
        help="Sort order: 'asc' for ascending, 'desc' for descending. Default is ascending.",
    )
    parser.add_argument(
        "--output",
        choices=["csv", "json", "both"],
        default="csv",
        help="Specify the output format: 'csv' for CSV file, 'json' for JSON file, or 'both' for both formats. Default is 'csv'.",
    )

    return parser.parse_args()


def generate_url(domain: str, page: int, args) -> str:
    """
    Generate the URL for the given domain, page number, and additional filters in a more concise manner.
    :param domain: The domain to get the reviews for.
    :param page: The page number.
    :param args: Parsed command-line arguments containing filters.
    :return: The URL for the given domain and page number with query parameters.
    """
    base_url = f"https://www.trustpilot.com/review/{domain}"
    params = {"page": page} if page != 1 else {}

    if args.stars:
        for star in args.stars:
            params[f"stars"] = star
    if args.date:
        params["date"] = args.date
    if args.search:
        params["search"] = args.search
    if args.languages:
        params["languages"] = args.languages
    if args.verified:
        params["verified"] = "true"
    if args.replies:
        params["replies"] = "true"

    query_string = "&".join([f"{key}={value}" for key, value in params.items()])
    return f"{base_url}?{query_string}" if params else base_url


def is_allowed_by_robots_txt(url: str, user_agent: str) -> bool:
    """
    Check if the given user agent is allowed to scrape the URL according to robots.txt rules.
    :param url: The base URL of the website to check.
    :param user_agent: The User-Agent string of the scraper.
    :return: True if allowed, False otherwise.
    """
    parser = RobotFileParser()
    parser.set_url(f"{url}/robots.txt")
    parser.read()
    return parser.can_fetch(user_agent, url)


def iso_to_datetime(iso_str: str) -> datetime | None:
    """
    Convert an ISO 8601 formatted string to a datetime object.
    :param iso_str: The ISO 8601 formatted string.
    :return: The datetime object.
    """
    if iso_str:
        # Remove the 'Z' and convert to datetime
        return datetime.fromisoformat(iso_str.replace("Z", "+00:00"))
    return None


def get_html(url: str) -> BeautifulSoup | None:
    """
    Get the HTML content of the given URL using a persistent session.
    :param url: The URL to get the HTML content from.
    :return: BeautifulSoup object containing the HTML content.
    """
    ua = UserAgent()
    session.headers.update({"User-Agent": ua.random})
    response = session.get(url)

    final_url = response.url
    initial_params = parse_qs(urlparse(url).query)
    final_params = parse_qs(urlparse(final_url).query)
    if len(initial_params) > 1 and initial_params != final_params:
        logger.error(f"Redirected to {final_url}. Unexpected redirection detected.")
        sys.exit(1)

    if response.status_code == 404:
        return None

    if response.status_code == 200:
        html_content = BeautifulSoup(response.content, "lxml")
        return html_content
    response.raise_for_status()


def get_reviews_data(html: BeautifulSoup) -> list[dict]:
    """
    Get the reviews data from the HTML content.
    :param html: BeautifulSoup object containing the HTML content.
    :return: List of dictionaries containing the review data.
    """
    script_tag = html.find("script", {"id": "__NEXT_DATA__"})
    return json.loads(script_tag.string)["props"]["pageProps"]["reviews"]


def parse_review(review: dict) -> dict:
    """
    Parse the review data and extract the relevant information.
    :param review: Dictionary containing the raw review data.
    :return: Dictionary containing the processed review data.
    """
    parsed_review = {
        "id": review.get("id"),
        "filtered": review.get("filtered"),
        "pending": review.get("pending"),
        "text": review.get("text"),
        "rating": review.get("rating"),
        "title": review.get("title"),
        "likes": review.get("likes"),
        "report": review.get("report"),
        "has_unhandled_reports": review.get("hasUnhandledReports"),
        "language": review.get("language"),
        "location": review.get("location"),
        "consumers_review_count_on_same_domain": review.get(
            "consumersReviewCountOnSameDomain"
        ),
        "consumers_review_count_on_same_location": review.get(
            "consumersReviewCountOnSameLocation"
        ),
    }

    # Date information
    dates = review.get("dates", {})
    parsed_review["published_date"] = iso_to_datetime(dates.get("publishedDate"))
    parsed_review["experienced_date"] = iso_to_datetime(dates.get("experiencedDate"))
    parsed_review["updated_date"] = iso_to_datetime(dates.get("updatedDate"))

    # Consumer information
    consumer = review.get("consumer", {})
    parsed_review["display_name"] = consumer.get("displayName")
    parsed_review["image_url"] = consumer.get("imageUrl")
    parsed_review["review_count"] = consumer.get("numberOfReviews")
    parsed_review["country_code"] = consumer.get("countryCode")
    parsed_review["has_image"] = consumer.get("hasImage")
    parsed_review["consumer_verified"] = consumer.get("isVerified")

    # Verification labels
    labels = review.get("labels", {}).get("verification", {})
    parsed_review["review_verified"] = labels.get("isVerified")
    parsed_review["review_verification_level"] = labels.get("verificationLevel")
    parsed_review["review_verification_source"] = labels.get("verificationSource")
    parsed_review["review_verification_date"] = labels.get("createdDateTime")
    parsed_review["review_source_name"] = labels.get("reviewSourceName")
    parsed_review["has_dach_exclusion"] = labels.get("hasDachExclusion")

    # Reply information
    reply = review.get("reply")
    if reply:
        parsed_review["reply_message"] = reply.get("message")
        parsed_review["reply_published_date"] = iso_to_datetime(
            reply.get("publishedDate")
        )
        parsed_review["reply_updated_date"] = iso_to_datetime(reply.get("updatedDate"))
    else:
        parsed_review["reply_message"] = None
        parsed_review["reply_published_date"] = None
        parsed_review["reply_updated_date"] = None

    return parsed_review


def process_reviews(reviews_data: list[dict]) -> list[dict]:
    """
    Process the reviews data and extract the relevant information.
    :param reviews_data: List of dictionaries containing the raw review data.
    :return: List of dictionaries containing the processed review data.
    """
    return [parse_review(review) for review in reviews_data]


def write_reviews_to_csv(reviews: list[dict], filename: str) -> None:
    """
    Write the reviews to a CSV file.
    :param reviews: List of dictionaries containing the review details.
    :param filename: The name of the CSV file to write the reviews to.
    """
    with open(filename, "w", newline="") as file:
        writer = csv.DictWriter(
            file,
            fieldnames=[
                "id",
                "filtered",
                "pending",
                "text",
                "rating",
                "title",
                "likes",
                "report",
                "has_unhandled_reports",
                "language",
                "location",
                "consumers_review_count_on_same_domain",
                "consumers_review_count_on_same_location",
                "published_date",
                "experienced_date",
                "updated_date",
                "display_name",
                "image_url",
                "review_count",
                "country_code",
                "has_image",
                "consumer_verified",
                "review_verified",
                "review_verification_level",
                "review_verification_source",
                "review_verification_date",
                "review_source_name",
                "has_dach_exclusion",
                "reply_message",
                "reply_published_date",
                "reply_updated_date",
            ],
        )
        writer.writeheader()
        writer.writerows(reviews)


def datetime_converter(o: object) -> str:
    """
    Convert a datetime object to a string.
    :param o: The object to convert.
    :return: The string representation of the object.
    """
    if isinstance(o, datetime):
        return o.isoformat()
    raise TypeError(
        "Object of type '{}' is not JSON serializable".format(o.__class__.__name__)
    )


def write_reviews_to_json(reviews: list[dict], filename: str) -> None:
    """
    Write the reviews to a JSON file, converting datetime objects to strings.
    :param reviews: List of dictionaries containing the review details.
    :param filename: The name of the JSON file to write the reviews to.
    """
    # Convert datetime objects to strings
    reviews_converted = []
    for review in reviews:
        review_converted = {
            key: datetime_converter(value) if isinstance(value, datetime) else value
            for key, value in review.items()
        }
        reviews_converted.append(review_converted)

    with open(filename, "w") as file:
        json.dump(reviews_converted, file, indent=4)


def sort_reviews(reviews: list[dict], sort_by: str, sort_order: str) -> list[dict]:
    """
    Sort the reviews by a specified field in ascending or descending order.
    :param reviews: List of dictionaries containing the review details.
    :param sort_by: The field to sort the reviews by.
    :param sort_order: The order to sort the reviews in ('asc' for ascending, 'desc' for descending).
    :return: List of dictionaries containing the sorted review details.
    """
    reverse = sort_order == "desc"
    if sort_by and any(review.get(sort_by) for review in reviews):
        return sorted(reviews, key=lambda x: x.get(sort_by, 0), reverse=reverse)
    return reviews


def main():
    args = parse_arguments()
    domain = args.domain
    page = 1
    reviews = []

    # Check if allowed by robots.txt
    ua = UserAgent()
    user_agent = ua.random
    if not is_allowed_by_robots_txt(
        f"https://www.trustpilot.com/review/{domain}", user_agent
    ):
        logger.error("Scraping is disallowed by robots.txt.")
        return

    while True:
        try:
            url = generate_url(domain, page, args)
            html = get_html(url)
            if html is None:
                logger.info(f"Page {page} does not exist. Stopping.")
                break
            page_reviews = get_reviews_data(html)
            logger.info(f"Found {len(page_reviews)} reviews on page {page}")
            if not page_reviews:
                break
            page_reviews = process_reviews(page_reviews)
            reviews.extend(page_reviews)
            page += 1
            time.sleep(random.randint(5, 10) / 10)
        except requests.exceptions.HTTPError as e:
            logger.error(f"Error fetching page {page}: {e}")
            break

    if args.sort_by:
        logger.debug(f"Sorting reviews by {args.sort_by} in {args.sort_order} order.")
        reviews = sort_reviews(reviews, args.sort_by, args.sort_order)

    if reviews:
        current_timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        if args.output == "csv" or args.output == "both":
            csv_filename = f"reviews_{args.domain}_{current_timestamp}.csv"
            write_reviews_to_csv(reviews, csv_filename)
            logger.info(f"Reviews saved to CSV file {csv_filename}")

        if args.output == "json" or args.output == "both":
            json_filename = f"reviews_{args.domain}_{current_timestamp}.json"
            write_reviews_to_json(reviews, json_filename)
            logger.info(f"Reviews saved to JSON file {json_filename}")
    else:
        logger.info("No reviews scraped.")


if __name__ == "__main__":
    main()
