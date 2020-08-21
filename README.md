# CORD-19 Alberta Search Engine
In response to the COVID-19 pandemic, the Allen Institute for AI has developed the [COVID-19 Open Research Dataset (CORD-19)](https://www.semanticscholar.org/cord19/download), a corpus of COVID-19 related scientific publications. We present the CORD-19 Alberta Search Engine (CASE), a search engine that allows users to search the CORD-19 corpus using natural language queries. CASE expands upon the BM25+ ranking function by incorporating the proximity and synonyms of query terms into our ranking. For more information on our system [click here](https://docs.google.com/document/d/1sQ-h6G24PVaV3sALfM2Df6t1keHQWwjwvkdRJW7vqRY/edit?usp=sharing).

## Usage
To use CASE, clone this repository. CASE uses a SQLite database, which you can download [here](https://drive.google.com/file/d/1PnjXTHNs91qNYojLiB499WBnm9-GBXtv/view?usp=sharing). This database contains the June 19th version of CORD-19. Navigate to the "system" directory and place the database there. To start the program, enter the following in the command line:
```
python query_tool.py [path to database]
```
Replace ```[path to database]``` with the path to the database. If you downloaded our SQLite database and placed it in the system directory, you would enter:
```
python query_tool.py cord19-2020-06-19.db
```
The system will take a few seconds to load, then you will see a greeting as follows:
```
Loading...
Welcome to the CORD-19 Alberta Search Engine.
There are currently 73861 documents in the database.

Enter "quit" to exit the application.
Enter a query: 
```
And now you are free to search the CORD-19 corpus! Our system returns the top 25 documents that match your query, displaying the title and first few sentences of each document along with a link where you can access the full text. Here is an example of a search:
```
Enter a query: coronavirus remdesivir
Top 25 documents retrieved in 0.54 seconds
Remdesivir in treatment of COVID-19: A systematic benefit-risk assessment
        Background: There is a need to identify effective, safe treatments for
        COVID-19 (coronavirus disease) rapidly, given the current, ongoing
        pandemic. A systematic benefit-risk assessment was designed and
        conducted to strengthen the ongoing understanding of the benefit-risk
        balance for remdesivir in COVID-19 treatment by using a structured
        method which uses all available data. Methods: The Benefit-Risk Action
        Team (BRAT) framework was used to assess the overall benefit-risk of
        the use of remdesivir as a treatment for COVID-19 compared to standard
        of care, placebo or other treatments. We searched PubMed,Google
        Scholar and government agency websites to identify literature
        reporting clinical outcomes in patients taking remdesivir for
        COVID-19. A value tree was constructed and key benefits and risks were
        ranked by two clinicians in order of considered importance...
Link: http://medrxiv.org/cgi/content/short/2020.05.07.20093898v1?rss=1
Press enter to view next document or type "return" to enter another query

```

# Credits
The CORD-19 Alberta Search Engine is developed at the University of Alberta by Michelle Aubin (phiangda@ualberta.ca) under the supervision of Davood Rafiei (drafiei@ualberta.ca)
