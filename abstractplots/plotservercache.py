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

    

fragment_sizes = ["25", "50", "75", "100"]
datastructures = ["btree"]
datasets = ["stops", "randomstops", "realistic"]

dictionary = dict({"fragments requested": [], "ping":[], "cch":[], "ccm":[], "ccr": [], "sch":[], "scm":[], "server cache hit ratio":[], "bdw":[], "effall":[], "effused":[], "effratio":[], "dataset": [], "datastructure": [], "fragmentsize": []})
for dataset in datasets:
  for datastructure in datastructures:
    for fragmentsize in fragment_sizes:
      index = 1
      f = open(file_path("../newclientresults/generaldata"+dataset+datastructure+"test"+str(fragmentsize)+".txt")).readlines()
      for line in f:
        linesplit = json.loads(line) #line.rstrip().split(":")
        for item in linesplit:
          if (item == "efficiency"):
            dictionary["effall"].append(linesplit[item]["all"])
            dictionary["effused"].append(linesplit[item]["used"])
            if (linesplit[item]["all"] == 0):
              dictionary["effratio"].append(0)
            else:
              dictionary["effratio"].append(int(linesplit[item]["used"])/int(linesplit[item]["all"]))
          else:
            dictionary[item].append(linesplit[item])


        dictionary["dataset"].append(dataset)

        if datastructure == "prefix":
          dictionary["datastructure"].append("Prefix tree")
        else:
          dictionary["datastructure"].append("B-tree")

        dictionary["fragmentsize"].append(fragmentsize)
        dictionary["fragments requested"].append(index)
        if (linesplit["ccm"] + linesplit["cch"]) != 0:
          dictionary["ccr"].append(linesplit["cch"] / (linesplit["ccm"] + linesplit["cch"]))
        else:
          dictionary["ccr"].append(0)

        if (linesplit["scm"] + linesplit["sch"]) != 0:
          dictionary["server cache hit ratio"].append(linesplit["sch"] / (linesplit["scm"] + linesplit['sch']))
        else:
          dictionary["server cache hit ratio"].append(0)
        index += 1
        # print(linesplit)
for key in dictionary:
  print(key, len(dictionary[key]))

dataframe = pd.DataFrame(dictionary)
print(dataframe)

dfwc = [ dataframe.loc[(dataframe['fragments requested'] >= 1000) & (dataframe['dataset'] == "stops")],   
          dataframe.loc[(dataframe['fragments requested'] >= 1000) & (dataframe['dataset'] == "randomstops")],
          dataframe.loc[(dataframe['fragments requested'] >= 1000) & (dataframe['dataset'] == "realistic")]]

for (i, dataset) in enumerate(["query log", "randomized", "realistic"]):
  print( [str(round(dfwc[i].loc[dfwc[i]["fragmentsize"] == fs]["server cache hit ratio"].mean(), 2)) for fs in ["25", "50", "75", "100"]])
    # print(df["server cache hit ratio"].mean())
    


# sns.set(font_scale=1.4)

# ax = sns.relplot( x = "fragments requested" , y="server cache hit ratio", hue="fragmentsize", hue_order = fragment_sizes, row="datastructure", col="dataset", data=dataframe, linewidth=2.5, kind="line", palette=sns.color_palette("Set1", dataframe["fragmentsize"].nunique()) )

# axes = ax.axes.flatten()

# i = 0

# for d in ["Prefix tree", "B-tree"]:
#   for s in ["transport stops (query log)", "transport stops (randomized)",  "OSMnames (randomized)"]:
#   # for s in ["OSMnames"]:
#     axes[i].set_title(d + " | " + s)
#     i += 1

# plt.subplots_adjust(top=0.9)
# plt.gcf().suptitle('Server cache hit ratio')

# plt.savefig(file_path("results/servercacheratio/"+ "+".join(datasets) +'.png'))
# plt.show()
# print("Done")