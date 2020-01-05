# -*- coding: utf-8 -*-

import unittest
from backend.lyrics_cleanup import LyricsCleanup


class Test(unittest.TestCase):
    lyrics_strip = [
        (
            "<i>(Dr. Dre)</i> Marshall, sounds like an S.O.S. <i>(Eminem)</i> Holy wack unlyrical lyrics André, youre "
            "fucking right! <i>(Dr. Dre)</i> To the rap mobile, lets go!  <i>(Lady)</i> Marshall! Marshall! "
            "<i>(Eminem)</i> Bitches and gentlemen Its showtime Hurry, hurry step right up Introducing the star of our "
            "show; his name is… <i>(Lady)</i> Marshall! <i>(Eminem)</i> You wouldnt wanna be anywhere else in the world"
            " right now So without futher ado, I bring to you… <i>(Lady)</i> Marshall!  <i>(Eminem)</i> Your bout to "
            "witness hip-hop in its most purest Most rawest form, flow almost flawless Most hardest, most honest known "
            "artist Chip off the old block, but old doc is back Looks like Batman brought his own Robin Oh god, Sadams "
            "got his own Laden With his own private plane, his own pilot Set to blow college dorm room doors off the "
            "hinges Oranges, peach, pears, plums, syringes Vrrm, vrrm, yeah, here I come, Im inches Away from you, "
            "dear fear none Hip-hop is in a state of 9-11, so Lets get down to business I dont got no time to play "
            "around. What is this? Must be a circus in town; lets shut that shit down On these clowns. Can I get a "
            "witness? <i>(Dr. Dre)</i> (Hell yeah!) <i>(Eminem)</i> Lets get down to business I dont got no time to play "
            "around. What is this? Must be a circus in town; lets shut that shit down On these clowns. Can I get a "
            "witness? <i>(Dr. Dre)</i> (Hell yeah!) <i>(Eminem)</i> Quick; gotta move fast, gotta perform miracles "
            'Gee wilikers, <a href="/wiki/Dr._Dre" title="Dr. Dre">Dre</a>, holy bat syllables Look at all the '
            "bullshit that goes on in Gotham When Im gone. Time to get rid of these rap criminals So skip to "
            "your lou, while I do what I do best You aint even impressed no more; you used to it Flows too wet, "
            "nobody close to it Nobody says it, but still everyone knows the shit The most hated on out of all "
            "those who say they get hated on In eighty songs and exagerate it all so much They make it all up; theres no "
            "such thing Like a female with good looks who cooks and cleans It just means so much more to so much more "
            "People when youre rappin, and you know what for The show must go on, so I",
            "Marshall, sounds like an S.O.S. Holy wack unlyrical lyrics André, youre "
            "fucking right! To the rap mobile, lets go! Marshall! Marshall! "
            "Bitches and gentlemen Its showtime Hurry, hurry step right up Introducing the star of our "
            "show; his name is… Marshall! You wouldnt wanna be anywhere else in the world"
            " right now So without futher ado, I bring to you… Marshall! Your bout to "
            "witness hip-hop in its most purest Most rawest form, flow almost flawless Most hardest, most honest known "
            "artist Chip off the old block, but old doc is back Looks like Batman brought his own Robin Oh god, Sadams "
            "got his own Laden With his own private plane, his own pilot Set to blow college dorm room doors off the "
            "hinges Oranges, peach, pears, plums, syringes Vrrm, vrrm, yeah, here I come, Im inches Away from you, "
            "dear fear none Hip-hop is in a state of 9-11, so Lets get down to business I dont got no time to play "
            "around. What is this? Must be a circus in town; lets shut that shit down On these clowns. Can I get a "
            "witness? (Hell yeah!) Lets get down to business I dont got no time to play "
            "around. What is this? Must be a circus in town; lets shut that shit down On these clowns. Can I get a "
            "witness? (Hell yeah!) Quick; gotta move fast, gotta perform miracles "
            "Gee wilikers, Dre, holy bat syllables Look at all the "
            "bullshit that goes on in Gotham When Im gone. Time to get rid of these rap criminals So skip to "
            "your lou, while I do what I do best You aint even impressed no more; you used to it Flows too wet, "
            "nobody close to it Nobody says it, but still everyone knows the shit The most hated on out of all "
            "those who say they get hated on In eighty songs and exagerate it all so much They make it all up; theres no "
            "such thing Like a female with good looks who cooks and cleans It just means so much more to so much more "
            "People when youre rappin, and you know what for The show must go on, so I",
        )
    ]

    def test_lyrics_strip(self):
        for orig, expect in self.lyrics_strip:
            print(LyricsCleanup.clean_up(orig))
            print(expect)
            assert LyricsCleanup.clean_up(orig) == expect


if __name__ == "__main__":
    unittest.main()
