import requests
import csv
import time
from bs4 import BeautifulSoup
import logging
from pydrive.auth import GoogleAuth
from pydrive.drive import GoogleDrive
import click
from clint.textui import puts, colored, indent
from datetime import datetime
from progress.bar import Bar


def callback(context, param, value):
    if value == 'n':
        return False
    else:
        return True


@click.command()
@click.option('--name', prompt='What is the name of the subreddit you want to scrape?')
@click.option('--yes-drive', default=False, callback=callback, prompt='Do you want a to upload a copy of the '
                                                                      'generated .csv to your '
                                                                      'Google Drive? [y/n]')
def main(name, yes_drive):
    print('subreddit:', name)

    g_drive = None
    if yes_drive is True:
        g_auth = GoogleAuth()
        g_auth.LocalWebserverAuth()
        print('g auth', g_auth)
        g_drive = GoogleDrive(g_auth)

    logging.basicConfig(filename='index.log', level=logging.DEBUG)

    base_url = 'https://old.reddit.com'
    target_url = 'https://reddit.com'
    scraper_url = base_url + '/r/' + name + '/new/'

    headers = {'User-Agent': 'Mozilla/5.0'}

    page = requests.get(scraper_url, headers=headers)

    soup = BeautifulSoup(page.text, 'html.parser')

    posts = soup.findAll('div', {'class': 'top-matter'})

    with Bar('processing...') as bar:
        counter = 1
        while counter <= 100:
            for p in posts:
                is_ad = p.find('span', {'class': 'promoted-tag'})
                if is_ad is None:
                    raw_flair = p.find('span', {'class': 'linkflairlabel'})
                    flair = None
                    if raw_flair is not None:
                        flair = raw_flair.text
                    if name == 'hardwareswap':
                        if flair != 'OFFICIAL' and flair != 'BUYING' and flair != 'CLOSED':
                            title_href = p.find('a', {'class': 'title'})['href']
                            title = p.find('a', {'class': 'title'}).text
                            built_url = target_url + title_href
                            utc_time_posted = p.find('time', {'class': 'live-timestamp'}).text
                            date_now = datetime.now()
                            timestamp = date_now.strftime('%d-%b-%Y')

                            post_line = [utc_time_posted, flair, title, title_href, built_url]

                            file_name = name + '-' + timestamp + '.csv'
                            file_path = 'output/' + file_name

                            with open(file_path, 'a') as f:
                                writer = csv.writer(f)
                                writer.writerow(post_line)

                            counter += 1
                            bar.next()

                        if yes_drive is True:
                            if counter == 100:
                                g_file = g_drive.CreateFile()
                                g_file.SetContentFile(file_path)
                                g_file.Upload()
                    else:
                        title_href = p.find('a', {'class': 'title'})['href']
                        title = p.find('a', {'class': 'title'}).text
                        built_url = target_url + title_href
                        utc_time_posted = p.find('time', {'class': 'live-timestamp'}).text
                        date_now = datetime.now()
                        timestamp = date_now.strftime('%d-%b-%Y')

                        post_line = [utc_time_posted, flair, title, title_href, built_url]

                        file_name = name + '-' + timestamp + '.csv'
                        file_path = 'output/' + file_name

                        with open(file_path, 'a') as f:
                            writer = csv.writer(f)
                            writer.writerow(post_line)

                        counter += 1
                        bar.next()

                    if yes_drive is True:
                        if counter == 100:
                            g_file = g_drive.CreateFile()
                            g_file.SetContentFile(file_path)
                            g_file.Upload()
                else:
                    continue

                next_button = soup.find('span', {'class': 'next-button'})
                next_page_link = next_button.find('a')['href']
                time.sleep(2)

                def get_next_page(u):
                    new_page = requests.get(u, headers=headers)
                    new_soup = BeautifulSoup(new_page.text, 'html.parser')
                    return new_soup

                get_next_page(next_page_link)
        else:
            bar.finish()
            with indent(4, quote='>>>'):
                if yes_drive is True:
                    message = 'finished writing rows to local .csv and uploading final copy to Google Drive!'
                else:
                    message = 'finished writing rows to local .csv file!'
                puts(colored.blue(message))


if __name__ == '__main__':
    main()
