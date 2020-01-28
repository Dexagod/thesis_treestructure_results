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

dictionary = dict({"efficiency": [], "datastructure": [], "fragment size": [], "executed query series": [], "dataset": []})

for dataset in datasets:
  for datastructure in datastructures:
    for fragmentsize in fragment_sizes:
      filename = file_path("../newclientresults/"+dataset+datastructure+"test"+str(fragmentsize)+".json")
      print(filename)

      queryratios = [list() for _ in range(SERIESRANGE)]

      with open(filename) as json_file:
        data = json.load(json_file)

        for user in data:
          userqueryseries = user["queryseries"]
          for (seriesindex, queryserie) in enumerate(userqueryseries):
            if (seriesindex < SERIESRANGE):
              queryserietotalitems = 0
              queryserieuseditems = 0

              queryseriesalllist = []
              queryseriesusedlist = []

              for query in queryserie:
                if( len(query["efficiency"]) > 0):
                  for efficiency_info in query["efficiency"]:
                    queryseriesalllist.append(efficiency_info["all"])
                    queryseriesusedlist.append(efficiency_info["used"])

              if (len(queryseriesalllist) != 0):
                queryserietotalitems = max(queryseriesalllist) / len(queryserie)
              if (len(queryseriesusedlist) != 0):
                queryserieuseditems = max(queryseriesusedlist) / len(queryserie)
              
              if (queryserietotalitems != 0):
                queryratios[seriesindex].append( (queryserieuseditems / queryserietotalitems) )
              else:
                queryratios[seriesindex].append( 0 )

      for i in range(SERIESRANGE):
        if (len(queryratios[i]) > 0):
          dictionary["efficiency"].append( sum(queryratios[i]) / len(queryratios[i]) )
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


ax = sns.relplot( x = "executed query series" , y="efficiency", hue="fragment size", hue_order = fragment_sizes, row="datastructure", col="dataset", data=dataframe, linewidth=2.5, kind="line", palette=sns.color_palette("Set1", dataframe["fragment size"].nunique()) )

axes = ax.axes.flatten()

i = 0


ax.set(xlabel='evaluated query series', ylabel='efficiency ratio per query series')
for d in ["Prefix tree", "B-tree"]:
  for s in ["street names", "transport stops", "OSMnames"]:
    axes[i].set_title(d + "   |   " + s)
    i += 1

plt.subplots_adjust(top=0.9)
plt.gcf().suptitle('Efficiency ratio per query series')

plt.savefig(file_path("results/efficiency/"+ "+".join(datasets) +'.png'))
# plt.show()
print("Done")
