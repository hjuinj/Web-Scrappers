"""
//TODOs:
1: Dealing with more than 1 page in the headlines
2: Formatting output using HTML

"""
library(stringr)
library(XML)
library(RCurl)

url <- "http://cctv.cntv.cn/lm/xinwenlianbo/"
url <- str_c(url, format(Sys.Date(), "%Y%m%d"), ".shtml")

info <- debugGatherer()
handle <- getCurlHandle(cookiejar
                        = "",
                        followlocation = TRUE, autoreferer = TRUE, debugfunc
                        = info$update,
                        verbose
                        = TRUE,
                        httpheader = list( from
                                           = "sw4512@ic.ac.uk",
                                           'user-agent' = str_c(R.version$version.string, ", ", R.version$platform)
                  ))

main <- getURL(url, curl = handle, .encoding = "UTF-8")
main <- htmlParse(main)
headlines <- xpathSApply(doc =main, path = "//div[@class='title_list_box_130503']/ul")

links <- c()
for(i in 1: length(headlines)){
      temp <- xpathSApply(headlines[[i]], "li/a")
      if(length(temp) == 0) break
      links <- c(links, sapply(1:length(temp), function(j){
            if(str_detect(as.character(xmlValue(temp[[j]])), "\\[视频\\]"))
                  xmlAttrs(temp[[j]])["href"]
      }))
}


text <- sapply(links, function(i){
      print(i)
      temp <- getURL(i, curl = handle, .encoding = "UTF-8")
      temp <- htmlParse(temp)
      xpathSApply(temp, path = "//div[@id='content_body']", fun = xmlValue)
})

for(i in text)
      cat(i)
