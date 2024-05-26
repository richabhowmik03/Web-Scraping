

import requests #importing request library to get data from website
from bs4 import BeautifulSoup #importing beautifulsoup library for parsing
from urllib.parse import urljoin #to join url
import os #to create directories

def get_soup(url): #function to get soup
    response = requests.get(url) #requesting the url
    return BeautifulSoup(response.content, 'html.parser') #returning soup

def extract_mp_data(mp, gender): #function to extract data
    name = mp.find('div', class_='ce-mip-mp-name').text.strip() #extracting name from the div class
    party = mp.find('div', class_='ce-mip-mp-party').text.strip() #extracting party from the div class
    constituency = mp.find('div', class_='ce-mip-mp-constituency').text.strip() #extracting constituency from the div class
    province = mp.find('div', class_='ce-mip-mp-province').text.strip() #extracting province from the div class
    image_url = mp.find('img')['src'] #extracting image from the img tag
    final_url = 'https://www.ourcommons.ca/' + image_url #adding https://www.ourcommons.ca/ to the image url so that it can be accessed
    mp_url = mp.find_parent('a', class_='ce-mip-mp-tile')['href'] #extracting url from the a tag which can be accessed only using parent
    
    return {
        'Name': name,
        'Gender': gender,
        'Party': party,
        'Constituency': constituency,
        'Province': province,
        'Image URL': final_url,
        'MP URL': mp_url
    } #returning data in a dictionary form to store it in a list 

def fetch_mps_data(base_url, params, gender): #function to fetch data based on params (male and female pms)
    url = base_url + params #adding params to the base url
    soup = get_soup(url) #calling get_soup function
    mps = soup.find_all('div', class_='ce-mip-flex-tile') #extracting data from the div class
    mps_data = [extract_mp_data(mp, gender) for mp in mps] #calling extract_mp_data function
    return mps_data #returning mps_data

def generate_html_table(mps_data_store, base_url): #function to generate html table
    table_html = "<table>\n" #Opening the HTML table tag
    table_html += "<thead>\n<tr>\n" #Opening the HTML table row tag
    table_html += "<th>Name</th>\n" #making the name header
    table_html += "<th>Gender</th>\n" #making the gender header
    table_html += "<th>Party</th>\n" #making the party header 
    table_html += "<th>Constituency</th>\n" #making the constituency header 
    table_html += "<th>Province</th>\n" #making the province header 
    table_html += "<th>Image</th>\n" #making the image header 
    table_html += "<th>MP URL</th>\n" #making the mpurl header 
    table_html += "</tr>\n</thead>\n" #Closing the HTML table row tag

    table_html += "<tbody>\n" #Opening the HTML table body tag
    for mp in mps_data_store: #Looping through the list of dictionaries
        table_html += "<tr>\n" #Opening the HTML table row tag
        table_html += f"\t<td>{mp['Name']}</td>\n" #Opening the HTML table data tag
        table_html += f"\t<td>{mp['Gender']}</td>\n" #Opening the HTML table data tag
        table_html += f"\t<td>{mp['Party']}</td>\n" #Opening the HTML table data tag
        table_html += f"\t<td>{mp['Constituency']}</td>\n" #Opening the HTML table data tag
        table_html += f"\t<td>{mp['Province']}</td>\n" #Opening the HTML table data tag
        table_html += f"\t<td><img src='{mp['Image URL']}' alt='{mp['Name']}'></td>\n" #Opening the HTML table data tag
        
        mp_url = urljoin(base_url, mp['MP URL']) #Joining the base url with the mp url
        table_html += f"\t<td><a href='{mp_url}'>Link</a></td>\n" #Opening the HTML table data tag
        
        table_html += "</tr>\n" #Closing the HTML table row tag
    table_html += "</tbody>\n" #Closing the HTML table body tag

    table_html += "</table>" #Closing the HTML table tag
    
    return table_html #returning table_html

def save_html(html_content, file_path): #function to save html file
    with open(file_path, 'w', encoding='utf-8') as f: #opening the file in write mode
        f.write(html_content) #writing the html content

def download_images(mps_data_store, output_dir): #function to download images
    if not os.path.exists(output_dir): #checking if the output directory exists
        os.makedirs(output_dir) #creating the output directory

    for mp in mps_data_store: #Looping through the list of dictionaries
        image_url = mp['Image URL'] #Extracting the image url
        response = requests.get(image_url) #requesting the image
        img_name = str(image_url).split("/")[-1] #Extracting the image name from the last part of the image url
        image_path = os.path.join(output_dir, img_name) #Joining the output directory with the image name
        with open(image_path, "wb") as f: #opening the image in write mode
            f.write(response.content) #writing the image

if __name__ == "__main__": #main function
    base_url = "https://www.ourcommons.ca/Members/en/" #main url which contains all the mps list
    female_params = "search?caucusId=all&province=all&gender=F" #url which contains only female mps 
    male_params = "search?caucusId=all&province=all&gender=M" #url which contains only male mps

    male_mps_data = fetch_mps_data(base_url, male_params, 'Male') #calling fetch_mps_data function to take the male data
    female_mps_data = fetch_mps_data(base_url, female_params, 'Female') #calling fetch_mps_data function to take the female data

    all_mps_data = male_mps_data + female_mps_data #merging male and female data

    html_table = generate_html_table(all_mps_data, base_url) #calling generate_html_table function
    save_html(html_table, 'main.html') #calling save_html function

    download_images(all_mps_data, 'output') #calling download_images function to save it in the output directory
