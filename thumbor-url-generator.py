#!/usr/bin/env python
import logging
from argparse import ArgumentParser
from os import getenv
from pathlib import Path
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


def parse_args():
    """Parses the arguments."""
    parser = ArgumentParser(description="Thumbor URL generator")
    parser.add_argument(
        "-c", "--copy", default=False, action="store_true", help="Copy to clipboard"
    )
    parser.add_argument("-e", "--env_file", default=None, help="Path to .env file")
    parser.add_argument("-H", "--height", type=int, help="Height of the image")
    parser.add_argument(
        "-S", "--smart", default=True, action="store_true", help="Use smart cropping"
    )
    parser.add_argument(
        "-u", "--unsafe", default=False, action="store_true", help="Generate unsafe url"
    )
    parser.add_argument(
        "-v",
        "--verbose",
        action="count",
        default=0,
        help="Verbosity, can be used multiple times, default is disabled, -v for info, -vv for debug",
    )
    parser.add_argument("-W", "--width", type=int, help="Width of the image")
    parser.add_argument("image_url", help="Image URL")
    return parser.parse_args()


def encode_url(in_url: str) -> str:
    """Encodes the url by replacing : with %3A and / with %2F."""
    try:
        t_url = parse.quote(in_url)
        t_url = t_url.replace("/", "%2F")
    except Exception as e:
        logger.error(e)
        raise e
    logger.debug("Encoded URL: %s", t_url)
    return t_url


def generate_unsafe_url(
    thumbor_base_url: str,
    in_image_url: str,
    img_width: int,
    img_height: int,
    is_smart=True,
    is_copy=False,
) -> str:
    """Generates unsafe url for thumbor."""
    encoded_url = encode_url(in_image_url)
    if encode_url is None:
        logger.error("Encoded URL is None")
        raise Exception("Encoded URL is None")
    unsafe_url = (
        (
            thumbor_base_url
            + "/unsafe/"
            + img_width
            + "x"
            + img_height
            + "/smart/"
            + encoded_url
        )
        if is_smart
        else (
            thumbor_base_url
            + "/unsafe/"
            + img_width
            + "x"
            + img_height
            + "/"
            + encoded_url
        )
    )
    logger.info("Generated URL: %s", unsafe_url)
    unsafe_url = unsafe_url.strip()
    if is_copy:
        copy(unsafe_url)
    return unsafe_url


def generate_safe_url(
    thumbor_base_url,
    thumbor_key,
    in_image_url: str,
    img_width: int,
    img_height: int,
    is_smart=True,
    is_copy=False,
) -> str:
    """Generates safe url for thumbor."""
    try:
        crypto = CryptoURL(key=thumbor_key)
    except Exception as err:
        logger.error(err)
        raise err

    encoded_url: str = encode_url(in_image_url)
    if encode_url is None:
        logger.error("Encoded URL is None")
        raise Exception("Encoded URL is None")

    encrypted_url: str = crypto.generate(
        width=img_width,
        height=img_height,
        smart=is_smart,
        image_url=encoded_url,
    )

    safe_url = thumbor_base_url + encrypted_url
    safe_url = safe_url.strip()
    logger.info("Encrypted url: %s", encrypted_url)
    logger.info("Generated URL: %s", safe_url)
    if is_copy:
        copy(safe_url)
    return safe_url


if __name__ == "__main__":
    args = parse_args()
    if args.verbose > 0:
        if args.verbose == 1:
            logger.setLevel(logging.INFO)
        elif args.verbose == 2:
            logger.setLevel(logging.DEBUG)
    else:
        logger.setLevel(logging.CRITICAL)
    env_file = args.env_file
    if env_file is None:
        env_file = (
            getenv("XDG_CONFIG_HOME") + "/thumbor-url-generator/config"
            if getenv("XDG_CONFIG_HOME") is not None
            else getenv("HOME") + "/.config/thumbor-url-generator/config"
        )
    logger.debug("env_file: %s", env_file)
    assert Path(env_file).exists(), f"{env_file} does not exist"
    load_dotenv(env_file)

    THUMBOR_BASE_URL = getenv("THUMBOR_BASE_URL")
    assert THUMBOR_BASE_URL is not None, "THUMBOR_BASE_URL is not set"
    THUMBOR_KEY = getenv("THUMBOR_KEY")
    assert THUMBOR_KEY is not None, "THUMBOR_KEY is not set"

    e_width = getenv("WIDTH")
    e_height = getenv("HEIGHT")
    e_smart = getenv("SMART")
    e_unsafe = getenv("UNSAFE")
    e_copy = getenv("COPY")

    logger.debug("Environment variables:")
    logger.debug("THUMBOR_BASE_URL: %s", THUMBOR_BASE_URL)
    logger.debug("THUMBOR_KEY: %s", THUMBOR_KEY)
    logger.debug("WIDTH: %s", e_width)
    logger.debug("HEIGHT: %s", e_height)
    logger.debug("SMART: %s", e_smart)
    logger.debug("COPY: %s", e_copy)
    logger.debug("UNSAFE: %s", e_unsafe)

    width = args.width if args.width is not None else e_width
    height = args.height if args.height is not None else e_height
    smart = args.smart if args.smart is not None else e_smart
    unsafe = args.unsafe if args.unsafe is not None else e_unsafe
    cpy = args.copy if args.copy is not None else e_copy

    if width is None and height is None:
        logger.error("Width or height is required")
        raise Exception("Width or height is required")

    if width is None:
        width = 0
    if height is None:
        height = 0

    logger.debug("\nFunction arguments:")
    logger.debug("WIDTH: %s", width)
    logger.debug("HEIGHT: %s", height)
    logger.debug("SMART: %s", smart)
    logger.debug("COPY: %s", cpy)
    logger.debug("UNSAFE: %s", unsafe)

    url = (
        generate_unsafe_url(THUMBOR_BASE_URL, args.image_url, width, height, smart, cpy)
        if unsafe
        else generate_safe_url(
            THUMBOR_BASE_URL,
            THUMBOR_KEY,
            args.image_url,
            width,
            height,
            smart,
            cpy,
        )
    )
    print()
    print("URL:", url)
