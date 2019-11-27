# ns-community-detection
Detecting communities in social networks using conformity

## Scripts

extract_data.py

   Extracts data from [Weibo dataset](https://www.dropbox.com/s/vbjb46kpb5xx948/retweetWithContent.7z). To run this script, you will need Google Natural Language API credentials. A subset of the data has been extracted and can be found in output folder.

create_edge_list.py

   Uses the data extracted from Weibo dataset to create the edges of the graph. This graph produces edges.txt, each line of which corresponds to a directed edge.

clustering.py

   Community detection algorithm that writes the communities to c_communities.csv

Test.py
   
   Community detection algorithm that writes the communities of sub graph to the subgraph_comm.csv


