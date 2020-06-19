from selenium import webdriver
import time
import csv

def crawl():
    driver = webdriver.Chrome(executable_path=r'C:\Users\miche\Downloads\chromedriver.exe')
    with open("task1_questions.txt", "r") as f_in:
        questions = {line.strip() : {} for line in f_in}
    for question in questions:
        driver.get('https://evidenceminer.com/')
        search_bar = driver.find_element_by_class_name("prompt")
        search_bar.send_keys(question)
        # send enter key
        search_bar.send_keys(u'\ue007')
        time.sleep(0.7)
        exclude_button = driver.find_element_by_class_name("ui.checkbox")
        exclude_button.click()
        time.sleep(0.7)
        titles = driver.find_elements_by_class_name("small-title")
        for title in titles:
            if title.text == "Title: No Title" or len(title.text) < 6:
                continue
            questions[question][title.text[7:]] = "none"
            if len(questions[question]) == 5:
                break
    driver.quit()
    return questions

def title_to_id(questions):
    with open(r'C:\Users\miche\Documents\summer research 2020\cord-19_2020-05-12\2020-05-12\metadata.csv', "r", encoding="utf-8") as f_meta:
        metadata = csv.DictReader(f_meta)
        for row in metadata:
          title = row.get("title")
          for question, titles in questions.items():
              if title in titles:
                titles[title] = row.get("cord_uid")  
    with open("task1_results_evidenceminer.txt", "w") as f_out:
        for question, titles in questions.items():
            for title, cord_uid in titles.items():
                f_out.write(cord_uid + "\n")
            f_out.write("\n")

def main():
    questions = crawl()
    title_to_id(questions)

main()