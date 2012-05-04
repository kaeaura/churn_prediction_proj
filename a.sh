producer='analyzer/db.py'
inputDir='../exp/db/degree_seq/'
outputDir='doc/interactions_over_platforms/tables/deg_seq'
idArg='inDegSeq'
odArg='outDegSeq'
dArg='degSeq'

# list of files under inputDir
#anderson_chat_degree_seq.db
#anderson_friend_degree_seq.db
#twitter_cut_degree_seq.db
#twitter_follower_degree_seq.db
#undirected
#yahoo_chat_degree_seq.db

python ${producer} -i ${inputDir}/anderson_chat_degree_seq.db -a ${idArg} -w csvs -o ${outputDir}/fairyland_interaction_indegree.csv 
python ${producer} -i ${inputDir}/anderson_chat_degree_seq.db -a ${odArg} -w csvs -o ${outputDir}/fairyland_interaction_outdegree.csv 

python ${producer} -i ${inputDir}/anderson_friend_degree_seq.db -a ${idArg} -w csvs -o ${outputDir}/fairyland_ally_indegree.csv 
python ${producer} -i ${inputDir}/anderson_friend_degree_seq.db -a ${odArg} -w csvs -o ${outputDir}/fairyland_ally_outdegree.csv 

python ${producer} -i ${inputDir}/twitter_cut_degree_seq.db -a ${idArg} -w csvs -o ${outputDir}/twitter_interaction_indegree.csv
python ${producer} -i ${inputDir}/twitter_cut_degree_seq.db -a ${odArg} -w csvs -o ${outputDir}/twitter_interaction_outdegree.csv 

python ${producer} -i ${inputDir}/twitter_follower_degree_seq.db -a ${idArg} -w csvs -o ${outputDir}/twitter_ally_indegree.csv
python ${producer} -i ${inputDir}/twitter_follower_degree_seq.db -a ${odArg} -w csvs -o ${outputDir}/twitter_ally_outdegree.csv 

python ${producer} -i ${inputDir}/yahoo_chat_degree_seq.db -a ${idArg} -w csvs -o ${outputDir}/yahoo_interaction_indegree.csv
python ${producer} -i ${inputDir}/yahoo_chat_degree_seq.db -a ${odArg} -w csvs -o ${outputDir}/yahoo_interaction_outdegree.csv

python ${producer} -i ${inputDir}/yahoo_friend_degree_seq.db -a ${dArg} -w csvs -o ${outputDir}/yahoo_ally_degree.csv
