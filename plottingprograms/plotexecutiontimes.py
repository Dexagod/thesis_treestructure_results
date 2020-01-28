import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
import os
def file_path(relative_path):
    dir = os.path.dirname(os.path.abspath(__file__))
    split_path = relative_path.split("/")
    new_path = os.path.join(dir, *split_path)
    return new_path

stats = dict({"processing": [], "totalprocessingtime" : [], "onlyprocessingtime" : [], "jsonldprocessing" : [], "totalrequest" : [], "fragmentsize": [], "cache": []})
for datastructure in ["btree"]:
  for fragmentsize in [25, 50, 75, 100, 200, 500, 1000]:
    for cache in ["cold", "warm"]:
      f = open(file_path("../timetests/"+cache+"timetest"+datastructure+str(fragmentsize)+".txt")).readlines()
      for line in f:
        linesplit = line.rstrip().split(":")
        if (linesplit[0] == "ping"):
          if (cache == "cold"):
            stats["cache"].append("cache miss (cache server)")
          else:
            stats["cache"].append("cache hit (cache server)")
          stats["fragmentsize"].append(int(fragmentsize))
        else :
          stats[linesplit[0]].append(float(linesplit[1]))
        
for key in stats:
  print(key, len(stats[key]))

sns.set(style="whitegrid")
sns.set(font_scale=1.25)


dataframe = pd.DataFrame(stats)

for col in [("jsonldprocessing", "time (ms)", False, "Conversion time from JSON-LD fragment to triples"), 
            ("onlyprocessingtime", "time (ms)", True, "Time to request and receive a fragment from the server"), 
            ("totalprocessingtime", "time (ms)", True, "Total time to retrieve and convert a fragment from the server")]:

  if (col[2]):
    ax = sns.boxenplot( x = "fragmentsize", y=col[0], hue="cache", data=dataframe, linewidth=2.5)
  else:
    ax = sns.boxenplot( x = "fragmentsize", y=col[0], data=dataframe, linewidth=2.5)
  ax.set_title(col[3])
  ax.set_xlabel("Subjects per fragment", fontsize = 12)
  ax.set_ylabel(col[1], fontsize = 12)

  for item in ([ax.title, ax.xaxis.label, ax.yaxis.label]):
    item.set_fontsize(18)

  plt.ylim(0, 500)
  plt.savefig(file_path("results/executiontimes/"+col[0]+'.png'), bbox_inches='tight')
  plt.show()