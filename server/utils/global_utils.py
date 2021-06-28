from os.path import dirname, sep


SRC_DIR= dirname(dirname(__file__)) + sep
PROJ_DIR= dirname(dirname(SRC_DIR)) + sep

DATA_DIR= PROJ_DIR + "data" + sep
CACHE_DIR= PROJ_DIR + "cache" + sep
CONFIG_DIR= PROJ_DIR + "config" + sep
LOG_DIR= PROJ_DIR + "logs" + sep

LOGGING_CONFIG= CONFIG_DIR + "logging.yaml" # @todo
CONFIG_FILE= CONFIG_DIR + "config.yaml"
DICTIONARY_FILE= DATA_DIR + "words.yaml"
RANGES_FILE= DATA_DIR + "ranges.json"

AUCTION_DIR= DATA_DIR + "auctions/"
AUCTION_CACHE_DIR= CACHE_DIR + "auctions/"
AUCTION_TEMPLATES= DATA_DIR + "auction_templates.yaml"
AUCTION_FORMAT_CONFIG= CONFIG_DIR + "format_settings.yaml"

PAGES_DIR= PROJ_DIR + sep + "client" + sep + "dist" + sep
TIMER_PAGE= PAGES_DIR + "timer_page.html"
TIMER_BACKGROUND_DIR= "timer_backgrounds" + sep