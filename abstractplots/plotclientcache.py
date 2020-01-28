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
datastructures = ["btree"]
datasets = ["stops", "randomstops", "realistic"]


dictionary = dict({"cache hit ratio": [], "datastructure": [], "fragment size": [], "executed query series": [], "dataset": []})
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
              queryseriescch = 0
              queryseriesccm = 0
              for query in queryserie:
                queryseriescch += query["cch"]
                queryseriesccm += query["ccm"]
              queryratios[seriesindex].append( (queryseriescch / (queryseriescch + queryseriesccm)) )

      for i in range(SERIESRANGE):
        if (len(queryratios[i]) > 0):
          dictionary["cache hit ratio"].append( sum(queryratios[i]) / len(queryratios[i]) )
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


print("")
print("1")

    
dfwc = [ dataframe.loc[(dataframe['executed query series'] >= 0) & (dataframe['dataset'] == "stops")],   
          dataframe.loc[(dataframe['executed query series'] >= 0) & (dataframe['dataset'] == "randomstops")],
          dataframe.loc[(dataframe['executed query series'] >= 0) & (dataframe['dataset'] == "realistic")]]

for (i, dataset) in enumerate(["query log", "randomized", "realistic"]):
  print( [str(round(dfwc[i].loc[dfwc[i]["fragment size"] == fs]["cache hit ratio"].mean(), 2)) for fs in ["25", "50", "75", "100"]])
    # print(df["server cache hit ratio"].mean())

print("")
print("2")

    
dfwc = [ dataframe.loc[(dataframe['executed query series'] >= 1) & (dataframe['dataset'] == "stops")],   
          dataframe.loc[(dataframe['executed query series'] >= 1) & (dataframe['dataset'] == "randomstops")],
          dataframe.loc[(dataframe['executed query series'] >= 1) & (dataframe['dataset'] == "realistic")]]

for (i, dataset) in enumerate(["query log", "randomized", "realistic"]):
  print( [str(round(dfwc[i].loc[dfwc[i]["fragment size"] == fs]["cache hit ratio"].mean(), 2)) for fs in ["25", "50", "75", "100"]])
    # print(df["server cache hit ratio"].mean())
    
print("")
print("3")

    

dfwc = [ dataframe.loc[(dataframe['executed query series'] >= 3) & (dataframe['dataset'] == "stops")],   
          dataframe.loc[(dataframe['executed query series'] >= 3) & (dataframe['dataset'] == "randomstops")],
          dataframe.loc[(dataframe['executed query series'] >= 3) & (dataframe['dataset'] == "realistic")]]

for (i, dataset) in enumerate(["query log", "randomized", "realistic"]):
  print( [str(round(dfwc[i].loc[dfwc[i]["fragment size"] == fs]["cache hit ratio"].mean(), 2)) for fs in ["25", "50", "75", "100"]])
    # print(df["server cache hit ratio"].mean())
    


# sns.set(font_scale=1.4)

# ax = sns.relplot( x = "executed query series" , y="cache hit ratio", hue="fragment size", hue_order = fragment_sizes, row="datastructure", col="dataset", data=dataframe, linewidth=2.5, kind="line", palette=sns.color_palette("Set1", dataframe["fragment size"].nunique()) )

# axes = ax.axes.flatten()

# i = 0

# ax.set(xlabel='evaluated query series', ylabel='client cache hit ratio per query series')
# for s in [r'437 $\times 10^3$ triples', r'124 $\times 10^6$ triples']:
# # for s in ["OSMnames"]:
#   axes[i].set_title(s)
#   i += 1

# plt.subplots_adjust(top=0.9)
# plt.gcf().suptitle('Client cache hit ratio per query series')

# plt.savefig(file_path("results/clientcacheratio/"+ "+".join(datasets) +'.png'))
# plt.show()
# print("Done")