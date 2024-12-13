import argparse
import csv
import json
import logging
import random
import sys
import time
from collections import defaultdict
from datetime import datetime
from urllib.parse import parse_qs, urlparse
from urllib.robotparser import RobotFileParser

import matplotlib.pyplot as plt
import requests
from bs4 import BeautifulSoup
from fake_useragent import UserAgent
from scipy.stats import pearsonr
from sklearn.feature_extraction.text import CountVectorizer

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
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
    parser.add_argument("--analyze", action="store_true", help="Analyze correlation between ratings and keywords.")
    parser.add_argument("--visualize", action="store_true", help="Group reviews by location and visualize trends.")
    parser.add_argument("--retry", action="store_true", help="Enable retry logic for slow-loading or dynamic pages.")
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
    params = {}

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

    if page > 1:
        params["page"] = page

    query_string = "&".join([f"{key}={value}" for key, value in params.items()])
    return f"{base_url}?{query_string}" if params else base_url


def get_html_with_retry(url: str, retry_enabled: bool) -> BeautifulSoup | None:
    if retry_enabled:
        retries = 3
        for attempt in range(retries):
            try:
                return get_html(url)
            except requests.exceptions.RequestException:
                logger.warning(f"Retrying ({attempt + 1}/{retries})...")
                time.sleep(random.randint(1, 3))
    return get_html(url)


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
    with open(filename, "w", newline="", encoding="utf-8-sig") as file:
        writer = csv.DictWriter(
            file,
            delimiter=";",
            quoting=csv.QUOTE_MINIMAL,
            fieldnames=[
                "id",
                "display_name",
                "country_code",
                "title",
                "text",
                "rating",
                "likes",
                "language",
                "consumers_review_count_on_same_domain",
                "published_date",
                "experienced_date",
                "updated_date",
                "review_count",
                "consumer_verified",
                "image_url",
                "has_image",
                "review_verified",
                "review_verification_level",
                "review_verification_source",
                "review_verification_date",
                "review_source_name",
                "has_dach_exclusion",
                "reply_message",
                "reply_published_date",
                "reply_updated_date",
                "filtered",
                "pending",
                "report",
                "has_unhandled_reports",
                "location",
                "consumers_review_count_on_same_location",
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
        if sort_by in ["published_date", "experienced_date", "updated_date"]:
            return sorted(
                reviews,
                key=lambda x: x.get(sort_by) or datetime.min,
                reverse=reverse,
            )
        else:
            return sorted(reviews, key=lambda x: x.get(sort_by, 0), reverse=reverse)
    return reviews


def group_reviews_by_location(reviews: list[dict], reviews_by_location: dict):
    for review in reviews:
        location = review.get("location") or "Unknown"
        if location not in reviews_by_location:
            reviews_by_location[location] = []
        reviews_by_location[location].append(review["rating"])


def visualize_reviews_by_location(reviews_by_location: dict, output_file: str):
    import matplotlib.pyplot as plt
    averages = {loc: sum(ratings) / len(ratings) for loc, ratings in reviews_by_location.items()}
    locations = list(averages.keys())
    avg_ratings = list(averages.values())
    plt.figure(figsize=(10, 6))
    plt.barh(locations, avg_ratings, color='teal')
    plt.xlabel("Average Rating")
    plt.ylabel("Location")
    plt.title("Average Rating by Location")
    plt.savefig(output_file)
    plt.close()


def analyze_keywords(review: dict, keyword_analysis: dict):
    import re
    text = review.get("text", "")
    rating = review.get("rating")
    if not text or not rating:
        return
    words = re.findall(r'\w+', text.lower())
    for word in words:
        if word not in keyword_analysis:
            keyword_analysis[word] = {"total_rating": 0, "count": 0}
        keyword_analysis[word]["total_rating"] += rating
        keyword_analysis[word]["count"] += 1


def save_keyword_analysis(keyword_analysis: dict, output_file: str):
    with open(output_file, "w", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)
        writer.writerow(["Keyword", "Average Rating", "Count"])
        for keyword, data in keyword_analysis.items():
            avg_rating = data["total_rating"] / data["count"] if data["count"] else 0
            writer.writerow([keyword, avg_rating, data["count"]])


def identify_review_platform():
    """
    Xác định và kiểm tra nền tảng đánh giá
    """
    review_platforms = {
        'Trustpilot': 'https://www.trustpilot.com',
        'Google Reviews': 'https://www.google.com/maps/reviews',
        'Yelp': 'https://www.yelp.com',
        'Amazon Reviews': 'https://www.amazon.com/reviews'
    }

    # Thêm logic kiểm tra khả năng truy cập và cấu trúc trang web
    return review_platforms


def handle_pagination_and_lazy_loading(url):
    """
    Xử lý các trường hợp phân trang và tải chậm
    """
    max_retries = 3
    retry_delay = 2

    for attempt in range(max_retries):
        try:
            # Sử dụng Selenium để xử lý tải động
            from selenium import webdriver
            from selenium.webdriver.common.by import By
            from selenium.webdriver.support.ui import WebDriverWait
            from selenium.webdriver.support import expected_conditions as EC

            driver = webdriver.Chrome()  # Hoặc trình duyệt khác
            driver.get(url)

            # Chờ các phần tử tải
            WebDriverWait(driver, 10).until(
                EC.presence_of_all_elements_located((By.CLASS_NAME, 'review-element'))
            )

            # Cuộn trang để tải thêm nội dung
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")

            return driver.page_source

        except Exception as e:
            logger.error(f"Pagination error (Attempt {attempt + 1}): {e}")
            time.sleep(retry_delay)

    return None


def analyze_rating_keyword_correlation(reviews):
    """
    Phân tích tương quan giữa xếp hạng và từ khóa
    """
    # Trích xuất văn bản và xếp hạng
    texts = [review['text'] for review in reviews if review['text']]
    ratings = [review['rating'] for review in reviews if review['text']]

    # Sử dụng CountVectorizer để trích xuất từ khóa
    vectorizer = CountVectorizer(stop_words='english', max_features=50)
    X = vectorizer.fit_transform(texts)
    keywords = vectorizer.get_feature_names_out()

    # Tính tương quan Pearson
    correlations = []
    for i, keyword in enumerate(keywords):
        keyword_counts = X[:, i].toarray().flatten()
        correlation, p_value = pearsonr(keyword_counts, ratings)
        correlations.append((keyword, correlation, p_value))

    # Sắp xếp và in các từ khóa có tương quan mạnh
    correlations.sort(key=lambda x: abs(x[1]), reverse=True)
    return correlations[:10]


def group_and_visualize_reviews_by_location(reviews):
    """
    Nhóm và trực quan hóa đánh giá theo vị trí địa lý
    """
    # Nhóm đánh giá theo quốc gia
    location_groups = defaultdict(list)
    for review in reviews:
        country = review.get('country_code', 'Unknown')
        location_groups[country].append(review)

    # Tạo biểu đồ phân bố đánh giá theo quốc gia
    countries = list(location_groups.keys())
    review_counts = [len(reviews) for reviews in location_groups.values()]
    average_ratings = [
        sum(review['rating'] for review in reviews) / len(reviews)
        for reviews in location_groups.values()
    ]

    plt.figure(figsize=(12, 6))
    plt.bar(countries, review_counts)
    plt.title('Số lượng đánh giá theo quốc gia')
    plt.xlabel('Quốc gia')
    plt.ylabel('Số lượng đánh giá')
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.savefig('reviews_by_country.png')

    # Biểu đồ xếp hạng trung bình
    plt.figure(figsize=(12, 6))
    plt.bar(countries, average_ratings)
    plt.title('Xếp hạng trung bình theo quốc gia')
    plt.xlabel('Quốc gia')
    plt.ylabel('Xếp hạng trung bình')
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.savefig('average_ratings_by_country.png')

    return location_groups


def main():
    args = parse_arguments()
    domain = args.domain
    page = 1
    reviews = []

    reviews_by_location = {}
    keyword_analysis = {}

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
            html = get_html_with_retry(url, args.retry)
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

            if args.analyze:
                for review in page_reviews:
                    analyze_keywords(review, keyword_analysis)

            if args.visualize:
                group_reviews_by_location(page_reviews, reviews_by_location)
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
    if args.analyze and keyword_analysis:
        save_keyword_analysis(keyword_analysis, f"keyword_analysis_{current_timestamp}.csv")
        logger.info("Keyword analysis completed and saved.")

    if args.visualize and reviews_by_location:
        visualize_reviews_by_location(reviews_by_location, f"review_trends_{current_timestamp}.png")
        logger.info("Review visualization completed and saved.")
    else:
        logger.info("No reviews scraped.")
    keyword_correlations = analyze_rating_keyword_correlation(reviews)
    logger.info("Top keyword correlations:")
    for keyword, corr, p_val in keyword_correlations:
        logger.info(f"Keyword: {keyword}, Correlation: {corr}, P-value: {p_val}")
    location_groups = group_and_visualize_reviews_by_location(reviews)


if __name__ == "__main__":
    main()
