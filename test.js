async function main(){

  for (let i = 0; i < 100; i++){
    console.log("start", i)
    let a = new Promise(resolve => setTimeout(function() {
      console.log("A FINISHED", i)
      resolve()
    }, 100))
  
    await b(i)
    await (a)
    
    console.log("iteration", i, "done")
  }

}


async function b(i){
  await new Promise(resolve => setTimeout(function(){
    console.log("b", i)
    resolve()
  }, 2520));
}

main()