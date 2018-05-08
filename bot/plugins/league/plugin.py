"""
I will inform you whenever a new set of patch notes is released on Riot's feed.
"""
import logging

import aiohttp
import bs4
import jarvis.core.plugin as plugin


logger = logging.getLogger(__name__)


CHANNEL = 'league-of-legends'

BASE_URL = 'http://oce.leagueoflegends.com'
PATCH_URL = '{}/en/news/game-updates/patch'.format(BASE_URL)

PATCH_TEASER_SOUP = '.views-row-1 .default-2-3 .teaser-content div'
PATCH_TITLE_SOUP = '.views-row-1 .default-2-3 h4 a'


class League(plugin.Plugin):
    def help(self, ch):
        self.send_now(ch, __doc__.replace('\n', ' '))

    @plugin.Plugin.on_api('POST', 'new_patch')
    async def new_patch(self, request):
        await request.post()
        logger.debug('Scraping new patch data.')

        async with aiohttp.ClientSession() as session:
            async with session.get(PATCH_URL) as resp:
                html = await resp.text()

        soup = bs4.BeautifulSoup(html, 'html.parser')
        teaser = soup.select(PATCH_TEASER_SOUP)[0]
        header = soup.select(PATCH_TITLE_SOUP)[0]

        link = BASE_URL + header['href']
        self.send_attachment(CHANNEL, {
            'author_name': 'Riot Games',
            'color': '#36a64f',
            'fallback': link,
            'pretext': 'Sir, Riot Games has provided new patch notes.',
            'text': teaser.text,
            'title': header.text,
            'title_link': link,
        })

        return aiohttp.web.Response(text='ok')
