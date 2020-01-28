let fs = require("fs")

let file = "./osmnamesshuffeled.txt"

let randomnames = fs.readFileSync(file).toString().split("\n").slice(0, 1000)
let outputfile = "parsedOSMnamesSeries.json"

let objectList = []

for (let name of randomnames){
  let userid = Math.floor(randomNumber(0, 50))

  // let prefixstart = randomNumber(0, name.length);
  // let prefixend = randomNumber(prefixstart, name.length);

  // if (prefixstart === prefixend){
  //   if (prefixend === name.length){
  //     prefixstart -= 1;
  //   } else {
  //     prefixend += 1;
  //   }
  // }

  let object = {
    "userid": userid,
    "requests": [],
    "target": name
  }
  object["requests"].push(name)
  objectList.push(object)

}

fs.writeFileSync(outputfile, JSON.stringify(objectList, null, 2))




function randomNumber(min, max) { // Max is excluded!!!
  return Math.random() * (max - min) + min;
}