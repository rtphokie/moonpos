'''
Created on Jan 8, 2017

@author: trice
'''
import unittest
import ephem
from twitter_config import saturntwitter, jupitertwitter
from twitter import *
import logging
import sys
linelen = 65
maxradii = 30

def setup_custom_logger(name):
    formatter = logging.Formatter(fmt='%(asctime)s %(levelname)-8s %(message)s',
                                  datefmt='%Y-%m-%d %H:%M:%S')
    handler = logging.FileHandler('%s_log.txt' % name, mode='w')
    handler.setFormatter(formatter)
    screen_handler = logging.StreamHandler(stream=sys.stdout)
    screen_handler.setFormatter(formatter)
    logger = logging.getLogger(name)
    logger.setLevel(logging.DEBUG)
    logger.addHandler(handler)
    logger.addHandler(screen_handler)
    return logger


def asciimoonpos(moons, planet, duration=2, legend=False):
    interval = ephem.hour * 3
    now = ephem.now()
    now -= now % interval
    result = ""
        
    t = now
    while t < now + duration:
        line = ['-'] * linelen
        put(line, planet, 0)
        for moon, character in moons:
            moon.compute(t)
            put(line, character, moon.x)
        result += ''.join(line).rstrip()
        result += " "
        result += str(ephem.date(t))
        result += "\n"
        t += interval
    if legend:
        result += ', '.join([ '%s = %s' % (c, m.name) for m, c in moons ]) 
        result += "\n"
    result = result.strip()
    return result.strip() 

def put(line, character, radii):
    if abs(radii) > maxradii:
        return
    offset = radii / maxradii * (linelen - 1) / 2
    i = int(linelen / 2 + offset)
    line[i] = character


def Jupiter():
    Jupiter = ((ephem.Io(), 'i'),
             (ephem.Europa(), 'e'),
             (ephem.Ganymede(), 'g'),
             (ephem.Callisto(), 'c'))
    try:
        t = Twitter(
                auth=OAuth(jupitertwitter['AccessToken'], 
                           jupitertwitter['AccessTokenSecret'],
                           jupitertwitter['ConsumerKey'], 
                           jupitertwitter['ConsumerSecret'])
               )
    except:
        t = None
        
    return asciimoonpos(Jupiter, 'J', duration=.1),  t, 'jupitermoonpos'

def Saturn():
    Saturn = ((ephem.Titan(), 'T'),
            (ephem.Mimas(), 'm'),
            (ephem.Rhea(), 'r'),
            (ephem.Dione(), 'd'),
            (ephem.Tethys(), 't'),
            (ephem.Enceladus(), 'e'),
            (ephem.Hyperion(), 'h'),
            (ephem.Tethys(), 't'))
    try:
        t = Twitter(
                auth=OAuth(saturntwitter['AccessToken'], 
                           saturntwitter['AccessTokenSecret'],
                           saturntwitter['ConsumerKey'], 
                           saturntwitter['ConsumerSecret'])
               )
    except:
        t = None

    return asciimoonpos(Saturn, 'S', duration=.1), t, 'saturnmoonpos'

def postit(t, twitteruser, message, timelinesize=5):
    timeline = t.statuses.user_timeline(screen_name = twitteruser, count=timelinesize)
    
    duplicate = False
    for post in timeline:
        duplicate = duplicate or post['text'] == message
    return not duplicate
        
class Test(unittest.TestCase):

    def testJupiter(self):
        message, t = Jupiter()
        self.assertTrue('J' in message)
        self.assertTrue(':' in message)
        self.assertTrue('---' in message)
        self.assertEqual(len (message), 84)


    def testSaturn(self):
        message, t = Saturn()
        self.assertTrue('S' in message)
        self.assertTrue(':' in message)
        self.assertTrue('---' in message)
        self.assertEqual(len (message), 84)


if __name__ == "__main__":
    logger = setup_custom_logger('moonpos')
    
    for work in [Jupiter(), Saturn()]:
        message, t, userid = work
        print '--'*20
        print userid
        if postit(t, userid, message):
            result = t.statuses.update( status=message) 
            logger.info(message)
            logger.info('posted %s ASCII map' % userid)
        else:
            logger.warn(message)
            logger.error('skipping %s duplicate' % userid)
            
        
