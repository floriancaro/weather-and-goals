# load packages
library(tidyverse)
library(readxl)
library(stringr)

# set PROJHOME
# PROJHOME <- "C:/Users/Florian Caro/LRZ Sync+Share/MOOCs/2021/Applied Data Science with Python Specialization/Applied Plotting, Charting & Data Representation in Python/Week 4/"
PROJHOME <- "/Users/fcaro/LRZ Sync+Share/MOOCs/2021/Applied Data Science with Python Specialization/Applied Plotting, Charting & Data Representation in Python/Week 4/" # MAC

# load data on matches
for(saison in c("20_21", "19_20", "18_19", "17_18", "16_17")) {
  matches <- read_excel(paste0(PROJHOME, "bundesliga_", saison, ".xlsx"), sheet = 1)
  matches <- matches[, c(1:3,5:6)]
  
  # rename columns
  colnames(matches) <- c("date", "time", "home", "away", "score")
  
  # drop rows with NAs indicating new matchdays
  matches <- matches[!is.na(matches$time), ]
  
  # extract time
  matches$time <- str_sub(as.character(matches$time), 12, 19)
  
  # propagate match date forward
  current_date <- matches$date[0]
  for(row in 1:nrow(matches)) {
    
    if(is.na(matches$date[row])) {
      matches$date[row] <- current_date
    } else {
      current_date <- matches$date[row]
    }
    
  }
  rm(row, current_date)
  
  # split score into half-time and final score
  matches$halftime_score <- str_extract_all(matches$score, pattern = "\\(.*\\)")
  matches$halftime_score <- str_remove_all(matches$halftime_score, pattern = "[()]")
  matches$score <- str_remove_all(matches$score, pattern = "\\(.*\\)")
  
  # get home and away goals
  matches$home_score <- as.numeric(str_remove_all(str_extract_all(matches$score, pattern = "[0-9]+[:]"), pattern = "[:]"))
  matches$away_score <- as.numeric(str_remove_all(str_extract_all(matches$score, pattern = "[:]+[0-9]"), pattern = "[:]"))
  
  # create alternative date format fitting weather data
  matches$date_alt <- ""
  for(row in 1:nrow(matches)) {
    matches$date_alt[row] <- paste0(str_split(matches$date[row], pattern = "[.]")[[1]][3], str_split(matches$date[row], pattern = "[.]")[[1]][2], str_split(matches$date[row], pattern = "[.]")[[1]][1])
  }
  rm(row)
  
  # export processed data
  write.csv(matches, file = paste0(PROJHOME, "matches_cleaned_", saison, ".csv"))
}
  