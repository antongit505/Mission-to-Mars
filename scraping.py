#Import dependencies
from splinter import Browser
from bs4 import BeautifulSoup as soup
from webdriver_manager.chrome import ChromeDriverManager
import pandas as pd
import datetime as dt

def scrape_all():
    #Set the executable path
    executable_path={'executable_path':ChromeDriverManager().install()}
    browser=Browser('chrome',**executable_path,headless=True)

    news_title,news_paragraph=mars_news(browser)

    # Run all scraping functions and store results in a dictionary
    data = {
        "news_title": news_title,
        "news_paragraph": news_paragraph,
        "featured_image": featured_image(browser),
        "facts": mars_facts(),
        "hemispheres":hemisphere_data(browser),
        "last_modified": dt.datetime.now()
            }

    # End the automated browsing session
    browser.quit()

    return data

def mars_news(browser):

    #Set the URL
    url='https://data-class-mars.s3.amazonaws.com/Mars/index.html'
    browser.visit(url)

    #Optional delay for loading the page
    browser.is_element_present_by_css('div.list_text',wait_time=1) 

    #Set the HTML Parser
    html=browser.html
    news_soup=soup(html,'html.parser')

    try:
        #create parent element
        slide_elem = news_soup.select_one('div.list_text') 

        # Begin with scraping
        #To only retrieve the title we use the parent element to find the first 'div' tag and save it as a 'news_title'
        news_title = slide_elem.find('div',class_='content_title').get_text() 

        #To scrape the content of the news
        news_p = slide_elem.find('div',class_='article_teaser_body').get_text()

    except AttributeError:
        return None,None

    return news_title,news_p


# ### Featured Images

def featured_image(browser):

    #Visit URL
    url='https://data-class-jpl-space.s3.amazonaws.com/JPL_Space/index.html'
    browser.visit(url)

    #Find and click the full image button
    full_image_elem=browser.find_by_tag('button')[1] 
    full_image_elem.click()

    #Parse the resulting html with soup
    html=browser.html
    img_soup=soup(html,'html.parser')

    try:
        #Find the relative image url
        img_url_rel= img_soup.find('img',class_='fancybox-image').get('src')

    except AttributeError:
        return None
    
    #Use the base url to create the absolute url
    img_url=f'https://data-class-jpl-space.s3.amazonaws.com/JPL_Space/{img_url_rel}'
            
    return img_url

# ### Scrape the table information
def mars_facts():
    try:
        #Use read_html to scrape the facts table into a df
        df=pd.read_html('https://data-class-mars-facts.s3.amazonaws.com/Mars_Facts/index.html')[0]

    except BaseException: 
        return None

    # Assign columns and set index of dataframe
    df.columns=['Description','Mars','Earth']
    df.set_index('Description',inplace=True)
    # Convert dataframe into HTML format, add bootstrap
    return (df.to_html(classes="table table-bordered")) 

def hemisphere_data(browser):
    hemisphere_image_urls=[]

    #Visit the url
    url = 'https://astrogeology.usgs.gov/search/results?q=hemisphere+enhanced&k1=target&v1=Mars'
    browser.visit(url)

    #Iterate through the 4 links in the page
    for link in range(4):
        # Click through each article
        browser.links.find_by_partial_text('Hemisphere')[link].click()
        
        # Parse every link into html
        html=browser.html
        html_soup=soup(html,'html.parser')
        
        # Navigate through the tags where the links for the img are
        img=html_soup.find('li') #since the image we want is in the first <li> we use find
        img_sub=img.find('a')
        img_url=img_sub.get('href')
    
        #Get the titles for the images
        tit=html_soup.find('h2')
        title=tit.text
        
        hemispheres={'img_url':img_url,'title':title}
        hemisphere_image_urls.append(hemispheres)
    
        #Browse back
        browser.back()
    return hemisphere_image_urls

if __name__ == "__main__":
    # If running as script, print scraped data
    print(scrape_all())