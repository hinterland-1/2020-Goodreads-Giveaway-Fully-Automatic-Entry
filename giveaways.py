import requests
import sys
from getpass import getpass
from lxml import html



def login(session, username, password):
	page = session.get('https://www.goodreads.com/')
	tree = html.fromstring(page.content)
	form = tree.xpath('//div[@id="signInForm"]')[0]
	authenticity_token = form.xpath('.//input[@name="authenticity_token"]/@value')[0]
	n = form.xpath('.//input[@name="n"]/@value')[0]

	payload = {
		'user[email]': username,
		'user[password]': password,
		'remember_me': 'on',
		'authenticity_token': authenticity_token,
		'n': n
	}
	response = session.post('https://www.goodreads.com/user/sign_in?source=home', data=payload)
	print('[*] Successfully logged in to Goodreads!')


def scrape_giveaways(session):
	giveaways = []
	count = 1

	while True:
		page = session.get('https://www.goodreads.com/giveaway?filter=print&sort=recently_listed&tab=recently_listed', params={'page': count})
		tree = html.fromstring(page.content)
		lis = tree.xpath('//li[@class="listElement giveawayListItem"]')

		if not lis: break

		for li in lis:
			timeDelay = random.uniform(0.1, 0.5)
			time.sleep(timeDelay)
			print(timeDelay, "Seconds Delay")
			ID = int(li.xpath('.//a[@class="actionLink detailsLink"]/@href')[0].rsplit('/', 1)[-1].split('-')[0])
			entered = not bool(li.xpath('.//a[@class="gr-button"]/@href'))
			giveaway = {
				'Name': li.xpath('.//a[@class="bookTitle"]/text()')[0],
				'URL': li.xpath('.//a[@class="bookTitle"]/@href')[0],
				'Entered': entered,
				'ID': ID
			}
			giveaways.append(giveaway)
		
		count = count + 1

	print('[*] {} giveaways scraped.'.format(len(giveaways)))
	return giveaways


def enter_giveaway(session, identifier):
	page = session.get('https://www.goodreads.com/giveaway/enter_choose_address/{}'.format(identifier))
	tree = html.fromstring(page.content)
	try:
		address = int(tree.xpath('//a[@class="gr-button gr-button--small"]/@id')[0][13:])
	except IndexError:
		print('''
[!] Looks like you didn\'t read the README properly. That\'s a shame. 
    Here\'s an important and relevant part of the README restated.

    Before running the script, make sure you've entered a giveaway manually at least once. The first time involves setting up a new address, and the script assumes that it's done.
			''')
		sys.exit()

	
	page = session.get('https://www.goodreads.com/giveaway/enter_print_giveaway/{}'.format(identifier), params={'address': address})
	tree = html.fromstring(page.content)
	authenticity_token = tree.xpath('//input[@name="authenticity_token"]/@value')[0]

	payload = {
		'authenticity_token': authenticity_token,
		'entry_terms': 1,
		'commit': 'Enter Giveaway'
	}
	response = session.post('https://www.goodreads.com/giveaway/enter_print_giveaway/{}'.format(identifier),
							params={'address': address}, data=payload)


def main():	
	session = requests.Session()
	username = input('[?] Enter your Goodreads username: ')
	password = getpass('[?] Enter your Goodreads password: ')
	login(session, username, password)
	giveaways = scrape_giveaways(session)
	print()

	for giveaway in giveaways:
		if not giveaway['Entered']:
			timeDelay = random.uniform(0.1, 0.5)
			time.sleep(timeDelay)
			print(timeDelay, "Seconds Delay")
			enter_giveaway(session, giveaway['ID'])
			print('[*] Entered giveaway for: {0} - {1}'.format(giveaway['Name'], giveaway['ID']))



if __name__=='__main__':
	main()
