import tkinter as tk
from tkinter import scrolledtext
from threading import Thread
import json
import vlc
import time
import schedule
from datetime import datetime, timedelta


# Функция для воспроизведения видео
def play_video(video_path, duration, log_widget):
    player = vlc.MediaPlayer(video_path)
    player.play()
    log_widget.insert(tk.END, f"Воспроизведение: {video_path}\n")
    time.sleep(duration)  # Время воспроизведения видео
    player.stop()


# Функция запуска расписания
def run_schedule(log_widget):
    while True:
        schedule.run_pending()
        time.sleep(1)


# Функция для запуска воспроизведения видео по расписанию
def schedule_playback(data, log_widget):
    start_time_str = data['screen']['start_time']
    start_time = datetime.strptime(start_time_str, '%H:%M:%S').time()

    def playback():
        current_time = datetime.now().time()
        if start_time <= current_time:
            for schedule_item in sorted(data['schedule'], key=lambda x: x['queue_number']):
                media_content_id = schedule_item['media_content']
                media_item = next((item for item in data['media_content'] if item['id'] == media_content_id), None)
                if media_item:
                    video_path = media_item['video']
                    duration = int(timedelta(hours=int(media_item['duration'].split(':')[0]),
                                             minutes=int(media_item['duration'].split(':')[1]),
                                             seconds=int(media_item['duration'].split(':')[2])).total_seconds())
                    play_video(video_path, duration, log_widget)
            log_widget.insert(tk.END, "Воспроизведение завершено\n")

    # Запланировать задачу на запуск
    schedule.every().day.at(start_time_str).do(playback)


# Чтение и анализ JSON-файла
with open('media/videomanager_data.json', 'r') as file:
    data = json.load(file)


# Создание интерфейса
def create_app():
    root = tk.Tk()
    root.title("Видео Агент")

    # Текстовое поле для логов
    log_widget = scrolledtext.ScrolledText(root, width=70, height=10)
    log_widget.pack(pady=10)

    # Планирование воспроизведения
    schedule_playback(data, log_widget)

    # Запуск планировщика в отдельном потоке
    Thread(target=run_schedule, args=(log_widget,), daemon=True).start()

    root.mainloop()


create_app()
