#!/usr/bin/env python
# coding: utf-8

# In[ ]:


# bibliotēka HTTP pieprasījumiem
import requests

# bibliotēka datu izgūšanai
from bs4 import BeautifulSoup

# bibliotēka datu apstrādei
import pandas as pd

# bibliotēka darbam ar laiku
from datetime import datetime

# bibliotēka darbam ar failiem
import os


# In[ ]:


urls = {
    "cost_of_living": "https://www.numbeo.com/cost-of-living/country_result.jsp?country=Latvia",
    "fuel_prices": "https://lv.fuelo.net/?lang=en",
    "electricity_prices": "https://www.energyprices.eu/electricity/latvia",
    "cpi": "https://tradingeconomics.com/latvia/consumer-price-index-cpi"
}


# In[ ]:


output_files = {
    "cost_of_living": "output_cost_of_living.csv",
    "fuel_prices": "output_fuel_prices.csv",
    "electricity_prices": "output_electricity_prices.csv",
    "cpi": "output_cpi.csv",
}


# In[ ]:


headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'
}


# In[ ]:


# ja sākotnējs HTTP pieprasījums nav veiksmīgs, tad tiek pievienota galvene, lai imitētu pārlūkprogrammas pieprasījumu 
def download_webpage(url):
    try:
        response = requests.get(url)
        if response.status_code == 200:
            return response.text
        else:
            response = requests.get(url, headers=headers)
            response.raise_for_status()
            return response.content


# In[ ]:


def scrape_cost_of_living(soup):
    # nepiciešami dati atrodas 1.tabulā
    table = soup.find('table', attrs={'class': 'data_wide_table'})
    rows = table.find_all('tr')
    
    data = {}

    # tiek palaista galvene un tiek atrasti visas 'td' iezīmes
    for i, row in enumerate(rows[1:], start=1):
        columns = row.find_all('td')
        
        if len(columns) >= 2:
            category = columns[0].get_text(strip=True)
            price_span = columns[1].find('span')
            price = price_span.get_text(strip=True) if price_span else 'N/A'
            
            print(f"category: {category}, price: {price}")  # izgūti dati
            data[category] = price
    
    return data


# In[ ]:


def scrape_fuel(soup):
    # nepiciešami dati atrodas pirmos trijos šīs klases 'div' iezīmēs 
    fuel_entries = soup.select('div.box.col-sm-6.col-md-4')[:3]
    
    data = {}
    
    for entry in fuel_entries:
        category_tag = entry.select_one('h2.text-center')
        price_tag = entry.select_one('h3.text-center > span')
            
        if price_tag:
            price = price_tag.get_text(strip=True).replace('€', '').strip()
        else:
            continue
            
        print(f"category: {category}, price: {price}")  # izgūti dati
        data[category] = price

    return data


# In[ ]:


def scrape_electricity(soup):
    tables = soup.find_all('table')
    
    if len(tables) >= 2:
        # nepiciešami dati atrodas 2.tabulā
        second_table = tables[1]
        last_tr = second_table.find_all('tr')[-1]
        last_td = last_tr.find_all('td')[-1]
        price = last_td.text.strip()
        
        print(f"category: kV/st., price: {price}")  # izgūti dati
        return {"kV/st.": price}


# In[ ]:


def scrape_cpi(soup):
    # nepiciešami dati atrodas 'div' iezīmē ar šō ID
    target_div = soup.find('div', id='ctl00_ContentPlaceHolder1_ctl00_ctl00_PanelPeers')
    target_table = target_div.find('table')
    tbody = target_table.find('tbody')
    rows = tbody.find_all('tr')

    data = {}

    for i, row in enumerate(rows[1:], start=1):
        columns = row.find_all('td')
        if len(columns) >= 2:
            category = columns[0].get_text(strip=True)
            price_span = columns[1].find('span')
            price = price_span.get_text(strip=True) if price_span else 'N/A'
            
            print(f"category: {category}, price: {price}")  # izgūti dati
            data[category] = price
    
    return data


# In[ ]:


def parse_html(html, data_type):
    soup = BeautifulSoup(html, 'html.parser')
    data = []
    if data_type == "cost_of_living":
        data = scrape_cost_of_living(soup)
        
    elif data_type == "fuel_prices":
        data = scrape_fuel(soup)
        
    elif data_type == "electricity_prices":
        data = scrape_electricity(soup)
        
    elif data_type == "cpi":
        data = scrape_cpi(soup)
        
    return data


# In[ ]:


# saglabāšana csv failā - ja fails neeksistē, tad tas tiek izveidots ar datu galvenēm
def append_to_csv(data, file_name):
    today_date = datetime.now().strftime('%Y-%m-%d')
    data["Date"] = today_date
    new_data = pd.DataFrame(data)
    
    columns_order = ["Date"] + [col for col in new_data.columns if col != "Date"]
    new_data = new_data[columns_order]
    
    if os.path.exists(file_name):
        existing_data = pd.read_csv(file_name)
        combined_data = pd.concat([existing_data, new_data], ignore_index=True)
        combined_data.to_csv(file_name, index=False)
    else:
        headers = ['Date'] + list(data.keys())
        new_data.to_csv(file_name, index=False, header=headers)


# In[ ]:


def main():
    for data_type, url in urls.items():
        html = download_webpage(url)
        data = parse_html(html, data_type)
        append_to_csv(data, output_files[data_type])


# In[ ]:


if __name__ == "__main__":
    main()

