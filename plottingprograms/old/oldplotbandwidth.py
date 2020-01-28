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
datasets = ["streets", "stops", "realistic"]

dictionary = dict({"bandwidth": [], "datastructure": [], "fragment size": [], "executed query series": [], "dataset": []})
for dataset in datasets:
  for datastructure in datastructures:
    for fragmentsize in fragment_sizes:
      filename = file_path("../newclientresults/"+dataset+datastructure+"test"+str(fragmentsize)+".json")
      print(filename)

      bandwidth = [list() for _ in range(SERIESRANGE)]

      with open(filename) as json_file:
        data = json.load(json_file)

        for user in data:
          userqueryseries = user["queryseries"]
          for (seriesindex, queryserie) in enumerate(userqueryseries):
            if (seriesindex < SERIESRANGE):
              queryseriebdw = 0
              for query in queryserie:
                if( len(query["bdw"]) > 0):
                  queryseriebdw += sum(query["bdw"])
              bandwidth[seriesindex].append( (queryseriebdw / len(queryserie)) / 1024 )

      seriesindex = 0
      for i in range(SERIESRANGE):
        if (len(bandwidth[i]) > 0):
          dictionary["bandwidth"].append( sum(bandwidth[i]) / len(bandwidth[i]) )
          if (datastructure == "btree"):
            dictionary["datastructure"].append( "B-tree" )
          else:
            dictionary["datastructure"].append( "Prefix Tree" )
          dictionary["fragment size"].append( fragmentsize )
          dictionary["dataset"].append( dataset )
          dictionary["executed query series"].append(i)
          seriesindex += 1
        else: break    

dataframe = pd.DataFrame(dictionary)
print(dataframe)


sns.set(font_scale=1.4)
ax = sns.relplot( x = "executed query series" , y="bandwidth", hue="fragment size", hue_order = fragment_sizes, row="datastructure", col="dataset", data=dataframe, linewidth=2.5, kind="line", palette=sns.color_palette("Set1", dataframe["fragment size"].nunique()) )

axes = ax.axes.flatten()

i = 0

ax.set(xlabel='evaluated query series', ylabel='average bandwidth per query (kB)')
for d in ["Prefix tree", "B-tree"]:
  for s in ["street names", "transport stops", "OSMnames"]:
    axes[i].set_title(d + "   |   " + s)
    i += 1

plt.subplots_adjust(top=0.9)
plt.gcf().suptitle('Average query bandwidth requirement per query series')

plt.savefig(file_path("results/bandwidth/"+ "+".join(datasets) +'.png'))
# plt.show()
print("Done")
