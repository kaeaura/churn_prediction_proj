# Jing-Kai Lou (kaeaura@gmail.com)
# Wed Aug 24 17:16:40 CST 2011
#!/bin/bash

# for tar.gz and tgz
TGZFILES=`find $1 -name "*.tgz" -type f -o -name "*.tar.gz" -type f`
TARFILES=`find $1 -name "*.tar" -type f`
GZFILES=`find $1 -name "*.gz" -type f`

for TGZFILE in ${TGZFILES} 
do
	tar zxvf ${TGZFILE} -C `dirname ${TGZFILE}`
	rm -f ${TGZFILE}
done

for TARFILE in ${TARFILES}
do
	tar xvf ${TARFILE} -C `dirname ${TARFILE}`
	rm -f ${TARFILE}
done

for GZFILE in ${GZFILES}
do
	gzip -d ${GZFILE}
done
