# TrustpilotReviewScraper

`TrustpilotReviewScraper` is a Python script designed to scrape reviews from Trustpilot.com. It extracts detailed review information including the reviewer's name, review count, country, rating, review date, review title, review content, and date of experience. The tool supports scraping across multiple pages and can fetch reviews in all available languages, outputting the data into a CSV file for further analysis.

## Requirements

- Python 3.12.1 (May work with earlier versions of Python 3, but not tested)

## Setup

To use `TrustpilotReviewScraper`, follow these setup instructions:

1. **Clone the Repository**

    ```
    git clone https://github.com/YOUR_USERNAME/TrustpilotReviewScraper.git
    cd TrustpilotReviewScraper
    ```

2. **Create and Activate a Virtual Environment**

    - For Unix/macOS:

        ```
        python3 -m venv env
        source env/bin/activate
        ```

    - For Windows:

        ```
        python -m venv env
        .\env\Scripts\activate
        ```

3. **Install Required Packages**

    ```
    pip install -r requirements.txt
    ```

## Usage

To start scraping reviews from a specific domain on Trustpilot, run the script as follows:

```python 
trustpilot_scraper.py [domain]
```
Replace `[domain]` with the Trustpilot domain you wish to scrape. For example:
python trustpilot_scraper.py example.com


The script will scrape reviews and save them into a CSV file named `reviews_[domain].csv`.

## Contributing

Contributions are welcome! Please feel free to submit a pull request or open an issue if you have suggestions or improvements.

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Disclaimer

This software is provided for educational purposes only. By using this software, you agree that it is solely for personal and educational use. The developer(s) of this project do not endorse or promote the use of this software for any purposes that may violate specific terms of service, legal agreements, or laws.
It is the responsibility of the user to ensure that their use of this software complies with all relevant terms of service and laws. The user should also be aware of and respect the ethical considerations involved in web scraping, such as respecting the robots.txt file of websites, avoiding excessive requests that can impact service performance, and not accessing or collecting data without permission.
The developer(s) assume no liability for any misuse of this software or any violations of terms or laws resulting from its use. Users are encouraged to consult a legal professional if they have questions about the legal implications of their intended use of this software.




