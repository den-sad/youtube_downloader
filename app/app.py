import datetime
import os
from os.path import isfile, join
from dotenv import load_dotenv
from loguru import logger

from pytube import Playlist
from pytube import YouTube
from pytube.exceptions import VideoUnavailable

import telebot
from telebot import apihelper

import owncloud
from http.client import IncompleteRead

from keyboards import (keyboard_main, keyboard_start)

load_dotenv()
LOG_PATH = os.getenv('LOG_PATH', './')
BOT_API_KEY = os.getenv('BOT_API_KEY')
ALLOWED_IDS = os.getenv('ALLOWED_IDS').split(',')
VIDEO_PATH = os.getenv('VIDEO_PATH', '/video')
OWNCLOUD_URL = os.getenv('OWNCLOUD_URL')
OWNCLOUD_USER = os.getenv('OWNCLOUD_USER')
OWNCLOUD_PASS = os.getenv('OWNCLOUD_PASS')
OWNCLOUD_DIR = os.getenv('OWNCLOUD_DIR', 'Downloads')


logger.add(f"{LOG_PATH}youtube-downloader.log", rotation="1 MB")

apihelper.SESSION_TIME_TO_LIVE = 5 * 60
bot = telebot.TeleBot(BOT_API_KEY)
logger.debug('Bot started ' + str(datetime.datetime.now()))

if not BOT_API_KEY:
    logger.error('Please set the TELEGRAM_APIKEY environment variable.')
    exit(1)
if not ALLOWED_IDS:
    logger.error('Please set the ALLOWED_IDS environment variable.')
    exit(1)
if not OWNCLOUD_URL:
    logger.error('Please set the OWNCLOUD_URL environment variable.')
    exit(1)
if not OWNCLOUD_USER:
    logger.error('Please set the OWNCLOUD_USER environment variable.')
    exit(1)
if not OWNCLOUD_PASS:
    logger.error('Please set the OWNCLOUD_PASS environment variable.')
    exit(1)


def get_file_list(dir: str) -> list:
    files = [f for f in os.listdir(dir) if isfile(
        join(dir, f)) and f.endswith('.mp4')]
    return files


def move_files_to_cloud() -> list:
    files = get_file_list(VIDEO_PATH)
    if len(files) == 0:
        logger.debug('No files to move')
        return 'Нет файлов для перемещения'
    file_links = []
    cloud = owncloud.Client(OWNCLOUD_URL)
    cloud.login(OWNCLOUD_USER, OWNCLOUD_PASS)
    for file in files:
        logger.debug(f'Moving file {file}')
        try:
            cloud.put_file(f'{OWNCLOUD_DIR}/{file}', f'{VIDEO_PATH}/{file}')
            os.remove(f'{VIDEO_PATH}/{file}')
            link = cloud.share_file_with_link(f'{OWNCLOUD_DIR}/{file}')
            file_links.append(link.get_link())
        except Exception as e:
            logger.error(f'Error moving file {file}: {e}')
    logger.debug('All files moved')
    return file_links


def download_video_file(video) -> str:
    logger.debug('Downloading started')
    try:
        video_file = video.streams.get_highest_resolution().download(
            output_path=VIDEO_PATH, max_retries=2)
        result = f'Загружено > {video_file.title()}'
        logger.debug(f'Downloaded > {video_file.title()}')
    except VideoUnavailable:
        result = f'Видео {video_file.title()} недоступно, пропускаем...'
        logger.error(f'VideoUnavailable > {video_file.title()}')
    except IncompleteRead:
        result = "Ошибка загрузки видео"
        logger.error(f'IncompleteRead > {video_file.title()}')
    except Exception as e:
        result = "Ошибка ", str(e)
        logger.error(f'ERROR > {video_file.title()} > {str(e)}')
    return result


def download_video(url: str, message: telebot.types.Message) -> None:
    youtube_video = YouTube(url)
    result = download_video_file(youtube_video)
    bot.reply_to(message, result, reply_markup=keyboard_main)
    logger.debug('Getting links for file')
    links = move_files_to_cloud()
    if len(links) > 0:
        for link in links:
            bot.reply_to(message, link, reply_markup=keyboard_main)


def download_playlist(url: str, message) -> None:
    playlist = Playlist(url)
    bot.reply_to(message, f'В листе {str(len(playlist.videos))} видео...',
                 reply_markup=keyboard_main)
    for youtube_video in playlist.videos:
        result = download_video_file(youtube_video)
        bot.reply_to(message, result, reply_markup=keyboard_main)
    logger.debug('Getting links for files')
    links = move_files_to_cloud()
    if len(links) > 0:
        for link in links:
            bot.reply_to(message, link, reply_markup=keyboard_main)
    logger.debug('All links sent')


def download_from_url(message: telebot.types.Message) -> None:
    url = message.text.strip()
    if len(url) < 5:
        bot.reply_to(message, 'url пустой', reply_markup=keyboard_main)
        return
    if url.__contains__("playlist"):
        logger.debug("Downloading playlist...")
        bot.reply_to(message, 'Загрузка плейлиста начата...',
                     reply_markup=keyboard_main)
        download_playlist(url, message)
        logger.debug('Downloading playlist completed')
    else:
        logger.debug("Downloading video...")
        bot.reply_to(message, 'Загрузка видео начата...',
                     reply_markup=keyboard_main)
        download_video(url, message)
        logger.debug('Downloading video completed')

    bot.reply_to(message, 'Завершено', reply_markup=keyboard_main)


@bot.message_handler(commands=['старт', 'start'])
def start(message: telebot.types.Message) -> None:
    if str(message.chat.id) not in ALLOWED_IDS:
        bot.reply_to(
            message, f'Не достаточно полномочий! Ваш id:{message.chat.id}',
            reply_markup=keyboard_start)
        logger.debug(f'Unauthorized user {message.chat.id}')
    else:
        bot.send_message(
            message.chat.id, 'Бот работает', reply_markup=keyboard_main)


@bot.message_handler(commands=['скачать', 'download'])
def command_download(message: telebot.types.Message) -> None:
    if str(message.chat.id) not in ALLOWED_IDS:
        bot.reply_to(
            message, f'Не достаточно полномочий! Ваш id:{message.chat.id}',
            reply_markup=keyboard_start)
        logger.debug(f'Unauthorized user {message.chat.id}')
    else:
        msg = bot.reply_to(
            message, 'Введите URL видео или плейлиста',
            reply_markup=keyboard_main)
        bot.register_next_step_handler(msg, download_from_url)


bot.polling(none_stop=True)
