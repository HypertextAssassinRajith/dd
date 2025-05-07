import time
from selenium import webdriver
from bs4 import BeautifulSoup

# Set the target URL
url = "https://dd.lk/public/guest/login.php"
lesson_base_url = "https://dd.lk/public/student/lesson-singleview.php?lid="

# Launch browser
driver = webdriver.Chrome()  # You can replace this with the appropriate driver
driver.get(url)

def print_lessons(lesson_html):
    soup = BeautifulSoup(lesson_html, 'html.parser')
    lessons = soup.find_all('div', class_='lesson')
    for i, lesson in enumerate(lessons, start=1):
        title = lesson.get_text(strip=True)
        onclick = lesson.get('onclick')
        if onclick:
            match = onclick.split("lid=")
            if len(match) > 1:
                lid = match[1].strip("';")
                full_url = f"{lesson_base_url}{lid}"
                print(f"{i:02d}. {title} → {full_url}")

def get_lesson_container_html():
    soup = BeautifulSoup(driver.page_source, 'html.parser')
    lesson_div = soup.find('div', class_='lesson-container')
    return str(lesson_div) if lesson_div else None


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
