from playwright.sync_api import sync_playwright
from dataclasses import dataclass,asdict,field
import pandas as pd
import argparse

@dataclass
class Business: # contains business info 
    name: str=None
    address: str=None
    phone_number: str=None
    website: str=None
    reviews_count: int=None
    rating: float=None


@dataclass
class BusinessList:
    business_list: list[Business] = field(default_factory=list) # so it can be appended not immutable

    def dataframe(self):
        return pd.json_normalize((asdict(business) for business in self.business_list),sep="_")
    
    def save_to_excel(self,filename):
        self.dataframe().to_excel(f"{filename}.xlsx",index=False)   

    def save_to_csv(self,filename):
        self.dataframe().to_csv(f"{filename}.csv",index=False) 

def main():
    total=10
    with sync_playwright() as p:
        browser=p.chromium.launch(headless=False) 
        page=browser.new_page()
        page.goto("https://www.google.com/maps/?hl=en",timeout=60000)   
        page.wait_for_timeout(5000) 
        #page.wait_for_load_state("networkidle",timeout=100000)

        page.locator('input#searchboxinput').fill(search_for)
        page.wait_for_timeout(3000)

        page.keyboard.press("Enter")
        page.wait_for_timeout(10000)

        #scrolling 
        page.locator('(//div/a[contains(@href,"place")])[1]').hover()

        while True:
            page.mouse.wheel(0,10000)
            page.wait_for_timeout(2000)

            if page.locator('//div/a[contains(@href,"place")]').count()>= total:
             listings=page.locator('//div/a[contains(@href,"place")]').all()[:total]
             print(f"total scraped : {len(listings)}")
             break

            else:
                print(f"currently scraped : {len(listings)}")

        business_list=BusinessList()

        for listing in listings[:total]:
            listing.click()
            
            name_xpath='//div[@role="main"][@aria-label]'
            address_xpath='//button[@data-item-id="address"]/div/div[2]'
            phone_xpath='//button[contains(@data-item-id,"phone")]/div/div[2]'
            website_xpath='//a[contains(@aria-label,"Website")]/div/div[2]'
            reviews_count_xpath='//span[contains(@aria-label,"reviews")]'
            rating_xpath='//div[@role="main"][@aria-label]//following-sibling::span[contains(@aria-label,"star")]'

            page.locator('//div/button[@role="tab"][contains(@aria-label,"Reviews")]').hover()
            page.wait_for_timeout(2000)
            page.mouse.wheel(0,100)
            page.wait_for_timeout(2000)

            business=Business() # we called the first dataclass
            name_element=page.locator(name_xpath)
            if name_element.count()>0 :
                   business.name=name_element.get_attribute('aria-label') 
            else:
                business.name = 'N/A'   
                    
            address_element=page.locator(address_xpath)
            if address_element.count()>0 :
                business.address=address_element.inner_text()
            else:
                business.address = 'N/A'

            phone_element=page.locator(phone_xpath)
            if phone_element.count()>0 :
                business.phone_number=phone_element.inner_text()
            else:
                business.phone_number = 'N/A'

            website_element = page.locator(website_xpath)
            if website_element.count() > 0:  # Check if the website element exists
                business.website = website_element.inner_text()
            else:
                business.website = 'N/A'

            reviews_element = page.locator(reviews_count_xpath)
            if reviews_element.count() > 0:  # Check if the website element exists
                business.reviews_count = int(reviews_element.get_attribute('aria-label').split(' ')[0])
            else:
                business.reviews_count = 0

            rating_element = page.locator(rating_xpath)
            if rating_element.count() > 0:  # Check if the website element exists
                business.rating = float(rating_element.get_attribute('aria-label').split(' ')[0])
            else:
                business.rating = 0                
            

            business_list.business_list.append(business)

            business_list.save_to_csv('google_maps_demo')
            business_list.save_to_excel('google_maps_demo')



        browser.close()



if __name__ == "__main__":
    #here we will enter arguments in command line 
    parser=argparse.ArgumentParser()
    parser.add_argument("-s", "--search",type=str)         
    parser.add_argument("-l", "--location",type=str)  
    args=parser.parse_args()  
 
    if args.search and args.location:
          search_for= f"{args.search}  {args.location}"

    else:
        search_for="butcher shop london"

    main()        