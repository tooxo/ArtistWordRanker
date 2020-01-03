import re
import string


# TODO add unit tests


class LyricsCleanup:
    @staticmethod
    def lyrics_wikia_remove_artists(lyrics: str):
        """
        This removes some html tags from specific lyrics-wikia lyrics,
        which state the current singer in bold and italic
        :param lyrics: lyrics to filter
        :return: filtered lyrics
        """
        thick_regex = r"<[\w]+>[\w]+<\/[\w]>: "
        lyrics = re.sub(pattern=thick_regex, string=lyrics, repl="")
        italic_regex = r"<i>\([^)]+\)</i>"
        return re.sub(pattern=italic_regex, string=lyrics, repl="")

    @staticmethod
    def remove_html_tags(lyrics: str):
        """
        This removes any other html tags from the lyrics
        (the regex was stolen from here: https://www.regextester.com/93515)
        :param lyrics: input lyrics
        :return: filtered lyrics
        """
        html_tag_regex = r"<[^>]*>"
        return re.sub(pattern=html_tag_regex, string=lyrics, repl="")

    @staticmethod
    def remove_square_brackets(lyrics: str):
        """
        remove square brackets with text inside (mostly unimportant)
        :param lyrics:
        :return:
        """
        square_regex = r"\[[^\]]+\]"
        return re.sub(pattern=square_regex, string=lyrics, repl="")

    @staticmethod
    def remove_double_spaces(lyrics: str):
        while "  " in lyrics:
            lyrics = lyrics.replace("  ", " ")
        return lyrics

    @staticmethod
    def remove_start_and_end_spaces(lyrics: str):
        start_of_line = r"^[ ]+"
        end_of_line = r"[ ]+$"
        lyrics = re.sub(pattern=start_of_line, string=lyrics, repl="")
        lyrics = re.sub(pattern=end_of_line, string=lyrics, repl="")
        return lyrics

    @staticmethod
    def clean_up(lyrics: str):
        """
        runs all of them
        :param lyrics:
        :return:
        """
        return LyricsCleanup.remove_start_and_end_spaces(
            LyricsCleanup.remove_double_spaces(
                LyricsCleanup.remove_square_brackets(
                    LyricsCleanup.remove_html_tags(
                        LyricsCleanup.lyrics_wikia_remove_artists(lyrics=lyrics)
                    )
                )
            )
        )
