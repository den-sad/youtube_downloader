import telebot
import telebot.types

keyboard_main = telebot.types.ReplyKeyboardMarkup()
keyboard_main.row('/скачать', '/старт')
keyboard_main.resize_keyboard = True

keyboard_start = telebot.types.ReplyKeyboardMarkup()
keyboard_start.row('/cтарт')
keyboard_start.resize_keyboard = True
