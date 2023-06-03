from common.models import ComicInfo
from ExternalSources.MetadataSources import ScraperFactory

scraper = ScraperFactory().get_scraper("AniList")
cinfo = ComicInfo()
cinfo.series = "My Dress-Up Darling"
ret_cinfo = scraper.get_cinfo(cinfo)
print(ret_cinfo)
