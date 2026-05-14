from .promptbase import PromptBaseCrawler
from .civitai import CivitaiCrawler
from .xiaohongshu import XiaohongshuCrawler
from .github import GitHubCrawler
from .liblib import LiblibCrawler
from .runninghub import RunninghubCrawler
from .youmind import YoumindCrawler
from .twitter import TwitterCrawler
from .gptimage2 import GptImage2Crawler
from .neospark import NeoSparkCrawler

CRAWLERS = {
    "liblib": LiblibCrawler(),
    "github": GitHubCrawler(),
    "civitai": CivitaiCrawler(),
    "runninghub": RunninghubCrawler(),
    "youmind": YoumindCrawler(),
    "twitter": TwitterCrawler(),
    "gptimage2": GptImage2Crawler(),
    "neospark": NeoSparkCrawler(),
    "promptbase": PromptBaseCrawler(),
    "xiaohongshu": XiaohongshuCrawler(),
}
