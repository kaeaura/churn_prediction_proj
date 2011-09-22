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

PROJ_DIR = /home/kae/trace/fairyland
TRACE_DIR = ${PROJ_DIR}/trace
DATA_DIR = ${PROJ_DIR}/distillation
SRC_DIR = ${PROJ_DIR}/src
# trace
CHATTRACE_DIR = ${TRACE_DIR}/chat
DATATRACE_DIR = ${TRACE_DIR}/data
# data
PATH_COLLECTION_DIR = ${DATA_DIR}/trace_path
ACT_COLLECTION_DIR = ${DATA_DIR}/act_collections
USER_COLLECTION_DIR = ${DATA_DIR}/user_collections
# settings
REALMS = alice anderson doll green mermaid red wolf
CHANNELS = tell say family party 

clear:
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
# works for 4 different-format chat logs: tell, say, family, party
# and extract the family information
chparse: ch_parser.awk
	@for REALM in ${REALMS}; do \
		for CHANNEL in ${CHANNELS}; do \
			echo "chparse-stage: $${REALM}; $${CHANNEL}"; \
			TARGET=${ACT_COLLECTION_DIR}/$${REALM}_$${CHANNEL}; \
			if [ -e $${TARGET} ]; then \
				echo -n "Parsing file: $${TARGET}"; \
				gawk \
					-f ch_parser.awk \
					-v style=$${CHANNEL} $${TARGET} \
				> $${TARGET}.parsed; \
				echo " ...done"; \
				if [ $${CHANNEL} = "family" ]; then \
					echo -n "extracting family information ..."; \
					sh family_info.sh $${TARGET}.parsed \
					> $${TARGET}.time; \
					echo " done"; \
				fi \
			else \
				echo "file: $${TARGET} does not exist"; \
			fi \
		done; \
	done;

# mold (get features extracted from *.parsed files) (TODO need for modictation)
mold: mold_saver.py
	@for REALM in ${REALMS}; do \
		for CHANNEL in ${CHANNELS}; do \
			echo "mold-stage: $${REALM}; $${CHANNEL}"; \
			TARGET=${ACT_COLLECTION_DIR}/$${REALM}_$${CHANNEL}; \
			if [ -e $${TARGET}.parsed ]; then \
				echo -n "Molding file: $${TARGET}"; \
				python mold_saver.py -l $${CHANNEL} -i $${TARGET}.parsed -s $${TARGET}.feature ; \
				echo " ...done"; \
			else \
				echo "file: $${TARGET}.parsed does not exist"; \
			fi \
		done; \
	done;

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


