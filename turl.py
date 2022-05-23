#!/usr/bin/env python
import logging
from argparse import ArgumentParser
from os import getenv
from urllib import parse

from dotenv import load_dotenv
from libthumbor import CryptoURL
from pyperclip import copy

logging.basicConfig(
    level=logging.DEBUG,
    format="%(message)s",
    handlers=[logging.StreamHandler()],
)
logger = logging.getLogger(__name__)

load_dotenv("/home/sudacode/Projects/Python/thumbor/.env")

THUMBOR_URL = "https://thumbor.sudacode.com"
KEY = getenv("THUMBOR_KEY")
assert KEY is not None and KEY != ""
crypto = CryptoURL(key=KEY)


def parse_args():
    """Parses the arguments."""
    parser = ArgumentParser(description="Thumbor URL generator")
    parser.add_argument(
        "-W", "--width", type=int, default=800, help="Width of the image"
    )
    parser.add_argument(
        "-H", "--height", type=int, default=0, help="Height of the image"
    )
    parser.add_argument(
        "-S", "--smart", default=True, action="store_true", help="Use smart cropping"
    )
    parser.add_argument(
        "-c", "--copy", default=False, action="store_true", help="Copy to clipboard"
    )
    parser.add_argument("image_url", help="Image URL")
    return parser.parse_args()


def encode_url(in_url) -> str:
    """Encodes the url by replacing : with %3A and / with %2F."""
    try:
        t_url = parse.quote(in_url)
        t_url = t_url.replace("/", "%2F")
    except Exception as e:
        logger.error(e)
        raise e
    logger.debug("Encoded URL: %s", t_url)
    return t_url


def generate_safe_url(
    in_image_url: str, width: int, height: int, smart: bool, is_copy=False
):
    """Generates safe url for thumbor."""
    encoded_url = encode_url(in_image_url)
    encrypted_url = crypto.generate(
        width=width,
        height=height,
        smart=smart,
        image_url=encoded_url,
    )

    logger.debug("Encrypted url: %s", encrypted_url)
    url = THUMBOR_URL + encrypted_url
    logger.info("Generated URL: %s", url)
    if is_copy:
        copy(url.strip())


if __name__ == "__main__":
    args = parse_args()
    logger.debug("Arguments: %s", args)
    generate_safe_url(args.image_url, args.width, args.height, args.smart, args.copy)
