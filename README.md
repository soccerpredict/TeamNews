# Contents

- [Introduction](#introduction)
- [Data](#data)
- [Algorithms](#algorithms)

# Introduction
This repository contains the _SoccerNews2018_ dataset. It as database that contains statistics and news about the teams participating in the 2018 Brazillian Championship.

The content is separated into a set of JSON files.

# Data
The data was divided into four parts: teams, matches, statistics and news.
In the [data](https://github.com/soccerpredict/TeamNews/tree/master/data) directory are all data in JSON files.

The set o JSON files are structured exactly the same as the SQL. Thus, they follow a unique pattern for queries and use in any programming languages.

- [Teams](https://github.com/soccerpredict/TeamNews/blob/master/data/teams.json) is the main file. He contains the twenty championship teams and each has a identifier from one to twenty, plus the twenty one wich is the draw.
- [Matches](https://github.com/soccerpredict/TeamNews/tree/master/data/matches) is a set of files that contains all matches of the league. Each match contains a set of identifiers, the date, the game attendance and the income of the game.
- [Statistics](https://github.com/soccerpredict/TeamNews/tree/master/data/statistics) is a set of files that contains all basic statistics of the matches. Each match contains two statistics, one of the mandant team and other of the visitant team. Each group represents one statistic, so each match contains two statistic groups.
- [News](https://github.com/soccerpredict/TeamNews/tree/master/data/news) is a set of files that contains news about all teams of the league. The news comes from all teams participating in the championship, from April to December 2018.
  
# Algorithms

The _NewsCrawler_ algorithms used for create this database are in directory [NewsCrawler](https://github.com/soccerpredict/TeamNews/tree/master/NewsCrawler).
The _Statistics_Crawler_ algorithms used for create this database are in directory [crawler_statistics](https://github.com/soccerpredict/TeamNews/tree/master/crawler_statistics).

- [NewsCrawler](https://github.com/soccerpredict/TeamNews/blob/master/NewsCrawler/NewsCrawler.py) is the news crawler. This directory contains the entities that are responsible for extracting and storing the news about the teams.
  - For execute this crawler, use the command:
  ```
  python3 NewsCrawler.py
  ```
- [GetStatistics](https://github.com/soccerpredict/TeamNews/tree/master/crawler_statistics) is the statistics crawler. This crawler works by reading a file of links and visiting all of them to extract the HTML element that has a class called _game_stats_.
  - For execute this crawler, use the command:
  ```
  python3 get_statistics.py
  ```


For any question, send a email to juliocmalvares07@gmail.com
