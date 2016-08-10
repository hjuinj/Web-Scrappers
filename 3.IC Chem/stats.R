library(rmongodb)
library(stringr)
library(ggplot2)

mongo <- mongo.create()
if(mongo.is.connected(mongo) == TRUE) {
    db <- mongo.get.databases(mongo)
    coll <- mongo.get.database.collections(mongo, db)
}


mongo.count(mongo, coll)

type <- mongo.distinct(mongo, coll, 'publication-type')
person <- mongo.distinct(mongo, coll, "from")
mongo.distinct(mongo, coll, "title")

mongo.distinct(mongo, coll, "journal", fields = list('publication-type' = 1))

mongo.find.one(mongo, coll)
df <- mongo.find.all(mongo, coll, fields = list(from = 1, title = 1, 'publication-type' = 1, '_id' = 0))

ggplot(df, aes(x = df$)) + geom_bar()


