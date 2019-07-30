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
- [News](https://github.com/soccerpredict/TeamNews/tree/master/data/news) is a set of files that contains news about all teams of the league.
  
# Algorithms
