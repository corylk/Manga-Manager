import unittest

from common.models import ComicInfo


class TestSources(unittest.TestCase):
    def test_AnilistReturnMatches(self):
        from ExternalSources.MetadataSources import ScraperFactory
        scraper = ScraperFactory().get_scraper("AniList")
        cinfo = ComicInfo()
        cinfo.series = "tensei shitara datta ken"

        ret_cinfo = scraper.get_cinfo(cinfo)
        print("Assert series name matches")
        self.assertEqual("Tensei Shitara Slime Datta Ken", ret_cinfo.series)
        print("Assert loc series name matches")
        self.assertEqual("That Time I Got Reincarnated as a Slime", ret_cinfo.localized_series)
