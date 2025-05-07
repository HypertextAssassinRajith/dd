import time
from selenium import webdriver
from bs4 import BeautifulSoup

# Set the target URL
url = "https://dd.lk/public/guest/login.php"

# Launch browser
driver = webdriver.Chrome()  # Use appropriate driver if not using Chrome
driver.get(url)

def print_lessons(lesson_html):
    soup = BeautifulSoup(lesson_html, 'html.parser')
    lessons = soup.find_all('div', class_='lesson')
    for i, lesson in enumerate(lessons, start=1):
        title = lesson.get_text(strip=True)
        link = lesson.get('onclick')
        if link:
            link = link.split('=')[1].strip("';")
            print(f"{i:02d}. {title} → lesson-singleview.php?{link}")


def get_lesson_container_html():
    soup = BeautifulSoup(driver.page_source, 'html.parser')
    lesson_div = soup.find('div', class_='lesson-container')
    return str(lesson_div) if lesson_div else None

# Get initial lesson container HTML
prev_content = get_lesson_container_html()

print("Watching '.lesson-container' for changes... (Ctrl+C to stop)")

try:
    while True:
        time.sleep(5)
        current_content = get_lesson_container_html()

        if current_content != prev_content:
            print("🔄 '.lesson-container' content changed!")
            print_lessons(current_content)

            prev_content = current_content
        else:
            print("No change in '.lesson-container'.")

except KeyboardInterrupt:
    print("Stopped watching.")

finally:
    driver.quit()
