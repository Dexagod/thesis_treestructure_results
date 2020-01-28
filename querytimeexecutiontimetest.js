let fetcher = require("ldfetch")
let fs = require('fs')
var path = path || require('path');
let ping = require('ping')

var TESTSETSIZE = 100;
var LABELPREDICATE = "http://www.w3.org/2000/01/rdf-schema#label"

async function main(){


  let test = 1;

  for (let fragmentation of ["btree"]){
    for (let fragmentSize of [ 50, 200 /*25, 50, 75, 100, 200, 500, 1000*/]){
      let directory = "/home/dexa/Ugent/thesis/addressparser/data/"+fragmentation+"test/"

      console.log(fragmentation, fragmentSize)

      let coldfilename = "timetests/coldtimetest" + fragmentation + fragmentSize + ".txt"

      let warmfilename = "timetests/warmtimetest" + fragmentation + fragmentSize + ".txt"
      
      // clearing file
      fs.writeFileSync(coldfilename, "")
      fs.writeFileSync(warmfilename, "")

      // initialize fetcher
      let ldfetch = new fetcher({})
      let warmingldfetch = new fetcher({})

      // load local files to select 50 random files.
      let fragmentSizeDirectory = directory+fragmentSize+"/"
      let files =  walkSync(fragmentSizeDirectory, null, "")
      // fs.readdirSync(fragmentSizeDirectory).forEach(file => { files.push(file);  });

      // shuffle these files
      files = shuffle(files)

      console.log("FILES", files)


      // FILLING CACHE
      console.log("WARMING CACHE")
      for (let i = 0; i < TESTSETSIZE; i++){
        let file = files[i]
        let URL = "http://193.190.127.164/"+fragmentation + "test/"+fragmentSize+"/"+file
    
        ping.promise.probe("193.190.127.164")
          .then(function (res) {
            fs.appendFileSync(coldfilename, "ping: " + res.time + "\n")
          });

        var hrstart = process.hrtime()
        console.log(URL)
        let data = await ldfetch.get(URL)
        fs.appendFileSync(coldfilename, "jsonldprocessing: " + data.jsonldprocessingtime + "\n");
        fs.appendFileSync(coldfilename, "totalprocessingtime: " + data.totalprocessingtime + "\n");
        let onlyprocessingtime = data.totalprocessingtime - data.jsonldprocessingtime 
        fs.appendFileSync(coldfilename, "onlyprocessingtime: " + onlyprocessingtime + "\n");
        var hrend = process.hrtime(hrstart)
        let totalTime = hrend[1] / 1000000
        fs.appendFileSync(coldfilename, "totalrequest: " + totalTime + "\n");

        //process data 
        var hrstartdataprocess = process.hrtime()
        let labelTriples = processData(data)
        var hrenddataprocess = process.hrtime(hrstartdataprocess)
        let totalTimedataprocess = hrenddataprocess[1] / 1000000
        fs.appendFileSync(coldfilename, "processing: " + totalTimedataprocess + "\n");
      }

      console.log("DONE WARMING CACHE")
      await new Promise(resolve => setTimeout(resolve, 1000));
      // request first 50 files of the shuffeled list from remote server.abs
      // Measure ping, fetch time and parse time.  
      for (let i = 0; i < TESTSETSIZE; i++){
        let file = files[i]
        let URL = "http://193.190.127.164/"+fragmentation + "test/"+fragmentSize+"/"+file
    
        ping.promise.probe("193.190.127.164")
          .then(function (res) {
            fs.appendFileSync(warmfilename, "ping: " + res.time + "\n")
          });

        var hrstart = process.hrtime()
        console.log(URL)
        let data = await warmingldfetch.get(URL)
        fs.appendFileSync(warmfilename, "jsonldprocessing: " + data.jsonldprocessingtime + "\n");
        fs.appendFileSync(warmfilename, "totalprocessingtime: " + data.totalprocessingtime + "\n");
        let onlyprocessingtime = data.totalprocessingtime - data.jsonldprocessingtime 
        fs.appendFileSync(warmfilename, "onlyprocessingtime: " + onlyprocessingtime + "\n");
        var hrend = process.hrtime(hrstart)
        let totalTime = hrend[1] / 1000000
        fs.appendFileSync(warmfilename, "totalrequest: " + totalTime + "\n");

        //process data 
        var hrstartdataprocess = process.hrtime()
        let labelTriples = processData(data)
        var hrenddataprocess = process.hrtime(hrstartdataprocess)
        let totalTimedataprocess = hrenddataprocess[1] / 1000000
        fs.appendFileSync(warmfilename, "processing: " + totalTimedataprocess + "\n");
      }
    } 
  }
}


function processData(data){
  let labelTriples = []
  for (let triple of data.triples){
    if (triple.predicate.value === LABELPREDICATE){
      labelTriples.push(triple)
    }
  }
  return labelTriples
}


function shuffle(array) {
  var currentIndex = array.length, temporaryValue, randomIndex;

  // While there remain elements to shuffle...
  while (0 !== currentIndex) {

    // Pick a remaining element...
    randomIndex = Math.floor(Math.random() * currentIndex);
    currentIndex -= 1;

    // And swap it with the current element.
    temporaryValue = array[currentIndex];
    array[currentIndex] = array[randomIndex];
    array[randomIndex] = temporaryValue;
  }

  return array;
}


var walkSync = function(dir, filelist, relativedir) {
  relativedir = relativedir || "";
  files = fs.readdirSync(dir);
  filelist = filelist || [];
  files.forEach(function(file) {
    if (fs.statSync(path.join(dir, file)).isDirectory()) {
      filelist = walkSync(path.join(dir, file), filelist, path.join(relativedir, file));
    }
    else {
      filelist.push(path.join(relativedir, file));
    }
  });
  return filelist;
};


main()