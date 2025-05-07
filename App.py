import time
import re
import yt_dlp
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup
import os

# ------------------------------------
# Configuration
# ------------------------------------
LOGIN_URL = "https://dd.lk/public/guest/login.php"
LESSON_BASE_URL = "https://dd.lk/public/student/lesson-singleview.php?lid="
DOWNLOAD_FOLDER = "downloads"  # Folder where videos will be saved

# Create the download folder if it doesn't exist
if not os.path.exists(DOWNLOAD_FOLDER):
    os.makedirs(DOWNLOAD_FOLDER)

# ------------------------------------
# Setup ChromeDriver
# ------------------------------------
options = Options()
# Uncomment below for headless mode
# options.add_argument('--headless')
options.add_argument('--disable-gpu')
options.add_argument('--no-sandbox')
options.add_argument('--disable-dev-shm-usage')

driver = webdriver.Chrome(options=options)
driver.get(LOGIN_URL)

def download_video(youtube_url):
    try:
        print(f"   ⬇️ Downloading video from: {youtube_url}")
        ydl_opts = {
            'outtmpl': os.path.join(DOWNLOAD_FOLDER, '%(title)s.%(ext)s'),
            'format': 'bestvideo+bestaudio/best',
            'noplaylist': True,
            'quiet': False,  # Set to True to suppress output
            'postprocessors': [{
                'key': 'FFmpegVideoConvertor',
                'preferedformat': 'mp4',  # Download video as mp4
            }],
        }
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([youtube_url])
            print("   ✅ Download complete!")
    except Exception as e:
        print(f"   ❌ Error downloading video: {e}")

def print_lessons_and_check_youtube(lesson_html):
    soup = BeautifulSoup(lesson_html, 'html.parser')
    lessons = soup.find_all('div', class_='lesson')

    for i, lesson in enumerate(lessons, start=1):
        title = lesson.get_text(strip=True)
        onclick = lesson.get('onclick', '')
        match = re.search(r"lid=(\d+)", onclick)
        if not match:
            continue

        lid = match.group(1)
        lesson_url = f"{LESSON_BASE_URL}{lid}"
        print(f"\n{i:02d}. {title} → {lesson_url}")

        # Visit the lesson page
        try:
            driver.get(lesson_url)
            time.sleep(3)
            lesson_page = BeautifulSoup(driver.page_source, 'html.parser')

            # Look for YouTube iframe
            iframe_tags = lesson_page.find_all('iframe')
            youtube_iframes = [
                iframe['src'] for iframe in iframe_tags
                if 'youtube.com' in iframe.get('src', '')
            ]

            if youtube_iframes:
                youtube_url = youtube_iframes[0]
                print(f"   ▶️ YouTube video found: {youtube_url}")
                # Start downloading the video
                download_video(youtube_url)
                # Wait for download to complete before continuing
                while not any(f.endswith('.mp4') for f in os.listdir(DOWNLOAD_FOLDER)):
                    print("   ⏳ Waiting for download to complete...")
                    time.sleep(2)
            else:
                print("   ⛔ No YouTube video found.")

        except Exception as e:
            print(f"   ❌ Error visiting lesson: {e}")

def get_lesson_container_html():
    soup = BeautifulSoup(driver.page_source, 'html.parser')
    lesson_div = soup.find('div', class_='lesson-container')
    return str(lesson_div) if lesson_div else None

# ------------------------------------
# Monitor for changes
# ------------------------------------
prev_content = get_lesson_container_html()
print("👀 Watching '.lesson-container' for changes... (Ctrl+C to stop)")

try:
    while True:
        time.sleep(5)
        current_content = get_lesson_container_html()

        if current_content != prev_content:
            print("\n🔄 '.lesson-container' content changed!")
            print_lessons_and_check_youtube(current_content)
            prev_content = current_content
        else:
            print("... no change.")

except KeyboardInterrupt:
    print("🛑 Stopped watching.")

finally:
    driver.quit()
