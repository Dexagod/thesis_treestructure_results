import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
import json
import math
import os
def file_path(relative_path):
    dir = os.path.dirname(os.path.abspath(__file__))
    split_path = relative_path.split("/")
    new_path = os.path.join(dir, *split_path)
    return new_path
    

SERIESRANGE = 25
SERIESSIZE = 4
fragment_sizes = ["25", "50", "75", "100"]
datastructures = ["prefix", "btree"]

execution_time = 150
datasets = ["stops", "randomstops", "realistic"]

for dataset in datasets:
  print(dataset)
  dictionary = dict({"seriesindex": [], "execution time": [], "results": [], "fragment size": [], "datastructure": []})
  for datastructure in datastructures:
    for fragmentsize in fragment_sizes:
      filename = file_path("../newclientresults/"+dataset+datastructure+"test"+str(fragmentsize)+".json")


      querytimings = [list() for _ in range(SERIESSIZE)]
      with open(filename) as json_file:
        data = json.load(json_file)
        for user in data:
          for (seriesindex, queryserie) in enumerate(user["queryseries"]):
            for (queryindex, query) in enumerate(queryserie):
              if queryindex < SERIESSIZE:
                resultspertiming = [0 for _ in range(execution_time)]
                for timing in sorted(query["timing"]):
                  for i in range(math.floor(timing), execution_time):
                    resultspertiming[i] += 1
                querytimings[queryindex].append(resultspertiming)
                
      resultingtimings = [list() for _ in range(SERIESSIZE)]
      for i in range(SERIESSIZE):
        queryindexaverage = [list() for _ in range(execution_time)]
        for entry in querytimings[i]:
          for j in range(execution_time):
            queryindexaverage[j].append(entry[j])

        for k in range(execution_time):
          if len (queryindexaverage[k]) == 0:
            queryindexaverage[k] = 0
          else:
            queryindexaverage[k] = sum(queryindexaverage[k]) / len(queryindexaverage[k])

        resultingtimings[i] = queryindexaverage

      for i in range(SERIESSIZE):
        for j in range(execution_time):
          dictionary["fragment size"].append(fragmentsize)
          dictionary["datastructure"].append(datastructure)

          dictionary["seriesindex"].append(i)
          dictionary["execution time"].append(j)
          dictionary["results"].append(resultingtimings[i][j])
          
  dataframe = pd.DataFrame(dictionary)



  sns.set(font_scale=1.6)
  ax = sns.relplot( x = "execution time" , y="results", hue="fragment size", hue_order = fragment_sizes, col="seriesindex" ,row="datastructure", data=dataframe, linewidth=2.5, kind="line", palette=sns.color_palette("Set1", dataframe["fragment size"].nunique()) )
  

  ax.set(xlabel='execution time', ylabel='retrieved results')
  axes = ax.axes.flatten()

  i = 0

  plt.ylim(0, 25)
  plt.gcf().suptitle('Average performance for the  first five queries per series')
  ax.set(xlabel='execution time', ylabel='retrieved results')
  
  ax.legend(loc='center bottom', bbox_to_anchor=(0.5, 1.25), ncol=4)

  if dataset == "realistic":
    datasetname = "OSMnames"
  if dataset == "stops":
    datasetname = "transport stops"
  if dataset == "streets":
    datasetname = "street names"

  for d in ["Prefix tree", "B-tree"]:
    # for s in ["street names", "transport stops", "OSMnames"]:
    for s in ["query 1", "query 2", "query 3", "query 4"]:
      axes[i].set_title( d + " | " + s)
      i += 1

  plt.subplots_adjust(top=0.9)
  plt.gcf().suptitle('Average query results in 150ms over subsequent queries in a series')
  plt.savefig(file_path("results/performance/"+ dataset +'.png'))
