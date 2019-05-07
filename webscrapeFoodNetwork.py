# Alex Jirovsky
# May 7 2019
#
# FoodNetwork.com recipe webscraper
#
# This program navigates through recipes on FoodNetwork.com
# starting at a recipe URL that acts as the root URL for the 
# program. It navigates by collecting the URLs of recommended
# recipes and scraping those sites in addition to their 
# respective recommended recipes. When the program scrapes a 
# webpage, it is collecting and printing out all important 
# information that is displayed on the page through parsing
# the sites HTML with 'lxml' and the BeautifulSoup library.

from bs4 import BeautifulSoup
import requests

visited_webpages = []
good_webpage = []

url = 'https://www.foodnetwork.com/recipes/shrimp-watercress-and-farro-salad-2110063'

# scrapes the important information from the website
def scrape(url):

    page_request  = requests.get(url, timeout=5)

    soup = BeautifulSoup(page_request.content, 'lxml')

    # gets the line referring to the Author
    # "Recipe courtesy of firstName lastName" 
    author_info = soup.find('span',class_='o-Attribution__a-Name').getText()

    # separates the string into individual words
    author_info_list = author_info.split()
    list_length = len(author_info_list)

    # put the last two elements of author_info_list, which
    # will be the first and last name, into author_name
    author_name = author_info_list[list_length-2]+" "+author_info_list[list_length-1]

    #gets the full recipe name
    recipe_name = soup.find('span',class_='o-AssetTitle__a-HeadlineText').getText()

    # gets full RecipeInfo block
    recipe_info = soup.find('div',class_='o-RecipeInfo')

    # put all list items into recipe_info_list
    recipe_info_list = recipe_info.findAll('li')

    recipe_info_list_text = []

    # goes through recipe_info_list, converts each list
    # into a string, then appends it to recipe_info_list_text
    for info in recipe_info_list:

        # accounts for the Nutrition Info Special Case
        if info.find('section',class_='o-NutritionInfo'):
            recipe_inner_block = info.find('section',class_='o-NutritionInfo')
           
            dt_list = []
            dd_list = []

            # get the text from each <dt> tag
            for thing in recipe_inner_block.findAll('dt'):
                dt_list.append(thing.text)

            # get the text from each <dd> tag
            for thing in recipe_inner_block.findAll('dd'):
                dd_list.append(thing.text)
            
            # add the elements from dd_list and dt_list to 
            # the main list of recipe info in this particular
            # order
            for i in range(0,len(dt_list)):
                recipe_info_list_text.append(dt_list[i]+': '+dd_list[i])
                
            print('\n')

        else:
            # removes whitespace and new lines
            recipe_info_list_text.append(' '.join(info.text.split()))

    # delete duplicates to counteract repetative HTML
    recipe_info_list_text = [i for n, i in enumerate(recipe_info_list_text) if i not in recipe_info_list_text[:n]]

    # gets Ingredients list
    ingredients_block = soup.find('div',class_='o-Ingredients__m-Body')
    ingredient_list_code = ingredients_block.select('p')
    ingredient_list_text = []
    for ingredient in ingredient_list_code:
        ingredient_list_text.append(ingredient.getText())

    # gets cooking instructions
    cooking_instruction_block = soup.find('div',class_='o-Method__m-Body')
    cooking_instruction_list_code = cooking_instruction_block.select('li')
    cooking_instruction_list_text = []
    for instruction in cooking_instruction_list_code:
        cooking_instruction_list_text.append(instruction.getText())

    # get recommended recipes

    #grab the main block with all possible recommended recipes
    recommendations_block = soup.find('div',class_='o-Recommendations__TileContainer o-Recommendations__TileContainer--general l-Columns l-Columns--4up')

    # put all 'a' tags with corresponding links into a list 
    recommendations_url_list_code = recommendations_block.findAll('a',href=True)

    #star_rating = soup.find('span')
    
    # grab only the links from the previous list
    recommendations_url_list = []

    for webpage in recommendations_url_list_code:
        
        recommendations_url_list.append("https:"+webpage['href'])

    # delete duplicate URL's
    recommendations_url_list = [i for n, i in enumerate(recommendations_url_list) if i not in recommendations_url_list[:n]]

    # prints out all the scraped data

    print("Author: ",author_name)
    print("Recipe: ",recipe_name)
    for info in recipe_info_list_text:
        print(info)
    print("\nIngredients:\n")
    for ingredient in ingredient_list_text:
        print(ingredient)
    print("\nDirections\n")
    " ".join(cooking_instruction_list_text[0].split())
    instruction_number = 1
    for instruction in cooking_instruction_list_text:
        print(instruction_number,". "," ".join(instruction.split()),'\n')
        instruction_number+=1
    print('\n\n')
    
    # returns a list of URLs to recommeded recipes
    return recommendations_url_list

def run():

    bad_webpages = []


    try:
        urls = scrape(url)
    except:
        # prints out the URL that caused the program to throw 
        # an error
        print('\nIt messed up at ',url,'\n')
        
        # adds the webpage to a list of webpages that messed
        # up while navigating FoodNetwork.com recipes
        bad_webpages.append(url)

    # adds the URL that was just scraped to the list of visited
    # webpages so the script won't keep looking at the same one
    # and get caught in an infinite recursive loop
    visited_webpages.append(url)

    index = 0
    
    # the program scrapes until it has either:
    # Scraped 10 webpages, or
    # Ran out of valid webpages to scrape
    while(len(visited_webpages) < 10 and len(urls) > index):
        #print('made it to the while')
        # check if the url has been previously visited
        if urls[index] not in visited_webpages:
            # append the current url to the list of visited webpages
            
            visited_webpages.append(urls[index])

            try:
                # adds the list of recommended URLs from the
                # webpage that was just scraped to urls
                urls.extend(scrape(urls[index]))
            except:
                # prints out the URL that caused the program 
                # to throw an error
                print('\nIt messed up at ',urls[index],'\n')
                
                # adds the webpage to a list of webpages that 
                # messed up while navigating FoodNetwork.com  
                # recipes
                bad_webpages.append(urls[index])
            
        index += 1

    # prints out a list of the URLs that caused an error

    print('\n\nList of websites that it messed up at: \n')
    for webpage in bad_webpages:
        print(webpage,'\n')

    # prints out a list of the URLs that were visited

    print('\n\nList of visited webpages: \n')
    for webpage in visited_webpages:
        print(webpage,'\n')

    
    
    if len(bad_webpages) == 0:
        print('\n\nThere were no errors.\n')
    else:
        # if errors are encountered, it will print out how many
        # there were
        print('\n\nThere were ',len(bad_webpages),' errors.\n')


run()
