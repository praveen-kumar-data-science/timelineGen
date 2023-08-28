# Project Name

[![License](https://img.shields.io/badge/License-GPL-blue.svg)](LICENSE)

## Description

The goal of this project is to generate a time of events from any textual content, ordered by the most recent to the oldest events. The information can be collected from any online media from where the data is scrappable. The user can search based on any real-world entity name such as name/place/object and by default, we use Wikipedia data about the entity to collect, store and analyze the events based on the advanced chatGPT API in Python. The user may also provide their own link from where they would like to seek information and generate timelines (but the link should be scrappable). We use the BeautifulSoup library to extract the contents from the link (or Wikipedia page) and then pass them to the ChatGPT API with suitable prompt engineering to generate a timeline of events. Then, we use basic Python nltk packages to clean the results obtained from the chatGPT API, apply feature engineering techniques and present the final table of information on the events. The user can also filter and select the events that they feel are necessary to include in the timeline and also have an opportunity the download the Excel/CSV file containing the events. The timeline visualization is presented in the form of a .html page. 

## Table of Contents


## Installation

Provide instructions on how to install and set up the project. Include any dependencies that need to be installed and any environment setup necessary.

## Usage

Explain how to use the project or provide examples of its usage. Include code snippets or screenshots if applicable. You can also link to a separate documentation file if available.

## Contributing

Specify how others can contribute to the project. Include guidelines for submitting bug reports, feature requests, or pull requests. If you have a code of conduct, mention it here.

## License

This project is licensed under the [GNU General Public License v3.0](LICENSE).

## Contact

- [Lloyd Fernandes](https://github.com/lloydf96)
- [Praveen Kumar Murugaiah](https://github.com/praveen-kumar-data-science)
- [Raunak Sengupta]

Feel free to reach out if you have any questions, feedback, or suggestions!
