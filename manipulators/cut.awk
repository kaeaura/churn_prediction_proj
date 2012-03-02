# Jing-Kai Lou (kaeaura@gamil.com)

BEGIN{
	if (cutThr == "")
		cutThr = 0
	if (cutIndex == "")
		cutIndex = 1
}

NF >= cutIndex{
	cutItem = $cutIndex
	if (cutItem >= cutThr)
		print $0
	else
		next
}
