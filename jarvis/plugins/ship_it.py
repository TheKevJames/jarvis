"""
I have been configured to help you "ship it" upon command.
"""
import random

from ..plugin import Plugin


squirrels = [
    ('http://images.cheezburger.com/completestore/2011/11/2/'
     'aa83c0c4-2123-4bd3-8097-966c9461b30c.jpg'),
    ('http://images.cheezburger.com/completestore/2011/11/2/'
     '46e81db3-bead-4e2e-a157-8edd0339192f.jpg'),
    'http://28.media.tumblr.com/tumblr_lybw63nzPp1r5bvcto1_500.jpg',
    'http://i.imgur.com/DPVM1.png',
    'http://d2f8dzk2mhcqts.cloudfront.net/0772_PEW_Roundup/09_Squirrel.jpg',
    'http://www.cybersalt.org/images/funnypictures/s/supersquirrel.jpg',
    'http://www.zmescience.com/wp-content/uploads/2010/09/squirrel.jpg',
    'http://img70.imageshack.us/img70/4853/cutesquirrels27rn9.jpg',
    'http://img70.imageshack.us/img70/9615/cutesquirrels15ac7.jpg',
    'https://dl.dropboxusercontent.com/u/602885/github/sniper-squirrel.jpg',
    ('http://1.bp.blogspot.com/_v0neUj-VDa4/TFBEbqFQcII/AAAAAAAAFBU/'
     'E8kPNmF1h1E/s640/squirrelbacca-thumb.jpg'),
    'https://dl.dropboxusercontent.com/u/602885/github/squirrelmobster.jpeg',
    'http://cdn.meme.am/instances/250x250/63111222.jpg',
]


class ShipIt(Plugin):
    def __init__(self, slack):
        super(ShipIt, self).__init__(slack, 'ship_it')

    def help(self, ch):
        self.send_now(ch, __doc__.replace('\n', ' '))

    @Plugin.on_message(r'.*ship(ping)? it.*')
    def ship_it(self, ch, _user, _groups):
        self.send(ch, 'Will do, sir.')
        self.send(ch, random.choice(squirrels))
