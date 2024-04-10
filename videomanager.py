import json
import time
import logging
import vlc
from datetime import datetime, timedelta

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def read_json_schedule(file_path):
    try:
        with open(file_path, 'r') as file:
            data = json.load(file)
        logging.info("JSON data successfully loaded.")
        return data
    except Exception as e:
        logging.error(f"Error reading JSON file: {e}")
        return None

def play_video(video_path, player):
    logging.info(f"Attempting to play video: {video_path}")
    media = player.set_media(vlc.Media(video_path))
    player.play()
    time.sleep(1)  # Даем время на запуск видео
    while player.is_playing():
        time.sleep(1)  # Active wait until video is finished
    logging.info(f"Video finished: {video_path}")

def get_video_schedule(schedule, media_content):
    video_schedule = []
    for item in sorted(schedule, key=lambda x: x['queue_number']):
        content = next((c for c in media_content if c['id'] == item['media_content']), None)
        if content:
            video_schedule.append(content['video'])
    return video_schedule

def wait_until_start_time(start_time_str):
    start_time = datetime.strptime(start_time_str, '%H:%M:%S').time()
    now = datetime.now()
    start_datetime = datetime.combine(now.date(), start_time)
    if start_datetime < now:
        start_datetime += timedelta(days=1)
    wait_seconds = (start_datetime - now).total_seconds()
    if wait_seconds > 0:
        logging.info(f"Waiting until {start_datetime} to start playback ({wait_seconds} seconds)")
        time.sleep(wait_seconds)

def check_end_time(end_time_str):
    end_time = datetime.strptime(end_time_str, '%H:%M:%S').time()
    now = datetime.now().time()
    return now < end_time

def main():
    schedule_data = read_json_schedule('media/videomanager_data.json')
    if schedule_data:
        screen_info = schedule_data['screen']
        start_time_str = screen_info['start_time']
        end_time_str = screen_info['end_time']

        wait_until_start_time(start_time_str)

        video_schedule = get_video_schedule(schedule_data['schedule'], schedule_data['media_content'])
        if video_schedule:
            instance = vlc.Instance()
            player = instance.media_player_new()

            while check_end_time(end_time_str):
                for video_path in video_schedule:
                    if not check_end_time(end_time_str):
                        logging.info("Reached the end time of the broadcast. Stopping playback.")
                        break
                    play_video(video_path, player)
                    time.sleep(1)  # Пауза 1 секунду между видео
        else:
            logging.info("No videos to play.")
    else:
        logging.error("Failed to load schedule data.")

if __name__ == "__main__":
    main()