# Jing-Kai Lou (kaeaura@gamil.com)
# Thu Feb  2 17:14:20 CST 2012

#aladdin,trace/data/200406/green3/green3_data040601/data/user/am/aamm2jAULZmuk.o,aamm2jAULZmuk,o3483887,真愛等待,0,0,4,0,0,
#aladdin,trace/data/200406/green3/green3_data040601/data/user/am/aamNwyMMfLueI.o,aamNwyMMfLueI,jinnig04475,james,0,0,4,0,0,小捷仔;全身白;尋愛真難;煙霧

BEGIN{
	FS = ","
}

NF == 11 {
	cid = $5
	friends = $NF
	if (friends != "") {
		split(friends, friendArray, ";")
		for (fIndex in friendArray) 
			print cid, friendArray[fIndex]
	}
}

