# Jing-Kai Lou (kaeaura@gamil.com)
# Wed Sep 28 16:04:48 CST 2011
# project included functions

find_extension <- function(filename) {
	if (class(filename) == "character" && length(filename) == 1) {
		split_filename = strsplit(filename, '.', fixed = T)[[1]]
		if (length(split_filename) > 1) {
			return(split_filename[length(split_filename)])
		}else{
			cat("contains no exe")
			return(NULL)
		}
	}
}

replace_extention <- function(filename, replacing) {
	original_extension = find_extension(filename)
	if (!is.null(original_extension)) {
		return(sub(sprintf('.%s$', original_extension), replacing, filename))
	} else {
		return(1)
	}
}

