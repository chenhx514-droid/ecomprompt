from .promptbase import PromptBaseCrawler
from .xiaohongshu import XiaohongshuCrawler

CRAWLERS = {
    "promptbase": PromptBaseCrawler(),
    "xiaohongshu": XiaohongshuCrawler(),
}
