# Jing-Kai Lou (kaeaura@gamil.com)

BEGIN{
	if (cutMin == "")
		cutMin = 0
	if (cutMax == "")
		cutMax = 9999999999
	if (cutIndex == "")
		cutIndex = 1
}

NF >= cutIndex{
	cutItem = $cutIndex
	if (cutItem >= cutMin && cutItem <= cutMax)
		print $0
}
