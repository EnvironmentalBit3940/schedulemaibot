import vk


session = vk.Session(access_token='21e3a0cd21e3a0cd21e3a0cd4021ba9bfd221e321e3a0cd7a3c87daa75945317b8e0fed')
#session = vk.AuthSession('293283105', '+79688411209', 'PeR83973')
vk_api = vk.API(session, v='5.68')

def get_ovearhear_news():
	
	return vk_api.wall.search(owner_id=-58942429, domain='https://vk.com/overhear_mai', query='#новости_недели@overhear_mai', count=1)['items'][0]['text']

print(vk_api.wall.search(owner_id=-58942429, domain='https://vk.com/overhear_mai', query='#новости_недели@overhear_mai', count=1)['items'][0]['text'])
#print(vk_api.search.getHints())
