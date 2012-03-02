# Jing-Kai Lou (kaeaura@gamil.com)
# Mon Jan 30 16:44:35 CST 2012
# currently support "tell" and "family" channels only

function global_solidation(x){
	gsub(" ", "", x) 
	return(x)
}

function solidation(x){
	sub(" ", "", x) 
	return(x)
}

function surround_solidation(x){
	sub("^ *", "", x)
	sub(" *$", "", x)
	return(x)
}

function remove_emotion(char_id){
	black_lists[1] = "搖著手上的彩球,甩著大腿的肥肉"
	black_lists[2] = "手裡拿著加油槍,大聲地喊道"
	black_lists[3] = "拿出一大把玫瑰花，跪在"
	black_lists[4] = "舉起一塊牌子,上面寫著"
	black_lists[5] = "放了一個又臭又響的屁"
	black_lists[6] = "打了個大大的哈欠"
	black_lists[7] = "自得其樂的跳著說"
	black_lists[8] = "看起來很舒服"
	black_lists[9] = "覺得很抱歉"
	black_lists[10] = "神經病似的"
	black_lists[11] = "殺氣騰騰地"
	black_lists[12] = "的臉上露出"
	black_lists[13] = "揮舞著雙手"
	black_lists[14] = "大聲地喊著"
	black_lists[15] = "用慢動作"
	black_lists[16] = "哼的一聲"
	black_lists[17] = "渾身顫抖"
	black_lists[18] = "大聲尖叫"
	black_lists[19] = "低頭沉思"
	black_lists[20] = "臉上露出"
	black_lists[21] = "一巴掌打"
	black_lists[22] = "非常愉快地"
	black_lists[23] = "完全同意"
	black_lists[24] = "點點頭"
	black_lists[25] = "陰森森"
	black_lists[26] = "坐下來"
	black_lists[27] = "聳聳肩"
	black_lists[28] = "愉快地"
	black_lists[29] = "高興地"
	black_lists[30] = "用力地"
	black_lists[31] = "由衷地"
	black_lists[32] = "忿忿地"
	black_lists[33] = "喃喃的"
	black_lists[34] = "昏倒了"
	black_lists[35] = "大聲地"
	black_lists[35] = "說道"
	black_lists[36] = "大喊"
	black_lists[37] = "對著"

	new_char_id = char_id
	for (bindex = 1; bindex <= length(black_lists); bindex++){
		where = match(char_id, black_lists[bindex])
		if (where > 1) {
			new_char_id = substr(char_id, 1, where - 1)
			break
		}
	}
	return(new_char_id)
}

BEGIN{
	FS = ":"
	tToken = " tell "
	requiredNF = 3
}

NF >= requiredNF {
	# timestamp would be handled as a 14-digits number
	timestamp = global_solidation($1)

	# id section includes (secondID and receiverID) or (secondID and familyID)
	idSection = $2
	if ($2 ~ tToken) 						# tell channel
		splitToken = tToken
	else 									# family channel
		splitToken = " "

	split(idSection, idArray, splitToken)

	if (length(idArray) == 2) {
		firstID = global_solidation(idArray[1])
		secondID = global_solidation(idArray[2])

		if (splitToken == " " && firstID ~ "^\\[.*\\]$") {
			sub("^\\[", "", firstID)
			sub("\\]$", "", firstID)
		} else if (splitToken == tToken && length(firstID) > 10) {
			firstID = remove_emotion(firstID)
		}

		secondID = remove_emotion(secondID)
	} else {
		next
	}

	# content section includes the words
	contSection = ""
	for (nf = requiredNF; nf <= NF; nf++) 
		contSection = contSection $nf
	contLength = length(global_solidation(contSection))

	# print output
	print timestamp, firstID, secondID, contLength

}
