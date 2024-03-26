# TrustpilotReviewScraper

Welcome to **TrustpilotReviewScraper**, a Python-based tool designed for scraping detailed reviews from Trustpilot.com.

With TrustpilotReviewScraper, you can easily extract reviews for a specific domain on Trustpilot, filtering by star ratings, date ranges, languages, and more. With an easy-to-use command-line interface, you can quickly collect and analyze Trustpilot reviews for various purposes, such as sentiment analysis, customer feedback, and market research.

- 🔍 **Comprehensive Data Collection**: Extract all available data for Trustpilot reviews, including ratings, titles, content, dates, and more.
- 🌍 **Multi-Language Support**: Fetch reviews in all available languages, allowing for global data analysis.
- 📄 **Multi-Page Scraping**: Navigates and collects data from multiple pages automatically.
- 💾 **Flexible Output Options**: Offers CSV, JSON, or both formats for output, catering to various data processing needs.
- 🚿 **Customizable Filtering**: Filter reviews by star ratings, date ranges, search keywords, languages, and more.
- 🔀 **Sorting Capabilities**: Sort reviews by various fields, such as rating, date, relevance, etc.
- 💻 **Easy-to-Use Command-Line Interface**: Simple and intuitive command-line interface for easy data collection.

## Getting Started

### Prerequisites
- Tested with Python 3.12.1. Earlier versions may not be compatible.

### Installation
1. **Clone the Repository**
Start by cloning the repository to your local machine:
```sh
git clone https://github.com/YOUR_USERNAME/TrustpilotReviewScraper.git
cd TrustpilotReviewScraper
```
2. **Set Up a Virtual Environment**
Creating a virtual environment is recommended to avoid any conflicts with other Python projects:
- Unix/macOS:
```sh
python3 -m venv env
source env/bin/activate
```
- Windows:
```cmd
python -m venv env
.\env\Scripts\activate
```
3. **Install Required Packages**
Install all the necessary packages using pip:
```sh
pip install -r requirements.txt
```
## Usage
To scrape reviews for a specific domain on Trustpilot, use the following command, replacing `[domain]` with the actual domain you wish to scrape:
```sh
python trustpilot_scraper.py [domain]
```
### Required Argument
- `domain`: The domain to scrape reviews for, without the need for a flag. It is the first positional argument.

### Optional Arguments
- `--stars [N ...]`: Filter reviews by star ratings. Accepts multiple values. For instance, `--stars 4 5` will only fetch reviews rated with 4 or 5 stars.

- `--date`: Filter reviews by date. Options include 'last30days', 'last3months', 'last6months' and 'last12months'. Example usage: `--date last30days`.

- `--search`: Filter reviews by a search keyword. Example usage: `--search "excellent service"`.

- `--languages`: Specify the language of reviews to fetch (e.g., 'en' for English, 'es' for Spanish). The default is 'all', which collects reviews in all languages. Example usage: `--languages en`.

- `--verified`: If used, the script will only fetch reviews that are verified. No additional value needs to be specified. Example usage: `--verified`.

- `--replies`: If used, the script will only fetch reviews that have replies. No additional value needs to be specified. Example usage: `--replies`.

- `--sort-by`: Specify the field to sort reviews by. Options include 'rating', 'date', etc. The default is 'published_date'. Example usage: `--sort-by rating`.

- `--sort-order`: Specify the order to sort reviews in. Options are 'asc' for ascending and 'desc' for descending. The default is 'asc'. Example usage: `--sort-order desc`.

- `--output`: Choose the output format of the scraped data. Options are 'csv', 'json', or 'both'. The default is 'csv'. Example usage: `--output both`.

## Contributing
Contributions are welcome! Feel free to fork the repository, make changes, and submit pull requests. If you have any suggestions or issues, please open an issue in the GitHub repository.

## License
This project is licensed under the MIT License - see the LICENSE file for details.

## Disclaimer
This tool is for educational and research purposes only. Please use responsibly and ethically.
