
let AutocompleteClient = require("treebrowser").AutocompleteClientParrallel
let PrefixQuery = require("treebrowser").PrefixQuery
let BTreePrefixQuery = require("treebrowser").BTreePrefixQuery
let ping = require('ping')
const fs = require("fs")

process.on('uncaughtException', function(err) {
  console.log('Caught exception: ' + err);
});

async function main(){

  let maxamount = 25;

  let parsedStreetQueries = JSON.parse(fs.readFileSync("parsedstreets.json"))

  let parsedOSMnamesSeries = JSON.parse(fs.readFileSync("parsedOSMnamesSeries.json"))

  let parsedStopsQueries = JSON.parse(fs.readFileSync("parsedstops.json"))
  let parsedRandomStopsQueries = JSON.parse(fs.readFileSync("parsedStopsSeries.json"))


  // let stopsdataset = {name: "stops", shaclpath: "http://xmlns.com/foaf/0.1/name", queries: parsedStopsQueries};
  // let streetsdataset = {name: "streets", shaclpath: "http://www.w3.org/2000/01/rdf-schema#label", queries: parsedStreetQueries};

  let stopsrandomdataset = {name: "stops", shaclpath: "http://xmlns.com/foaf/0.1/name", queries: parsedRandomStopsQueries, writename:"randomstops"};
  let stopsdataset = {name: "stops", shaclpath: "http://xmlns.com/foaf/0.1/name", queries: parsedStopsQueries, writename:"stops"};
  let osmnamesdataset = {name: "", shaclpath: "http://xmlns.com/foaf/0.1/name", queries: parsedOSMnamesSeries, writename:"realistic"};

  // for (let dataset of [stopsdataset, stopsrandomdataset, osmnamesdataset]){
  for (let dataset of [stopsrandomdataset/*, , osmnamesdataset*/]){
    for (fragmentSize of [ 25, 50, 75, 100 ]){
      for (let datastructureManager of [{name:"prefix", query: PrefixQuery}, {name:"btree", query: BTreePrefixQuery} ]){

        console.log("")
        console.log(dataset.name, datastructureManager.name, fragmentSize)
        console.log("")

        let usermap = new Map();
        let generalStats = {cch: 0, ccm: 0, sch: 0, scm: 0, bdw: 0, efficiency : {all: 0, used: 0}, ping: 0}
        let generaldatafile = "newclientresults/generaldata" + dataset["writename"] + datastructureManager["name"] + "test" + fragmentSize + ".txt"
        fs.writeFileSync(generaldatafile, "")
      
        let queryUrl = "http://193.190.127.164/" + dataset["name"] + datastructureManager["name"] + "test/" + fragmentSize + "/node0.jsonld#Collection";
        let filename = "newclientresults/" + dataset["writename"] + datastructureManager["name"] + "test" + fragmentSize + ".json"
        fs.writeFileSync(filename, "")
        let progressindex = 0;
        let querieslength = dataset.queries.length;
        for (let queryRequest of dataset.queries){
          progressindex += 1
          console.log("PROGRESS", (progressindex / querieslength))
          let userid = queryRequest.userid

          if (! usermap.has(userid)){
            let client = new AutocompleteClient(maxamount, dataset.shaclpath)
            client.on("client-cache-miss", (obj) => { usermap.get(userid).ccm += 1; seriesEntry.ccm += 1; generalStats.ccm += 1}) 
            client.on("client-cache-hit", (obj) => { usermap.get(userid).cch += 1; seriesEntry.cch += 1; generalStats.cch += 1 }) 
            client.on("server-cache-miss", (obj) => { usermap.get(userid).scm += 1; generalStats.scm += 1 }) 
            client.on("server-cache-hit", (obj) => { usermap.get(userid).sch += 1; generalStats.sch += 1 }) 
            client.on("efficiency", (obj) => { 
              usermap.get(userid).efficiency.push(obj) ; 
              generalStats.efficiency.all += obj.all; 
              generalStats.efficiency.used += obj.used; 
              seriesEntry.efficiency.push(obj)
            }) 
            client.on("downloaded", (obj) => { usermap.get(userid).bdw += obj.totalBytes; seriesEntry.bdw.push(obj.totalBytes); generalStats.bdw += obj.totalBytes }) 
            let useropt = { cch: 0, ccm: 0, sch: 0, scm: 0, bdw: 0, efficiency: [], ping: [], requestsize: [], client: client, queryseries: []}
            usermap.set(userid, useropt)
          }
        
          let userClient = usermap.get(userid).client

          let listnerFunction = function(data){
            var hrend = process.hrtime(hrstart)
            seriesEntry.timing.push(hrend[1] / 1000000)
          }


          try{
            var serieslist = []
            
            usermap.get(userid).requestsize.push(queryRequest.requests.length)

            let reqping = await ping.promise.probe("193.190.127.164")
            usermap.get(userid).ping.push(reqping.time)
            generalStats.ping = reqping.time

            for (let searchvalue of queryRequest.requests){
              console.log(userid, searchvalue)
              // DIT IS EEN ENKELE QUERY VAN EEN SERIE
              var seriesEntry = { timing: [], efficiency: [], cch: 0, ccm: 0, bdw: [] }

              userClient.on("data", listnerFunction)

              var hrstart = process.hrtime()

              let [query, querytask] = userClient.query(searchvalue, datastructureManager.query, dataset.shaclpath, queryUrl, 25)
              let timeoutPromise = new Promise(resolve => setTimeout(function() {
                query.interrupt()
                resolve()
              }, 150))
              await timeoutPromise
              console.log("data found", seriesEntry.timing.length)

              userClient.removeListener("data", listnerFunction)

              serieslist.push(seriesEntry)
              // console.log(seriesEntry)

              writeGeneralData(generaldatafile, generalStats)
            }
            // Stop previous queries from interfering with next set
            console.log("awaiting running queries")
            await userClient.await_running_queries()
            
            usermap.get(userid).queryseries.push(serieslist)
          } catch(e) {
            userClient.removeListener("data", listnerFunction)
            console.log("Error happened", dataset.name, datastructureManager.name, queryRequest, e)
            console.error("Error happened", dataset.name, datastructureManager.name, queryRequest)
          }
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