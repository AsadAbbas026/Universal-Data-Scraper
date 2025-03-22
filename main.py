from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
from nltk import pos_tag, word_tokenize
import requests
import re
import pandas as pd
import nltk

nltk.download('punkt')

def extract_href_value(a_tags):
    href_values = []
    for a_tag in a_tags:
        href_value = a_tag.get_attribute('href')
        href_values.append(href_value)
    return href_values

def scrape_website_single(url):
    try:
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'}
        response = requests.get(url, headers=headers)

        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            paragraphs = soup.find_all('p')
            cleaned_paragraphs = [re.sub(r'\[\d+\]', '', paragraph.text) for paragraph in paragraphs]

            for cleaned_paragraph in cleaned_paragraphs:
                print(cleaned_paragraph)

            return cleaned_paragraphs
        else:
            print(f"{url} Error: Unable to retrieve data. Status Code: {response.status_code}")
            return []
    except Exception as e:
        print(f"Error occurred: {e}")
        return []

def extract_relevant_words(paragraph):
    tokens = word_tokenize(paragraph)
    tagged_tokens = pos_tag(tokens)
    relevant_words = [word for word, pos in tagged_tokens if pos in ['NN', 'NNS', 'JJ', 'JJR', 'JJS']]
    return relevant_words

# Selenium code for scraping URLs
url = "https://www.google.com"
browser = webdriver.Chrome()
browser.maximize_window()
browser.get(url)
searchQuery = "What is Artificial Intelligence"
searchBar = browser.find_element(By.NAME, 'q')
searchBar.send_keys(searchQuery)
searchBar.submit()

wait = WebDriverWait(browser, 10)
wait.until(EC.presence_of_element_located((By.ID, 'search')))

all_a_tags = browser.find_elements(By.CSS_SELECTOR, 'a[jsname="UWckNb"]')
href_values = extract_href_value(all_a_tags)
href_values.remove(href_values[0])
for href_value in href_values:
    print(href_value)

browser.quit()

# Scraping and processing paragraphs
paragraphs_list = []
for href_value in href_values:
    paragraphs = scrape_website_single(href_value)
    paragraphs_list.extend(paragraphs)  # Use extend to append each paragraph individually

# Create DataFrame and save to Excel
df = pd.DataFrame({'Paragraphs': paragraphs_list})
df.to_excel('output.xlsx', index=False)
df = pd.read_excel('output.xlsx')
df = df.dropna()
relevant_words_df = df['Paragraphs'].apply(extract_relevant_words)
relevant_words_sample = [word for words in relevant_words_df for word in words]
pattern = '|'.join(re.escape(word) for word in relevant_words_sample)
relevant_df = df[df['Paragraphs'].str.lower().str.contains(pattern, regex=True)]
relevant_df.to_excel('output_relevant.xlsx', index=False)

print("Relevant words:", relevant_words_sample)
