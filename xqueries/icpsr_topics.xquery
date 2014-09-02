for $n in distinct-values(collection('/db/edc_ddi')//topcClas[@vocab='ICPSR subject classifications'])
order by $n ascending
return concat($n, "; ", 
    count(collection("/db/edc_ddi")/codeBook[ft:query(.//topcClas, <query><phrase>{$n}</phrase></query>)]),
   "; ",
  count(collection("/db/edc_ddi")/codeBook[ft:query(.//topcClas, <query><phrase>{$n}</phrase></query>)][.//geogCover="Global"])
)