from googleapiclient.discovery import build
from pprint import pprint
from dotenv import load_dotenv
import os
import requests
from bs4 import BeautifulSoup
from langchain_experimental.utilities import PythonREPL
import warnings
import wikipedia
from .config import *
from openai import OpenAI
wikipedia.set_lang('en')

load_dotenv()
client = OpenAI()

def get_webpage_info(url, search_term):
    """Gets a summary of the text on the webpage, along with any useful links relevant search_term, call this tool with following input format: get_webpage_info: <url>, <search_term>"""
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')
    # url_page_content = soup.get_text(separator=' ', strip=True)
    paragraphs = soup.find_all('p')
    url_page_content = " ".join(paragraph.get_text(strip=True) for paragraph in paragraphs)
    links = [
        link['href'] for link in soup.find_all('a', href=True)
        if link['href'].startswith('https://')
    ]

    completion = client.chat.completions.create(
        model="gpt-4o-mini", 
        messages=[
            {"role": "system", "content": config.WEB_PAGE_INFORMATION_RETRIEVAL_SYSTEM_MESSAGE.format(search_term=search_term, links=links)}, 
            {"role": "user", "content": url_page_content}
            ]
        )
    relevant_content = completion.choices[0].message.content
    return relevant_content

def google_search(search_term, num_results=3):
    """Google Search. Returns the title, url, page content and links for the top result from Google search. Good for general internet search."""
    search_term = search_term.strip('"')
    service = build("customsearch", "v1", developerKey=os.environ['GOOGLE_API_KEY'])
    results = service.cse().list(q=search_term, cx=os.environ['GOOGLE_CSE_ID'], num=num_results).execute()
    formatted_results = []
    for result in results['items']:
        title, url = result['title'], result['formattedUrl']
        relevant_content = get_webpage_info(url, search_term)
        formatted_results.append({"Title": {title}, "URL": {url}, "Relevant page content and links (if useful)": relevant_content})
    return formatted_results

def wikipedia_search(query, sentences=10, full_page=False):
    """Wikipedia Search. Searches wikipedia and returns a summary. Use this to get summaries of popular topics. Great at getting specific topic wise information, and if used, input query to this tool should be as specific as possible."""
    if full_page:
        return wikipedia.page(query).content
    return wikipedia.summary(query, sentences=sentences)

repl = PythonREPL()
def python_repl(query):
    """Runs the provided python code in a python REPL"""
    with warnings.catch_warnings():
        warnings.simplefilter('ignore')
        return repl.run(query)

def calculate(query):
    """Computes basic arithmetic calculations using python's eval() function"""
    return eval(query)

def knowledge_base_lookup(vector_store, query, top_k=10):
    """Returns most similar chunks of documents from user given knowledge base"""
    return vector_store.similarity_search(query, k=top_k)

# pprint(google_search('FIFA World Cup Final 2022 runner-up'))