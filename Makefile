# Jing-Kai Lou (kaeaura@gmail.com) Fri Sep  2 11:33:47 CST 2011 
#
#	project folder structure
#		- src: source code
#		- trace: original trace
#			- data
#			- chat
#		- distillation: mined data
#			- user-collection
#			- act-collection
#			- trace_path
# 

#PROJ_DIR = /home/kae/trace/fairyland
PROJ_DIR = ..
TRACE_DIR = ${PROJ_DIR}/trace
DATA_DIR = ${PROJ_DIR}/distillation
SRC_DIR = ${PROJ_DIR}/src
EXP_RESUILT_DIR = ${PROJ_DIR}/exp
# trace
CHATTRACE_DIR = ${TRACE_DIR}/chat
DATATRACE_DIR = ${TRACE_DIR}/data
# data
PATH_COLLECTION_DIR = ${DATA_DIR}/trace_path
ACT_COLLECTION_DIR = ${DATA_DIR}/act_collections
USER_COLLECTION_DIR = ${DATA_DIR}/user_collections
GRAPH_DIR = ${ACT_COLLECTION_DIR}/graphs
FEATURE_DIR = ${DATA_DIR}/features
FEATURE_PART_DIR = ${FEATURE_DIR}/parts
REPORT_DIR = ${EXP_RESUILT_DIR}/report
GRAPHS_DIR = ${EXP_RESUILT_DIR}/graphs

# settings
#REALMS = alice mermaid 
REALMS = alice
# (@Baal)
#REALMS = mermaid plurk anderson doll (@baal)
#REALMS = mermaid 
#REALMS = anderson 
#REALMS = doll
# (@Nyx)
#REALMS = green alice red wolf (@nyx)
#REALMS = green 
#REALMS = alice 
#REALMS = red
#REALMS = wolf
#CHANNELS = tell say party family 
CHANNELS = family tell
LIFESPANS = 1 7 14 28 500
LIFESPANSS = 1,7,14,28,500
STEPWIDTH = 1
#LIFESPANS = 500
#LIFESPANSS = 500

sweave: doc/feature_report.Rnw
	cd doc ;\
	R CMD Sweave feature_report.Rnw ; \
	test -e feature_report.tex && pdflatex feature_report.tex; pdflatex feature_report.tex ;

clean:
	rm -f *.pyc

drop:
	cd .. \
	cp src ~/Dropbox/projects/churn_prediction_proj/

# scan the trace/chat 
scan:
	ls -alR ${CHATTRACE_DIR} | grep ^- | gawk '{ print $$(NF) }' | sort > scan_result.csv 
	sed -i -e '/.[c|h|o]~*$$/d' -e '/.txt$$/d' -e '/.map$$/d' -e '/.old/d' -e '/,t$$/d' -e '/^[^\.]+$$/d' scan_result.csv  

# pack distillation & src using rscync
pack:
	@date_info=`date +%Y-%m-%d`; \
	echo "tar zcvf $${date_info}_fairyland_dataset.tar.gz ${DATA_DIR}/* ${SRC_DIR}/*" ;
	tar zcvf $${date_info}_fairyland_dataset.tar.gz ${DATA_DIR}/* ${SRC_DIR}/* ;

# profile classification
class_profile: map_realm.py
	@echo "Classify the realm of personal profiles ..."; 
	@sh map_profile.sh ${USER_COLLECTION_DIR}/parsed_profiles.csv

# find the expected trac-path
get_path: get_trace_path.R
	for REALM in ${REALMS} ; do \
		Rscript get_trace_path.R -r $${REALM} ; \
	done

# copy trace
get_trace: get_trace.R
	@for REALM in ${REALMS} ; do \
		for CHANNEL in ${CHANNELS} ; do \
			TARGET=$${REALM}_$${CHANNEL} ; \
			if [ -e ${PATH_COLLECTION_DIR}/$${TARGET} ]; then \
				echo "Rscript --vanilla get_trace.R ${PATH_COLLECTION_DIR}/$${TARGET}" ; \
				Rscript --vanilla get_trace.R ${PATH_COLLECTION_DIR}/$${TARGET} ${ACT_COLLECTION_DIR}; \
			fi; \
		done ; \
	done

# convert the encoding form big5 to UTF8
b2u:
	@for REALM in ${REALMS}; do \
		for CHANNEL in ${CHANNELS}; do \
			TARGET=${ACT_COLLECTION_DIR}/$${REALM}_$${CHANNEL} ; \
			echo "Encoding $${TARGET} ..."; \
			test -f $${TARGET} && b2u.sh $${TARGET} > $${TARGET}.u || echo "$${TARGET} not exist"; \
			test -f $${TARGET}.u && mv $${TARGET}.u $${TARGET}; \
		done; \
	done;

# parse the traces
# supports for 2 different format chat logs: tell and family
nChparse: manipulators/new_ch_parser.awk manipulators/timestamp_converter.awk
	for REALM in ${REALMS}; do \
		for CHANNEL in ${CHANNELS}; do \
			echo "chParse-stage: REALM=$${REALM}; CHANNEL=$${CHANNEL}"; \
			TARGET=$${REALM}_$${CHANNEL}; \
			FULL_TARGET=${ACT_COLLECTION_DIR}/$${TARGET}; \
			DENST=${ACT_COLLECTION_DIR}/parsed/$${REALM}; \
			FULL_DENST=$${DENST}/$${TARGET}; \
			test -d DENS_TARGET || mkdir -p $${DENST}; \
			if [ -f $${FULL_TARGET} -a ! -f $${FULL_DENST}.parsed ]; then \
				echo -n "Parsing file: $${TARGET}"; \
				awk \
					-f manipulators/timestamp_converter.awk \
					$${FULL_TARGET} \
				| awk \
					-f manipulators/new_ch_parser.awk \
				> $${FULL_DENST}.parsed ; \
				echo " ...done"; \
			else \
				echo "\tStop parsing $${FULL_TARGET}"; \
				echo "\tReason: $${FULL_TARGET} does not exist or $${FULL_DENST}.parsed already exists\n"; \
			fi ; \
		done; \
	done

# friend links
fParse: manipulators/get_friend_links.awk
	for REALM in ${REALMS}; do \
		echo "freindParse-stage: REALN=$${REALM}"; \
		TARGET=$${REALM}_user.csv; \
		SOURCE_PATH=${USER_COLLECTION_DIR}/; \
		DENST_PATH=${ACT_COLLECTION_DIR}/parsed/$${REALM}; \
		awk -f manipulators/get_friend_links.awk $${SOURCE_PATH}/$${TARGET} | sort | uniq > $${DENST_PATH}/$${REALM}_friend.parsed; \
	done

pp: manipulators/mask.awk manipulators/sort_profile.sh
	@for REALM in ${REALMS}; do \
		echo "hash-stage: REALM=$${REALM};"; \
		PFILE=$${REALM}_user.csv; \
		SOURCE_PATH=${USER_COLLECTION_DIR} ; \
		HASHTABL=${ACT_COLLECTION_DIR}/parsed/$${REALM}/$${REALM}_cid; \
		test -f $${HASHTABL} -a -f $${SOURCE_PATH}/$${PFILE} \
			&& echo "abcd" ;\
	done

# produce the cid profile
prof: manipulators/mask.awk manipulators/sort_profile.sh manipulators/get_accountship.awk
	@for REALM in ${REALMS}; do \
		echo "hash-stage: REALM=$${REALM};"; \
		PFILE=$${REALM}_user.csv; \
		SOURCE_PATH=${USER_COLLECTION_DIR} ; \
		HASHTABL=${ACT_COLLECTION_DIR}/parsed/$${REALM}/$${REALM}_cid; \
		test -f $${HASHTABL} -a -f $${SOURCE_PATH}/$${PFILE} \
			&& sh manipulators/sort_profile.sh $${SOURCE_PATH}/$${PFILE} \
				| awk -f manipulators/get_accountship.awk \
				> $${SOURCE_PATH}/$${PFILE}.sorted \
			&& awk \
				-f manipulators/mask.awk \
				-v hashTable=$${HASHTABL} \
				-v maskCol=1 \
				$${SOURCE_PATH}/$${PFILE}.sorted \
				| sort -n\
				> ${ACT_COLLECTION_DIR}/parsed/$${REALM}/$${REALM}_char \
			&& rm -f $${SOURCE_PATH}/$${PFILE}.sorted \
			|| echo "file: $${PFILE} does not exist"; \
	done

# hash the cid and fid
hash: manipulators/hash_node.awk manipulators/mask.awk
	@for REALM in ${REALMS}; do \
		echo "hash-stage: REALM=$${REALM};"; \
		TFILE=$${REALM}_tell.parsed; \
		FFILE=$${REALM}_family.parsed; \
		LFILE=$${REALM}_friend.parsed; \
		SOURCE_PATH=${ACT_COLLECTION_DIR}/parsed/$${REALM}; \
		CID_FILE=$${REALM}_cid; \
		FID_FILE=$${REALM}_fid; \
		test -f $${SOURCE_PATH}/$${CID_FILE} && rm -f $${SOURCE_PATH}/$${CID_FILE}; \
		test -f $${SOURCE_PATH}/$${FID_FILE} && rm -f $${SOURCE_PATH}/$${FID_FILE}; \
		test -f $${SOURCE_PATH}/$${TFILE} -a -f $${SOURCE_PATH}/$${FFILE} \
			&& awk '{ printf "%s\n%s\n", $$2, $$3}' $${SOURCE_PATH}/$${TFILE} | sort | uniq >> $${SOURCE_PATH}/$${CID_FILE} \
			&& awk '{ print $$3}' $${SOURCE_PATH}/$${FFILE} | sort | uniq >> $${SOURCE_PATH}/$${CID_FILE} \
			&& sort $${SOURCE_PATH}/$${CID_FILE} | uniq > $${SOURCE_PATH}/$${CID_FILE}.temp \
			&& mv $${SOURCE_PATH}/$${CID_FILE}.temp $${SOURCE_PATH}/$${CID_FILE} \
			&& awk '{ print $$2}' $${SOURCE_PATH}/$${FFILE} | sort | uniq > $${SOURCE_PATH}/$${FID_FILE} \
			&& awk -f manipulators/mask.awk -v hashTable="$${SOURCE_PATH}/$${CID_FILE}" -v maskCol=2 $${SOURCE_PATH}/$${TFILE} \
				| awk -f manipulators/mask.awk -v hashTable="$${SOURCE_PATH}/$${CID_FILE}" -v maskCol=3 > $${SOURCE_PATH}/$${REALM}_tell.masked \
			&& awk -f manipulators/mask.awk -v hashTable="$${SOURCE_PATH}/$${FID_FILE}" -v maskCol=2 $${SOURCE_PATH}/$${FFILE} \
				| awk -f manipulators/mask.awk -v hashTable="$${SOURCE_PATH}/$${CID_FILE}" -v maskCol=3 > $${SOURCE_PATH}/$${REALM}_family.masked \
			|| echo "file: $${SOURCE_PATH}/$${TFILE} or $${SOURCE_PATH}/$${FFILE} does not exist" ; \
		test -f $${SOURCE_PATH}/$${LFILE} \
			&& awk -f manipulators/mask.awk -v hashTable="$${SOURCE_PATH}/$${CID_FILE}" -v maskCol=1 $${SOURCE_PATH}/$${LFILE} \
				| awk -f manipulators/mask.awk -v hashTable="$${SOURCE_PATH}/$${CID_FILE}" -v maskCol=2 > $${SOURCE_PATH}/$${REALM}_friend.masked; \
	done;

# compact the parsed trace
monthly_compact: manipulators/log_compactor.awk manipulators/log_chopper.awk
	@for REALM in ${REALMS}; do \
		for CHANNEL in ${CHANNELS}; do \
			echo "chcompact-stage: REALM=$${REALM}; CHANNEL=$${CHANNEL}"; \
			TARGET=$${REALM}_$${CHANNEL}.masked; \
			TARGET_PATH=${ACT_COLLECTION_DIR}/parsed/$${REALM}/$${TARGET}; \
			DEST_DIR=${ACT_COLLECTION_DIR}/monthly/$${REALM}; \
			echo "DEST_DIR:: $${DEST_DIR}" ; \
			test -d $${DEST_DIR} || echo "creating directory for $${REALM}"; mkdir -p $${DEST_DIR}; \
			test -e $${TARGET_PATH} \
				&& echo "\tcompacting ..."; \
					awk -f manipulators/log_compactor.awk -v unit="month" $${TARGET_PATH} | sort > $${DEST_DIR}/$${TARGET}.monthly \
				|| echo "$${TARGET} does not exist"; \
		done; \
	done

# compact the parsed trace
daily_compact: manipulators/log_compactor.awk manipulators/log_chopper.awk
	@for REALM in ${REALMS}; do \
		for CHANNEL in ${CHANNELS}; do \
			echo "chcompact-stage: $${REALM}; $${CHANNEL}"; \
			TARGET=$${REALM}_$${CHANNEL}.masked; \
			TARGET_PATH=${ACT_COLLECTION_DIR}/parsed/$${REALM}/$${TARGET}; \
			DEST_DIR=${ACT_COLLECTION_DIR}/daily/$${REALM}; \
			echo "DEST_DIR:: $${DEST_DIR}" ; \
			test -d $${DEST_DIR} || echo "creating directory for $${REALM}"; mkdir -p $${DEST_DIR}; \
			test -e $${TARGET_PATH} \
				&& echo "\tcompacting ..."; \
					awk -f manipulators/log_compactor.awk -v unit="day" $${TARGET_PATH} | sort > $${DEST_DIR}/$${TARGET}.daily \
				|| echo "$${TARGET} does not exist"; \
		done; \
	done

# build the graph
to_graph: analyzer/toGraph.py
	UNIT="daily"; \
	for REALM in ${REALMS}; do \
		echo "fileToPickle-stage: $${REALM}"; \
		EDGES=$${REALM}_tell.masked.$${UNIT} ; \
		TRADES=$${REALM}_moneyFlow.masked.$${UNIT} ; \
		MEMBERS=$${REALM}_family.masked.$${UNIT} ; \
		FRIENDS=$${REALM}_friend.masked; \
		STATUS=$${REALM}_char; \
		PARSED_PATH=${ACT_COLLECTION_DIR}/parsed/$${REALM}/ ; \
		UNIT_PATH=${ACT_COLLECTION_DIR}/$${UNIT}/$${REALM}/ ; \
		DEST_PATH=${GRAPHS_DIR} ; \
		ARG_D="-d ${LIFESPANSS}" ; \
		ARG_W="-w ${STEPWIDTH}" ; \
		test -d $${DEST_PATH} || mkdir -p $${DEST_PATH} ; \
		test -f $${UNIT_PATH}/$${MEMBERS} && ARG_M="-m $${UNIT_PATH}/$${MEMBERS}" || ARG_M="" ; \
		test -f $${PARSED_PATH}/$${STATUS} && ARG_S="-S $${PARSED_PATH}/$${STATUS}" || ARG_S="";\
		test -f $${PARSED_PATH}/$${FRIENDS} && ARG_F="-f $${PARSED_PATH}/$${FRIENDS}" || ARG_F=""; \
		test -f $${UNIT_PATH}/$${EDGES} \
			&& echo "python analyzer/toGraph.py -i $${UNIT_PATH}/$${EDGES} $${ARG_M} $${ARG_S} $${ARG_D} $${ARG_W} -a -o $${DEST_PATH}/$${REALM}_chat_static_d.gpickle" \
			&& time python analyzer/toGraph.py -i $${UNIT_PATH}/$${EDGES} $${ARG_M} $${ARG_S} $${ARG_D} $${ARG_W} -a -o $${DEST_PATH}/$${REALM}_chat_static_d.gpickle \
			&& echo "python analyzer/toGraph.py -i $${UNIT_PATH}/$${EDGES} $${ARG_M} $${ARG_S} $${ARG_F} $${ARG_D} $${ARG_W} -o $${DEST_PATH}/$${REALM}_d.gpickle -s $${DEST_PATH}/temporal/$${REALM}_d.cpickle" \
			&& time python analyzer/toGraph.py -i $${UNIT_PATH}/$${EDGES} $${ARG_M} $${ARG_S} $${ARG_F} $${ARG_D} $${ARG_W} -o $${DEST_PATH}/$${REALM}_d.gpickle -s $${DEST_PATH}/temporal/$${REALM}_d.cpickle \
			|| echo "$${UNIT_PATH}/$${EDGES}, $${UNIT_PATH}/$${MEMBERS}, or $${PARSED_PATH}/$${FRIENDS} does not exist" ; \
		test -f $${UNIT_PATH}/$${TRADES} \
			&& echo "python analyzer/toGraph.py -i $${UNIT_PATH}/$${TRADES} $${ARG_M} $${ARG_S} $${ARG_D} $${ARG_W} -a -o $${DEST_PATH}/$${REALM}_trade_static_d.gpickle" \
			&& time python analyzer/toGraph.py -i $${UNIT_PATH}/$${TRADES} $${ARG_M} $${ARG_S} $${ARG_D} $${ARG_W} -a -o $${DEST_PATH}/$${REALM}_trade_static_d.gpickle \
			&& echo "python analyzer/toGraph.py -i $${UNIT_PATH}/$${TRADES} $${ARG_M} $${ARG_S} $${ARG_F} $${ARG_D} $${ARG_W} -o $${DEST_PATH}/$${REALM}_d.gpickle -s $${DEST_PATH}/temporal/$${REALM}_d.cpickle" \
			&& time python analyzer/toGraph.py -i $${UNIT_PATH}/$${TRADES} $${ARG_M} $${ARG_S} $${ARG_F} $${ARG_D} $${ARG_W} -o $${DEST_PATH}/$${REALM}_d.gpickle -s $${DEST_PATH}/temporal/$${REALM}_d.cpickle \
	done; 

evo_report: analyzer/evolution.py
	@for REALM in ${REALMS}; do \
		for LIFESPAN in ${LIFESPANS}; do \
			echo "pcikleToTable-stage: $${REALM}"; \
			INFOLDER=${ACT_COLLECTION_DIR}/graphs/temporal ; \
			time python analyzer/evolution.py -I $${INFOLDER} -r $${REALM} -d $${LIFESPAN} -o ${REPORT_DIR}/$${REALM}_directed_$${LIFESPAN}d.csv ; \
			time python analyzer/evolution.py -u -I $${INFOLDER} -r $${REALM} -d $${LIFESPAN} -o ${REPORT_DIR}/$${REALM}_undirected_$${LIFESPAN}d.csv ; \
		done; \
	done;

top_report: analyzer/topology.py
	@EXE="analyzer/topology.py"; \
	for REALM in ${REALMS}; do \
		echo "GraphToFeature-stage: $${REALM};" ; \
		echo "--"; \
		for DIRECTION in "d" "u"; do \
			GRAPH="${GRAPH_DIR}/$${REALM}_$${DIRECTION}.gpickle"; \
			TABLE="${REPORT_DIR}/$${REALM}_$${DIRECTION}_topology.csv"; \
			INPUT_ARG="-i $${GRAPH}"; \
			OUTPUT_ARG="-o $${TABLE}"; \
			REALM_ARG="-r $${REALM}"; \
			test -f $${GRAPH} \
				&& echo "python $${EXE} $${INPUT_ARG} $${OUTPUT_ARG} $${REAKM_ARG} -M -v" \
				&& python $${EXE} $${INPUT_ARG} $${OUTPUT_ARG} $${REAKM_ARG} -M -v \
				|| echo "$${GRAPH} does not exist"; \
		done \
	done

# make the centrality tables
temp_centrality: net_builder.py
	@for REALM in ${REALMS}; do \
		echo "build the temporal centrality table (monthly)"; \
		TARGET_DIR=${ACT_COLLECTION_DIR}/monthly/$${REALM}; \
		for TARGET in `ls $${TARGET_DIR}/$${REALM}_tell.parsed.monthly_2003-07.tester`; do \
			TARGET_BASENAME=`basename $${TARGET}` ; \
			test -e ${EXP_RESUILT_DIR}/monthly_centrality/$${REALM} || mkdir ${EXP_RESUILT_DIR}/monthly_centrality/$${REALM} ; \
			echo "python net_builder.py -i $${TARGET} -o ${EXP_RESUILT_DIR}/monthly_centrality/$${REALM}/$${TARGET_BASENAME}.csv" ; \
			time python net_builder.py -i $${TARGET} -o ${EXP_RESUILT_DIR}/monthly_centrality/$${REALM}/$${TARGET_BASENAME}.csv ; \
		done; \
	done;

# mold (build the Char_profiles)
mold: mold_saver.py
	@MOLD_SIZE=30000 ; \
	for REALM in ${REALMS} ; do \
		USER_CSV=${USER_COLLECTION_DIR}/$${REALM}_user.csv ; \
		USER_PICKLE=${FEATURE_DIR}/$${REALM}_P ; \
		if [ -e $${USER_CSV} ] ; then \
			echo "python mold_saver.py -P $${USER_CSV} -g $${MOLD_SIZE} -S $${USER_PICKLE}" ; \
			python mold_saver.py -P $${USER_CSV} -g $${MOLD_SIZE} -S $${USER_PICKLE} ; \
		else \
			echo "file: $${USER_CSV} does not exist" ; \
		fi ; \
	done;

# joint the events to the Char_profiles
joint: mold_saver.py
	JLOG='../joint_command_history.log'; \
	for REALM in ${REALMS} ; do \
		USER_PICKLS=`ls ${FEATURE_DIR}/$${REALM}_P_part*.cPickle`; \
		for USER_PICKLE in $${USER_PICKLS} ; do \
			USER_PICKLE_BASENAME=`basename $${USER_PICKLE}` ; \
			for CHANNEL in ${CHANNELS} ; do \
				echo "$${CHANNEL}" ; \
				case $${CHANNEL} in \
					"tell") OPT="-t";; \
					"say") OPT="-s";; \
					"family") OPT="-f";; \
					"party") OPT="-p";;  \
				esac ; \
				ACT_CSVS=`ls ${ACT_COLLECTION_DIR}/$${REALM}_$${CHANNEL}.parsed_*` ; \
				for ACT_CSV in $${ACT_CSVS} ; do \
					STAMP=`basename $${ACT_CSV} | sed 's/[^_]*_[^_]*_\([^_]*\)/\1/'`; \
					echo "== $${ACT_CSV} ==" >> $${JLOG} ; \
					echo "python mold_saver.py -l $${USER_PICKLE} -x $${OPT} $${ACT_CSV} -S ${FEATURE_PART_DIR}/$${CHANNEL}/$${USER_PICKLE_BASENAME}$${OPT}_$${STAMP}" >> $${JLOG} ; \
					test -e "${FEATURE_PART_DIR}/$${CHANNEL}" || mkdir -p ${FEATURE_PART_DIR} ; \
					if [ -e ${FEATURE_PART_DIR}/$${CHANNEL}/$${USER_PICKLE_BASENAME}$${OPT}_$${STAMP}.cPickle ] ; then \
						echo "File exists, so skipped for not overwriting" ; \
					else \
						python mold_saver.py -l $${USER_PICKLE} -x $${OPT} $${ACT_CSV} -S ${FEATURE_PART_DIR}/$${CHANNEL}/$${USER_PICKLE_BASENAME}$${OPT}_$${STAMP} ; \
					fi \
				done ; \
			done; \
		done ; \
	done;

# make table
table: mold_loader.py
	for REALM in ${REALMS} ; do \
		OPTS="";\
		for CHANNEL in ${CHANNELS} ; do \
			MPATH=${FEATURE_PART_DIR}/$${CHANNEL} ; \
			MFILES=`ls $${MPATH}/$${REALM}_*` ; \
			for MFILE in $${MFILES} ; do \
				test -e $${MFILE} && OPTS="$${OPTS} -m $${MFILE}" || echo "$${MFILE} doesnt exist"; \
			done ; \
		done ; \
		echo "python mold_loader.py $${OPTS} -w ../exp/$${REALM}_activity.csv" ; \
		python mold_loader.py $${OPTS} -w ../exp/$${REALM}_activity.csv ; \
	done

# interaction
interaction: mold_loader.py
	for REALM in ${REALMS} ; do \
		OPTS="";\
		for CHANNEL in ${CHANNELS} ; do \
			MPATH=${FEATURE_PART_DIR}/$${CHANNEL} ; \
			MFILES=`ls $${MPATH}/$${REALM}_*` ; \
			for MFILE in $${MFILES} ; do \
				test -e $${MFILE} && OPTS="$${OPTS} -m $${MFILE}" || echo "$${MFILE} doesnt exist"; \
			done ; \
		done ; \
		echo "python mold_loader.py $${OPTS} -I ../exp/$${REALM}_interaction.csv" ; \
		python mold_loader.py $${OPTS} -I ../exp/$${REALM}_interaction.csv ; \
	done

# time slice (suspend)
parse: ${ACT_COLLECTION_DIR}/ anonymize.awk
	for REALM in ${REALMS} ; do \
		echo "Processing Realm: $${REALM}" ; \
		for CHANNEL in ${CHANNELS} ; do \
			echo "	Channel: $${CHANNEL}" ; \
			TARGET=$${REALM}_$${CHANNEL} ; \
			gawk \
				-f anonymize.awk \
				-v outfile=${ACT_COLLECTION_DIR}/$${TARGET}.parsed \
				-v cut_begin=2001-03-31-23-59-59 \
				-v cut_end=2004-06-30-23-59-59 \
				${ACT_COLLECTION_DIR}/$${TARGET}.pre_parsed \
			| sort -k 2 -g > ${ACT_COLLECTION_DIR}/$${TARGET}.id ; \
			sort ${ACT_COLLECTION_DIR}/$${TARGET}.parsed > ${ACT_COLLECTION_DIR}/$${TARGET}.parsed.sorted ; \
		done ; \
	done
