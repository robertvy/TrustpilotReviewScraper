# Trustpilot Review Scraper

Welcome to the **Trustpilot Review Scraper**, a Python-based tool designed for scraping and analyzing detailed reviews
from Trustpilot.com using the `trustpilot.py` script.

With TrustpilotReviewScraper and the `trustpilot.py` script, you can easily extract and analyze reviews for a specific
domain on Trustpilot, filtering by star ratings, date ranges, languages, and more. This tool supports additional
capabilities such as sorting, visualization, and exporting data for comprehensive analysis.

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
- Tested with Python 3.12.1. Earlier versions may not be compatible.
- Required Dependencies:
    - Python libraries listed in `requirements.txt`:
        - pandas
        - requests
        - matplotlib
        - lxml
### Installation
1. **Clone the Repository**
Start by cloning the repository to your local machine:
```sh
git clone https://github.com/robertvy/TrustpilotReviewScraper.git
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

### Running the `trustpilot.py` Script
To scrape reviews for a specific domain on Trustpilot, use the following command, replacing `[domain]` with the actual domain you wish to scrape:
```sh
python trustpilot.py [domain]
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

### Example Usage Commands and Outputs

Below are examples of how to use the script along with a description of expected outputs:

- Fetch reviews for domain `example.com` with only 5-star ratings, sorted by rating in descending order, and output to
  JSON:

```sh
python trustpilot.py example.com --stars 5 --sort-by rating --sort-order desc --output json
```

Expected output:

- A JSON file `reviews_example.json` will be created with content structured as follows:

```json
[
   {
      "title": "Great service!",
      "content": "The service was amazing. Highly recommended.",
      "rating": 5,
      "date": "2023-10-01",
      "verified": true,
      "language": "en"
   },
   ...
]
```

- Fetch reviews for domain `example.com` over the last 30 days with replies, save as both CSV and JSON:

```sh
python trustpilot.py example.com --date last30days --replies --output both
```

Expected outputs:

- CSV file `reviews_example.csv` and JSON file `reviews_example.json` containing the requested review data.

## Archived Outputs

When the script processes reviews, output files are stored locally in the working directory based on the selected
format.

- **CSV File Structure**:
  Example CSV structure for scraped reviews:

| Title          | Content                    | Rating | Date       | Verified | Language |
|----------------|----------------------------|--------|------------|----------|----------|
| Great service! | The service was amazing... | 5      | 2023-10-01 | True     | en       |
| Average        | It was okay, not great...  | 3      | 2023-09-25 | True     | en       |

- **Keyword Analysis File**:
  A text analysis report can include the frequency of keywords across reviews, saved in a `.txt` or `.json` file:

```
Keyword Analysis:
- "amazing": 15 occurrences
- "service": 27 occurrences
- "highly recommended": 10 occurrences
```

- **Visual Outputs**:
  The script can generate bar charts for review ratings:

Example chart:

- Bar chart showing distribution of ratings from 1 to 5.

## Known Issues
Currently, the script does not fetch multiple reviews submitted by the same reviewer.

## Contributing
Contributions are welcome! Feel free to fork the repository, make changes, and submit pull requests. If you have any suggestions or issues, please open an issue in the GitHub repository.

## License
This project is licensed under the MIT License - see the LICENSE file for details.

## Disclaimer

### Important Notes on Ethical Scraping

- Always check and adhere to Trustpilot's `robots.txt` file.
- Use this tool responsibly to avoid violating terms of service or impacting website performance.
- This tool is for educational and research purposes only. Please use responsibly and ethically.
