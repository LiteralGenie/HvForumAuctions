from .config_utils import load_config
from bs4 import BeautifulSoup
import aiohttp


async def get_soup(link, session):
	html= await get_html(link, session)
	return BeautifulSoup(html, 'html.parser')

def get_session():
	# keep-alive because https://github.com/aio-libs/aiohttp/issues/3904#issuecomment-632661245
	return aiohttp.ClientSession(headers={'Connection': 'keep-alive',
										  'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:77.0) Gecko/20100101 Firefox/77.0'
					  			})

async def get_html(link, session=None):
	close_session= not bool(session)
	session= session or get_session()
	# @todo: close

	resp= await session.get(link)

	if not resp.status == 200:
		raise Exception # @todo logging
	else:
		text= await resp.text(encoding='utf-8', errors='ignore')
		return text

async def do_forum_login(session=None):
	CONFIG= load_config()
	if session is None:
		session= get_session()
	else:
		html= await get_html("https://forums.e-hentai.org/", session)
		soup= BeautifulSoup(html, 'html.parser')
		if not soup.find(class_='pcen'): # already logged in
			return session

	login_data= {
		'UserName': CONFIG['forum_name'],
		'PassWord': CONFIG['forum_pass'],
		'act': "Login",
		'CODE': "01",
		'referer': "act=Login&CODE=01",
		"CookieDate": "1"
	}
	login_link= 'https://forums.e-hentai.org/index.php?act=Login&CODE=00'

	await session.post(login_link, data=login_data)

	resp= await session.get('https://forums.e-hentai.org/index.php?act=idx')
	text= str(await resp.content.read())
	assert 'Welcome Guest' not in (text)

	return session

async def do_hv_login(session=None):
	if session is None:
		session= get_session()

	hv_link= "https://hentaiverse.org"
	test_link= hv_link + "/equip/1/test"
	invalid_string= "You must be logged on to visit the HentaiVerse."

	resp= await get_html(test_link, session)
	if invalid_string in resp:
		await do_forum_login(session)
		resp= await get_html(hv_link, session)
		assert invalid_string not in resp

	return session