# Jing-Kai Lou (kaeaura@gamil.com)

argv = commandArgs(TRUE)
argc = length(argv)
stopifnot(argc == 2)

data_file = argv[1]
plot_file = argv[2]

require('e1071')
cv 			= 3
p_index 	= 1
atr_index 	= 4:6
act_index 	= 9:40
event_index = 41:43

feature_index = c(act_index, event_index)

if (file.exists(data_file)) {

	print ("loading file")
	data 		= read.csv(data_file, header = T)
	print ("cutting training and testing sets")
	train_num 	= nrow(data) %/% 3 * 2
	train_index = sample(nrow(data), train_num)
	train_x 	= data[train_index, feature_index]
	train_y		= data[train_index, p_index]
	test_x		= data[-train_index, feature_index]
	test_y		= data[-train_index, p_index]

	print ("building model")
	model		= svm(train_x, train_y, cross = 3)
	print ("predicting testing set")
	pred		= predict(model, test_x)

	# plot figure
	print ("ploting figure")
	png(sprintf("%s.png", plot_file))
	plot( 	
		x 		= test_y, 
		y 		= pred,
		xlab	= 'truth value',
		ylab	= sprintf('predict with %02d features', length(feature_index)),
		main	= sprintf('svm regr. (cv = %d, cor = %.3f)', cv, cor(test_y, pred))
	)

	text(x = min(test_y), y = max(pred), sprintf("Train: %5d; Test: %5d", nrow(train_x), nrow(test_x)), adj = c(0, 0))

	# generate log
	print ("done")
	print (names(summary(model)))
	RMSE = sapply(summary(model)$MSE, function(x) sqrt(x))
	write (file = sprintf("%s.RMSE", plot_file), RMSE, ncol = 1)

}else{

	cat (sprintf("File %s does not eixt", data_file))
}
