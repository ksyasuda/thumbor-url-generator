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
    parser.add_argument(
        "-H", "--height", type=int, default=0, help="Height of the image"
    )
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
    parser.add_argument(
        "-W", "--width", type=int, default=800, help="Width of the image"
    )
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
    if is_smart:
        unsafe_url = (
            thumbor_base_url
            + "/unsafe/"
            + img_width
            + "x"
            + img_height
            + "/smart/"
            + encoded_url
        )
    else:
        unsafe_url = (
            thumbor_base_url
            + "/unsafe/"
            + img_width
            + "x"
            + img_height
            + "/smart/"
            + encoded_url
        )
    logger.info("Generated URL: %s", unsafe_url)
    if is_copy:
        copy(unsafe_url.strip())
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

    safe_url: str = thumbor_base_url + encrypted_url
    logger.info("Encrypted url: %s", encrypted_url)
    logger.info("Generated URL: %s", safe_url)
    if is_copy:
        copy(safe_url.strip())
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
    logger.debug("THUMBOR_BASE_URL: %s", THUMBOR_BASE_URL)
    logger.debug("THUMBOR_KEY: %s", THUMBOR_KEY)

    t_width = getenv("WIDTH")
    t_height = getenv("HEIGHT")
    t_smart = getenv("SMART")
    t_unsafe = getenv("UNSAFE")
    t_copy = getenv("COPY")

    logger.debug("Environment variables:")
    logger.debug("WIDTH: %s", t_width)
    logger.debug("HEIGHT: %s", t_height)
    logger.debug("SMART: %s", t_smart)
    logger.debug("COPY: %s", t_copy)
    logger.debug("UNSAFE: %s", t_unsafe)

    width = int(t_width) if t_width is not None else args.width
    height = int(t_height) if t_height is not None else args.height
    smart = t_smart == "True" if t_smart is not None else args.smart
    cpy = t_copy == "True" if t_copy is not None else args.copy
    unsafe = t_unsafe == "True" if t_unsafe is not None else args.unsafe

    logger.debug("Args:")
    logger.debug("Width: %s", width)
    logger.debug("Height: %s", height)
    logger.debug("Smart: %s", smart)
    logger.debug("Copy: %s", copy)
    logger.debug("Unsafe: %s", unsafe)

    url = ""
    if unsafe:
        url = generate_unsafe_url(
            THUMBOR_BASE_URL, args.image_url, width, height, smart, cpy
        )
    else:
        url = generate_safe_url(
            THUMBOR_BASE_URL,
            THUMBOR_KEY,
            args.image_url,
            width,
            height,
            smart,
            cpy,
        )

    print()
    print("URL:", url)
