# Jing-Kai Lou (kaeaura@gmail.com) Tue Aug 30 14:27:35 CST 2011 
# Usage gawk -f pre_parsed.awk -v style=[style] [file]

BEGIN { 
	Month["Jan"] = "01"
	Month["Feb"] = "02"
	Month["Mar"] = "03"
	Month["Apr"] = "04"
	Month["May"] = "05"
	Month["Jun"] = "06"
	Month["Jul"] = "07"
	Month["Aug"] = "08"
	Month["Sep"] = "09"
	Month["Oct"] = "10"
	Month["Nov"] = "11"
	Month["Dec"] = "12"

	if (style == "tell"){
		#Tue Nov  4 15:09:01 2003 : 哈娜亞 tell 冷漠無情 : 安
		#|$1          |$2|$3      |$4                    |$5  |
		FS = ":"; 
		field_num = 5 
	}else if (style == "family") {
		#Thu Nov  6 19:44:20 2003 : [§夏日香氣§] 光之海: ..別洗
		#|$1          |$2|$3      |$4                  |$5    |
		FS = ":";
		field_num = 5
	}else if (style == "say") {
		#Tue Nov  4 14:06:37 2003 : 虧妹0萬華宏0: 安安
		#|$1          |$2|$3      |$4           |$5  |
		FS = ":";
		field_num = 5
	}else if (style == "party") {
		#Tue Nov  4 17:28:34 2003 : 蘇飛雅: ???
		#|$1          |$2|$3      |$4     |$5  |
		FS = ":"
		field_num = 5
	}else if (style == "radio") {

	}
}

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

function toEpoch(t){
	CMD = "date -u -d \""t"\" +%s"
	CMD | getline epoch_time
	close(CMD)
	return(epoch_time)
}

function remove_emotion(char_id){
	black_lists[1] = "搖著手上的彩球,甩著大腿的肥肉"
	black_lists[2] = "手裡拿著加油槍,大聲地喊道"
	black_lists[3] = "拿出一大把玫瑰花，跪在"
	black_lists[4] = "舉起一塊牌子,上面寫著"
	black_lists[5] = "放了一個又臭又響的屁"
	black_lists[6] = "自得其樂的跳著說"
	black_lists[7] = "看起來很舒服"
	black_lists[8] = "覺得很抱歉"
	black_lists[9] = "神經病似的"
	black_lists[10] = "殺氣騰騰地"
	black_lists[11] = "的臉上露出"
	black_lists[12] = "揮舞著雙手"
	black_lists[13] = "大聲地喊著"
	black_lists[14] = "用慢動作"
	black_lists[15] = "哼的一聲"
	black_lists[16] = "渾身顫抖"
	black_lists[17] = "大聲尖叫"
	black_lists[18] = "低頭沉思"
	black_lists[19] = "臉上露出"
	black_lists[20] = "一巴掌打"
	black_lists[21] = "非常愉快地"
	black_lists[22] = "完全同意"
	black_lists[23] = "點點頭"
	black_lists[24] = "陰森森"
	black_lists[25] = "坐下來"
	black_lists[26] = "聳聳肩"
	black_lists[27] = "愉快地"
	black_lists[28] = "高興地"
	black_lists[29] = "用力地"
	black_lists[30] = "由衷地"
	black_lists[31] = "忿忿地"
	black_lists[32] = "喃喃的"
	black_lists[33] = "昏倒了"
	black_lists[34] = "說道"
	black_lists[35] = "大喊"
	black_lists[36] = "對著"

	new_char_id = char_id
	for (bindex in black_lists){
		where = match(char_id, black_lists[bindex])
		if (where > 1) {
			new_char_id = substr(char_id, 1, where - 1)
			break
		}
	}
	return(new_char_id)
}

{ 
	if (style == "tell"){
		if (NF >= field_num){ 
			split($1, f1_arr, " ")
			split($3, f2_arr, " ")
			split($4, users_arr, " tell ")

			year 		= f2_arr[2]
			month 		= global_solidation(f1_arr[2])
			day 		= sprintf("%02d", f1_arr[3])
			hour 		= f1_arr[4]
			min 		= $2
			sec 		= f2_arr[1]
			sender 		= global_solidation(users_arr[1])
			receiver 	= global_solidation(users_arr[2])
			content 	= solidation($field_num)
			if (NF > field_num){
				for (i = field_num + 1; i <= NF; i = i + 1){
					content = content " " append
				}
			}
			content_length	= length(global_solidation($5))

			#time_info = toEpoch(month"-"day"-"year" "hour":"min":"sec) 
			time_info = year""Month[month]""day""hour""min""sec
			user_info = sender" "receiver

			printf "%s %s %d\n", time_info, user_info, content_length
		}
	}else if (style == "family") {
		if (NF >= field_num) {
			split($1, f1_arr, " ")
			split($3, f2_arr, " ")
			split($4, users_arr, " ")

			year			= f2_arr[2]
			month			= global_solidation(f1_arr[2])
			day				= sprintf("%02d", f1_arr[3])
			hour			= f1_arr[4]
			min				= $2
			sec 			= f2_arr[1]
			content			= $field_num

			if (length(users_arr) == 2) {
				sender_family 	= global_solidation(users_arr[1])
				sender 			= global_solidation(users_arr[2])
			} else {
				sender_family 	= ""
				sender 			= ""
				
				family_token_number 	= 0
				family_token_index		= 0
				lm_family_token_index 	= 0
				rm_family_token_index 	= 0
				regex 					= "^\\[.*\\]$"
				lm_regex 				= "^\\["
				rm_regex 				= "\\]$"

				for (users_index in users_arr) {
					users_elt = users_arr[users_index]
					where_family = match(users_elt, regex)
					where_lm_family = match(users_elt, lm_regex)
					where_rm_family = match(users_elt, rm_regex)
					if (where_family) {
						family_token_number = 1
						family_token_index = users_index
					}
					if (where_lm_family) 
						lm_family_token_index = users_index
					if (where_rm_family)
						rm_family_token_index = users_index
				}

				if (family_token_number && lm_family_token_index == rm_family_token_index) {
					sender_family = global_solidation(users_arr[family_token_index])
					for (users_index in users_arr) {
						if (users_index > family_token_index) {
							sender = sender""users_arr[users_index]
						}
					}
				} else if (rm_family_token_index > lm_family_token_index) {
					for (fi = lm_family_token_index; fi <= rm_family_token_index; fi++)
						sender_family = sender_family""users_arr[fi]
					for (si = rm_family_token_index + 1; si <= length(users_arr); si++)
						sender = sender""users_arr[si]
				}
			}

			sub("^\\[", "", sender_family)
			sub("\\]$", "", sender_family)

			if (NF > field_num){
				for (i = field_num + 1; i <= NF; i = i + 1){
					content = content " " append
				}
			}
			content_length	= length(global_solidation($5))
			
			#time_info = toEpoch(month"-"day"-"year" "hour":"min":"sec) 
			time_info = year""Month[month]""day""hour""min""sec
			user_info = sender_family" "remove_emotion(sender)

			# the sender id charter is too long to be true
			if (length(remove_emotion(sender)) >= 10) {
				next
			}

			printf "%s %s %d\n", time_info, user_info, content_length
		} 
	}else if (style == "say" || style == "party") {
		if (NF >= field_numa) {
			split($1, f1_arr, " ")
			split($3, f2_arr, " ")

			year			= f2_arr[2]
			month			= global_solidation(f1_arr[2])
			day				= sprintf("%02d", f1_arr[3])
			hour			= f1_arr[4]
			min				= $2
			sec 			= f2_arr[1]
			sender 			= remove_emotion($4)
			content			= $field_num
			if (NF > field_num){
				for (i = field_num + 1; i <= NF; i = i + 1){
					content = content " " append
				}
			}
			content_length	= length(global_solidation($5))

			#time_info = toEpoch(month"-"day"-"year" "hour":"min":"sec) 
			time_info = year""Month[month]""day""hour""min""sec
			user_info = global_solidation(remove_emotion(sender))

			if (length(user_info) >= 10) {
				next
			}

			printf "%s %s %d\n", time_info, user_info, content_length
		}
	}
}
