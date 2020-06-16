from selenium import webdriver
import time
import csv

def crawl():
    driver = webdriver.Chrome(executable_path=r'C:\Users\miche\Downloads\chromedriver.exe')
    with open("task1_questions.txt", "r") as f_in:
        for line in f_in:
            question = line.strip()
            driver.get('https://evidenceminer.com/')
            search_bar = driver.find_element_by_class_name("prompt")
            search_bar.send_keys(question)
            # send enter key
            search_bar.send_keys(u'\ue007')
            time.sleep(2)
            excldude_button = driver.find_element_by_class_name("ui.checkbox")
            excldude_button.click()
            time.sleep(4)
            titles = driver.find_elements_by_class_name("small-title")
            i = 0
            with open("task1_results_evidenceminer_titles.txt", "a") as f_out:
                for title in titles:
                    if title.text == "Title: No Title" or title.text == "":
                        continue
                    if i == 5:
                        break
                    f_out.write(title.text[7:] + "\n")
                    i += 1
                f_out.write("\n")
    driver.quit()

def title_to_id():
    with open("task1_results_evidenceminer_titles.txt", "r") as f_titles:
        titles = {title.strip() : "none" for title in f_titles}
    with open(r'C:\Users\miche\Documents\summer research 2020\cord-19_2020-05-12\2020-05-12\metadata.csv', "r", encoding="utf-8") as f_meta:
        metadata = csv.DictReader(f_meta)
        for row in metadata:
          title = row.get("title")
          if title in titles:
              titles[title] = row.get("cord_uid")  
    with open("task1_results_evidenceminer.txt", "w") as f_out:
        i = 1
        for key, value in titles.items():
            print(key)
            if i % 6 == 0:
                f_out.write("\n")
            else:
                f_out.write(value + "\n")
            i += 1      

def main():
    crawl()
    title_to_id()

main()