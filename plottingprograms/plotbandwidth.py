import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
import json
import os
def file_path(relative_path):
    dir = os.path.dirname(os.path.abspath(__file__))
    split_path = relative_path.split("/")
    new_path = os.path.join(dir, *split_path)
    return new_path

SERIESRANGE = 25
fragment_sizes = ["25", "50", "75", "100"]
datastructures = ["prefix", "btree"]
datasets = ["stops", "randomstops", "realistic"]

dictionary = dict({"bandwidth": [], "datastructure": [], "fragment size": [], "cache": [], "dataset": []})

for testtype in ["Maximum"]: #"Average", "Median", 
  for dataset in datasets:
    for datastructure in datastructures:
      for fragmentsize in fragment_sizes:
        filename = file_path("../newclientresults/"+dataset+datastructure+"test"+str(fragmentsize)+".json")
        print(filename)


        with open(filename) as json_file:
          data = json.load(json_file)

          for user in data:
            userqueryseries = user["queryseries"]
            for (seriesindex, queryserie) in enumerate(userqueryseries):
              if (seriesindex < SERIESRANGE):
                # print(len(queryserie), [sum(query["bdw"]) for query in queryserie], ((sum([sum(query["bdw"]) for query in queryserie]) / len(queryserie)) / 1024), ((sorted([sum(query["bdw"]) for query in queryserie])[len(queryserie)//2]) / 1024), ((max([sum(query["bdw"]) for query in queryserie])) / 1024))

                # print((max([sum(query["bdw"]) for query in queryserie]) / len(queryserie)), [query["bdw"] for query in queryserie])

                if testtype == "Average":
                  result = ((sum([sum(query["bdw"]) for query in queryserie]) / len(queryserie)) / 1024)
                elif testtype == "Median":
                  result = ((sorted([sum(query["bdw"]) for query in queryserie])[len(queryserie)//2]) / 1024) # this is not exactly correct on uneven lengths
                elif testtype == "Maximum":
                  # result = ((max([sum(query["bdw"]) for query in queryserie]) / len(queryserie)) / 1024)
                  # result = ((sum([sum(query["bdw"]) for query in queryserie]) / len(queryserie)) / 1024)
                  result = (sum([sum(query["bdw"]) for query in queryserie]) / 1024)
                
                
                dictionary["bandwidth"].append(result)

                if seriesindex >= 3:
                  dictionary["cache"].append("warm")
                else:
                  dictionary["cache"].append("cold")

                if (datastructure == "btree"):
                  dictionary["datastructure"].append( "B-tree" )
                else:
                  dictionary["datastructure"].append( "Prefix Tree" )
                
                dictionary["fragment size"].append( fragmentsize )
                dictionary["dataset"].append( dataset )

  dataframe = pd.DataFrame(dictionary)
  print(dataframe)


  # sns.set(font_scale=1.4)
  # ax = sns.relplot( x = "cache" , y="bandwidth", hue="fragment size", hue_order = fragment_sizes, row="datastructure", col="dataset", data=dataframe, linewidth=2.5, kind="line", palette=sns.color_palette("Set1", dataframe["fragment size"].nunique()) )



  ax = sns.catplot(x="fragment size", y="bandwidth",
                  hue="cache",
                  data=dataframe, order=fragment_sizes,
                  row="datastructure", col="dataset",
                  kind="boxen", aspect=.7)


  # sns.set(font_scale=1.1)
  # ax.fig.tight_layout()
  plt.subplots_adjust(top=0.9)
  plt.subplots_adjust(hspace=0.25, wspace=0.6)

  axes = ax.axes.flatten()
  i = 0


  ax.set(xlabel='fragment size', ylabel='bandwidth (kB)')
  for d in ["Prefix tree", "B-tree"]:
    for s in ["transport stops (query log)", "transport stops (randomized)",  "OSMnames (randomized)"]:
      axes[i].set_title(d + " | " + s)
      i += 1

  plt.gcf().suptitle('Total bandwidth required per series of queries')

  plt.savefig(file_path("results/bandwidth/"+ testtype + "+".join(datasets) +'.png'))
  plt.show()
  print("Done")
