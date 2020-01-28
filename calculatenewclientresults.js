const fs = require("fs")
let parsedStopsQueries = JSON.parse(fs.readFileSync("parsedstopstest.json"))
let parsedStreetQueries = JSON.parse(fs.readFileSync("parsedstreetstest.json"))

for (fragmentSize of [100, 500, 1000]){
  for (let dataset of [ /* {name: "stops", shaclpath: "http://xmlns.com/foaf/0.1/name", queries: parsedStopsQueries} , */ {name: "streets", shaclpath: "http://www.w3.org/2000/01/rdf-schema#label", queries: parsedStreetQueries} ]){
    for (let datastructureManager of [ {name:"perfix"}, {name:"btree"} /*, {name:"hydra", query: queryEngine.PartialCollectionViewQuery} */]){
      console.log("")
      console.log(dataset.name, datastructureManager.name, fragmentSize)
      console.log("")

      let filename = "newclientresults/" + dataset["name"] + datastructureManager["name"] + "test" + fragmentSize + ".json"
      let userStatsArray = JSON.parse(fs.readFileSync(filename))
      // console.log(userStatsArray[0])

      let lt10 = {
        name: "lt10", averageping : 0, averagecch : 0, averageccm : 0, averagesch : 0, averagescm : 0, averagebdw : 0, averageai : 0, averageui : 0, averagebdwperreqest : 0, totalusers: 0, efficiency: 0
      }

      let gt10 = {
        name: "gt10", averageping : 0, averagecch : 0, averageccm : 0, averagesch : 0, averagescm : 0, averagebdw : 0, averageai : 0, averageui : 0, averagebdwperreqest : 0, totalusers: 0, efficiency: 0
      }

      let gt30 = {
        name: "gt30", averageping : 0, averagecch : 0, averageccm : 0, averagesch : 0, averagescm : 0, averagebdw : 0, averageai : 0, averageui : 0, averagebdwperreqest : 0, totalusers: 0, efficiency: 0
      }

      let gt50 = {
        name: "gt50", averageping : 0, averagecch : 0, averageccm : 0, averagesch : 0, averagescm : 0, averagebdw : 0, averageai : 0, averageui : 0, averagebdwperreqest : 0, totalusers: 0, efficiency: 0
      }

      for (let element of userStatsArray){
        let sumOfItems = element.requestsize.reduce((a, b) => a+b, 0)
        let ug = lt10;
        if (sumOfItems > 10){
          ug = gt10;
        } if (sumOfItems > 30){
          ug = gt30;
        } if (sumOfItems > 50){
          ug = gt50;
        }
        ug.averagecch += element.cch;
        ug.averageccm += element.ccm;
        ug.averagesch += element.sch;
        ug.averagescm += element.scm;
        ug.averagebdw += element.bdw
        ug.averageai += element.ai
        ug.averageui += element.ui
        ug.averageping += element.ping.reduce((a, b) => a+b, 0) / element.ping.length
        ug.averagebdwperreqest += element.bdw / sumOfItems
        ug.totalusers += 1;
      }

      for (let ug of [lt10, gt10, gt30, gt50]){
        ug.averageping = (ug.averageping / ug.totalusers).toFixed(2)
        ug.averagecch = (ug.averagecch / ug.totalusers).toFixed(2)
        ug.averageccm = (ug.averageccm / ug.totalusers).toFixed(2)
        ug.averagesch = (ug.averagesch / ug.totalusers).toFixed(2)
        ug.averagescm = (ug.averagescm / ug.totalusers).toFixed(2)
        ug.averagebdw = (ug.averagebdw / ug.totalusers).toFixed(2)
        ug.averageai = (ug.averageai / ug.totalusers).toFixed(2)
        ug.averageui = (ug.averageui / ug.totalusers).toFixed(2)
        ug.averagebdwperreqest = (ug.averagebdwperreqest / ug.totalusers).toFixed(2)
        ug.efficiency = (ug.averageui / ug.averageai).toFixed(2)
      }

      for (let ug of [lt10, gt10, gt30, gt50]){
        console.log(ug.name, "cch:", ug.averagecch, "ccm:",  ug.averageccm, "sch:", ug.averagesch, "scm:", ug.averagescm, "abdw:", ug.averagebdw, "abdwpr:", ug.averagebdwperreqest, "aai:", ug.averageai, "aui:", ug.averageui, "aeff:", ug.efficiency, "aping:", ug.averageping)
      }
      
    }
  }
}