import requests
from bs4 import BeautifulSoup

from playwright.sync_api import sync_playwright


if __name__ == '__main__':
    """
    url = "https://www.ville-ideale.fr/villespardepts.php"
    page = requests.get(url)

    soup = BeautifulSoup(page.content, "html.parser")

    liens = soup.select('p#listedepts a')

    for a in liens:
        print(a.text, a['href'])
    """

    url = "https://www.ville-ideale.fr/villespardepts.php"

    with sync_playwright() as p:
        browser = p.firefox.launch(headless=True)
        page = browser.new_page()

        page.goto(url)

        links_locator = page.locator('p#listedepts a')
        links_locator = links_locator.all()

        for a in links_locator:
            txt = a.inner_text()
            href = a.get_attribute('href')
            print(f"{txt} -> {href}")
            #a.click()
            #villes = page.locator('div#depart a')
            #print(villes)

        browser.close()
