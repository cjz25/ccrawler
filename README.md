# ccrawler

Crawl public Facebook group posts and store author, publish time and post content in a text file.

## Table of contents
1. [Requirements](#requirements)
2. [Installation](#installation)
3. [Usage](#usage)
4. [License](#license)

## Requirements

  * macOS
  * Python 3
  * Google Chrome
  * Selenium 3.141.0
  * PyYAML==5.4.1
  * urllib3==1.26.2
  * webdriver-update-tool==0.1.3

## Installation

Install from the source:

```sh
$ git clone https://github.com/cjz25/ccrawler.git
```

## Usage

### Set up config.yml

### Add more Facebook group links

You can add any public Facebook group link you like to the `facebook_group_link` file.  
Note: Please follow the pattern: One link per line, followed by the number of post to crawl.

### Demo: Crawl recent posts

```sh
$ python3 -m ccrawler.fb_group_post_crawler
```

Check your results in the `facebook_group` folder.

## License
MIT License
