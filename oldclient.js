
let AutocompleteClient = require("treebrowser").AutocompleteClient
let PrefixQuery = require("treebrowser").PrefixQuery
let BTreePrefixQuery = require("treebrowser").BTreePrefixQuery
let ping = require('ping')
const fs = require("fs")


async function main(){

  let maxamount = 25;

  // let parsedOSMnamesSeries = JSON.parse(fs.readFileSync("parsedstops.json"))
  // let parsedStreetQueries = JSON.parse(fs.readFileSync("parsedstreets.json"))

  let parsedOSMnamesSeries = JSON.parse(fs.readFileSync("parsedOSMnamesSeries.json"))
  // let parsedOSMnamesSeries = JSON.parse(fs.readFileSync("parsedOSMnamesSeriestest.json"))

  for (fragmentSize of [100, 500, 1000]){
    // for (let dataset of [ {name: "stops", shaclpath: "http://xmlns.com/foaf/0.1/name", queries: parsedStopsQueries} , {name: "streets", shaclpath: "http://www.w3.org/2000/01/rdf-schema#label", queries: parsedStreetQueries} ]){
    //   for (let datastructureManager of [{name:"perfix", query: PrefixQuery}, {name:"btree", query: BTreePrefixQuery} /*, {name:"hydra", query: queryEngine.PartialCollectionViewQuery} */]){
    for (let dataset of [ {name: "", shaclpath: "http://xmlns.com/foaf/0.1/name", queries: parsedOSMnamesSeries}  ]){
      for (let datastructureManager of [{name:"prefix", query: PrefixQuery}, {name:"btree", query: BTreePrefixQuery} /*, {name:"hydra", query: queryEngine.PartialCollectionViewQuery} */]){
           
        console.log("")
        console.log(dataset.name, datastructureManager.name, fragmentSize)
        console.log("")

        let usermap = new Map();
        let generalStats = {cch: 0, ccm: 0, sch: 0, scm: 0, bdw: 0, yesq: 0, noq: 0, ui: 0, ai: 0, ping: 0}
        let generaldatafile = "newclientresults/generaldata" + dataset["name"] + datastructureManager["name"] + "test" + fragmentSize + ".txt"
        fs.writeFileSync(generaldatafile, "")
      
        let queryUrl = "http://193.190.127.164/" + dataset["name"] + datastructureManager["name"] + "test/" + fragmentSize + "/node0.jsonld#Collection";
        let filename = "newclientresults/" + dataset["name"] + datastructureManager["name"] + "test" + fragmentSize + ".json"
        fs.writeFileSync(filename, "")
        for (let queryRequest of dataset.queries){
          let userid = queryRequest.userid

          if (! usermap.has(userid)){
            let client = new AutocompleteClient(maxamount, dataset.shaclpath)
            client.on("client-cache-miss", (obj) => { usermap.get(userid).ccm += 1; generalStats.ccm += 1}) 
            client.on("client-cache-hit", (obj) => { usermap.get(userid).cch += 1; generalStats.cch += 1 }) 
            client.on("server-cache-miss", (obj) => { usermap.get(userid).scm += 1; generalStats.scm += 1 }) 
            client.on("server-cache-hit", (obj) => { usermap.get(userid).sch += 1; generalStats.sch += 1 }) 
            client.on("downloaded", (obj) => { usermap.get(userid).bdw += obj.totalBytes; generalStats.bdw += obj.totalBytes }) 
            client.on("querystats", (obj) => {
              if (obj.fulfilled === true){ usermap.get(userid).yesq += 1; generalStats.yesq += 1;}
              else {usermap.get(userid).noq += 1; generalStats.noq += 1;}
              usermap.get(userid).ui += obj.useditems; generalStats.ui += obj.useditems;
              usermap.get(userid).ai += obj.allitems; generalStats.ai += obj.allitems;
            })
            let useropt = { cch: 0, ccm: 0, sch: 0, scm: 0, bdw: 0, yesq: 0, noq: 0, ui: 0, ai: 0, ping: [], newitemstiming: [], allitemstiming: [], requestsize: [], client: client }
            usermap.set(userid, useropt)
          }
         
          let userClient = usermap.get(userid).client
          let timingSeriesListNew = []
          let timingSeriesListAll = []
          usermap.get(userid).requestsize.push(queryRequest.requests.length)

          let reqping = await ping.promise.probe("193.190.127.164")
          usermap.get(userid).ping.push(reqping.time)
          generalStats.ping = reqping.time

          for (let searchvalue of queryRequest.requests){
            console.log(userid, searchvalue)
            // DIT IS EEN ENKELE QUERY VAN EEN SERIE

            let allitemstiming = []
            let newitemstiming = []
            let newlistnerFunction = function(data){
              if (data.searchvalue === searchvalue){
                var hrend = process.hrtime(hrstart)
                newitemstiming.push(hrend[1] / 1000000)
                allitemstiming.push(hrend[1] / 1000000)
              }
            }

            let alllistnerFunction = function(data){
              if (data.searchvalue === searchvalue){
                var hrend = process.hrtime(hrstart)
                allitemstiming.push(hrend[1] / 1000000)
              }
            }
            userClient.on("prevdata", alllistnerFunction)

            userClient.on("data", newlistnerFunction)

            var hrstart = process.hrtime()
            let timeoutPromise = new Promise(resolve => setTimeout(function() {
              userClient.interrupt()
              resolve()
            }, 150))
            await userClient.query(searchvalue, datastructureManager.query, dataset.shaclpath, queryUrl)
            await timeoutPromise
            userClient.removeListener("prevdata", alllistnerFunction)
            userClient.removeListener("data", newlistnerFunction)
            timingSeriesListNew.push(newitemstiming)
            timingSeriesListAll.push(allitemstiming)
            writeGeneralData(generaldatafile, generalStats)
          }
          await new Promise(resolve => setTimeout(resolve, 50));  // Wait 0.1 second to simulate a keypress
          usermap.get(userid).newitemstiming.push(timingSeriesListNew)
          usermap.get(userid).allitemstiming.push(timingSeriesListAll)
        }

        // Ending of a single run with the 3 stats
        writeData(filename, usermap)

      }
    }
  }
}

function writeData(filename, usermap){
  let valueArray = []
  for (let entry of usermap.entries()){
    let value = entry[1]
    value.userid = entry[0]
    delete value.client
    valueArray.push(value)
  }
  fs.appendFileSync(filename, JSON.stringify(valueArray, null, 2));
}

function writeGeneralData(filename, statsObj){
  fs.appendFileSync(filename, JSON.stringify(statsObj) + "\n");
}

main();