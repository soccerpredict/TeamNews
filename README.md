# Contents

- [Introduction](#introduction)
- [Data](#data)
- [Algorithms](#algorithms)

# Introduction
This repository contains the _SoccerNews2018_ dataset. It as database that contains statistics and news about the teams participating in the 2018 Brazillian Championship.

The content is separated into a set of JSON files and one SQL file.

# Data
The data was divided into four parts: teams, matches, statistics and news.
In the [data](https://github.com/soccerpredict/TeamNews/tree/master/data) directory are all data in JSON files.

The set o JSON files are structured exactly the same as the SQL. Thus, they follow a unique pattern for queries and use in any programming languages.

- [Teams](https://github.com/soccerpredict/TeamNews/blob/master/data/teams.json) is the main file. He contains the twenty championship teams and each has a identifier from one to twenty, plus the twenty one wich is the draw.
- [Matches](https://github.com/soccerpredict/TeamNews/tree/master/data/matches) is a set of files that contains all matches of the league. Each file contains a set of identifiers, the date, the game attendance and the income of the game.
- [Statistics](https://github.com/soccerpredict/TeamNews/tree/master/data/statistics) is a set of files that contains all basic statistics of the matches. Each match contains two statistics, one of the mandant team and other of the visitant team. Each file represents one statistic, so each match contains two statistic files.
- [News](https://github.com/soccerpredict/TeamNews/tree/master/data/news) is a set of files that contains news about all teams of the league. The news comes from all teams participating in the championship, from April to December 2018.
  
# Algorithms

All algorithms used for create this database are in directory [src](https://github.com/soccerpredict/TeamNews/tree/master/src).

- [crw_fbpred](https://github.com/soccerpredict/TeamNews/tree/master/src/crw_fbpred) is the news crawler. This directory contains the two entities that are responsible for extracting and storing the news about the teams.
  - For execute this crawler, use the command:
  ```
  scrapy crawl links
  or
  scrapy crawl news
  ```

- [GenLinks](https://github.com/soccerpredict/TeamNews/blob/master/src/gen_links.py) is the link generator for the statistics. This generator works by reading the tab_jogos_2018.csv file and generating the links of the [Veja](https://veja.abril.com.br/) portal.
  - For execute this file, use the command:
  ```
  python3 gen_links.py
  ```

- [GetStatistics](https://github.com/soccerpredict/TeamNews/blob/master/src/get_statistics.py) is the statistics crawler. This crawler works by reading a file of links and visiting all of them to extract the HTML element that has a class called _game_stats_.
  - For execute this crawler, use the command:
  ```
  python3 get_statistics.py
  ```

- [DB](https://github.com/soccerpredict/TeamNews/blob/master/src/db.py) is the database creator file. He is responsible for visiting the results of all crawlers, processing the data to a compatible format for SQL and storing the data in all tables.
  - For execute this file, use the command:
  ```
  python3 db.py
  ```
  
For any question, send a email to juliocmalvares07@gmail.com
