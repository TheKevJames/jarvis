"""
I have been configured to help you "ship it" upon command.
"""
import random

import jarvis.core.messages as messages
import jarvis.core.plugin as plugin


squirrels = [
    'http://28.media.tumblr.com/tumblr_lybw63nzPp1r5bvcto1_500.jpg',
    'http://cdn.meme.am/instances/250x250/63111222.jpg',
    'http://d2f8dzk2mhcqts.cloudfront.net/0772_PEW_Roundup/09_Squirrel.jpg',
    'http://i.imgur.com/DPVM1.png',
    'http://www.cybersalt.org/images/funnypictures/s/supersquirrel.jpg',
    'http://www.zmescience.com/wp-content/uploads/2010/09/squirrel.jpg',
    'https://dl.dropboxusercontent.com/u/602885/github/sniper-squirrel.jpg',
    'https://dl.dropboxusercontent.com/u/602885/github/squirrelmobster.jpeg',
    'https://qph.ec.quoracdn.net/main-qimg-97416d586555b6d0fb8c1394642b1fa6',
    ('http://1.bp.blogspot.com/_v0neUj-VDa4/TFBEbqFQcII/AAAAAAAAFBU/'
     'E8kPNmF1h1E/s640/squirrelbacca-thumb.jpg'),
    ('http://40.media.tumblr.com/8732a803c04c32dbc04c6cb37add2c44/'
     'tumblr_nm3d0o27Rc1urg4cfo1_500.jpg'),
]


class ShipIt(plugin.Plugin):
    def __init__(self, slack):
        super(ShipIt, self).__init__(slack, 'ship_it')

    def help(self, ch):
        self.send_now(ch, __doc__.replace('\n', ' '))

    @plugin.Plugin.on_words(['ship', 'it'])
    def ship_it(self, ch, _user, _groups):
        self.send(ch, messages.ACKNOWLEDGE())
        self.send(ch, random.choice(squirrels))
