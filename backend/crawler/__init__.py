from .promptbase import PromptBaseCrawler
from .civitai import CivitaiCrawler
from .xiaohongshu import XiaohongshuCrawler
from .github import GitHubCrawler
from .liblib import LiblibCrawler
from .runninghub import RunninghubCrawler

CRAWLERS = {
    "liblib": LiblibCrawler(),
    "github": GitHubCrawler(),
    "civitai": CivitaiCrawler(),
    "runninghub": RunninghubCrawler(),
    "promptbase": PromptBaseCrawler(),
    "xiaohongshu": XiaohongshuCrawler(),
}
