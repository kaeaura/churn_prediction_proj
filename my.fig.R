#my.fig.psdev
#my.fig.type: 1 single
#             2 side-by-side (1x2) two figures
#             3 side-by-side (2x2) four figures
#             4 side-by-side (3x2) six figures

my.fig.on = T
my.fig.png.on = F
my.fig.png.width = NULL
my.fig.png.height = NULL

mf.p <- function(v=NULL) {
  if (is.null(v)) {
    cat("my.fig.png.on =", my.fig.png.on, "\n")
    return(invisible(NULL))
  }
  if (!is.logical(v)) stop("not boolean value")
  
  my.fig.png.on <<- v
  cat("my.fig.png turn", v, "\n")
}

mf <- function(v=NULL) {
  if (is.null(v)) {
    cat("my.fig.on =", my.fig.on, "\n")
    return(invisible(NULL))
  }
  if (!is.logical(v)) stop("not boolean value")
  
  my.fig.on <<- v
  cat("my.fig turn", v, "\n")
}
# w: width / column / horizontal
# h: height / row / vertical
# h.inch, w.inch: specify figure height and width directly (by inch)
# main: main title exists?

my.fig <- function(s, h=1, w=1, h.inch = NA, w.inch = NA, main=F, sub=F) {  
  if (!my.fig.on) {
    my.fig.opar <<- par(mfrow=c(h,w))
    return(invisible(NULL))
  }
  
  my.fig.name <<- s
  my.fig.width <<- w
  my.fig.height <<- h
  
  if (is.na(h.inch)) h.inch = switch(h, 6, 9, 12, 14)
  if (is.na(w.inch)) w.inch = switch(w, 8, 12, 16)

  postscript(file=paste(my.fig.name,".eps",sep=""),
    width = w.inch,
    height = h.inch,
    horizontal = FALSE, onefile = FALSE, paper = "special", family="Helvetica")
  dev.control("enable"); # for copying contents to png
  my.fig.psdev <<- dev.cur()

  par(mfrow=c(h,w))
  
  # mar default = c(5, 4, 4, 2) + 0.1 c(bottom, left, top, right)
  par(mgp=c(2,.8,0), mar=c(ifelse(sub, 4.2, 3), 3, 
                           ifelse(main, 1.5, ifelse(sub, .5, 1)), 1) + 0.1)

  if (w == 1 && h == 1) par(cex=1.2)  
  else par(cex=1.5)
}

my.fig.off <- function() {
  if (!my.fig.on) {
    par(my.fig.opar)
    return(invisible(NULL))
  }

  if (my.fig.png.on) {
  
    if (is.null(my.fig.png.width)) width = ifelse(w==1, 800, 1000) else
      width = my.fig.png.width
    if (is.null(my.fig.png.height)) height = switch(h, 600, 600, 1200, 1200) else
      height = my.fig.png.height
  
    png(filename=paste(my.fig.name,".png",sep=""), width=width, height=height)
    pngdev = dev.cur()
  
    dev.set(my.fig.psdev)
    dev.copy(which=pngdev)
    dev.off(pngdev)
  }
  
  dev.off(my.fig.psdev)
}

my.png.fig <- function(s, h=1, w=1) {

  if (!my.fig.on) {
    my.fig.opar <<- par(mfrow=c(h,w))
    return(invisible(NULL))
  }

  if (is.null(my.fig.png.width)) width = ifelse(w==1, 800, 1000) else
    width = my.fig.png.width
        
  if (is.null(my.fig.png.height)) height = switch(h, 600, 600, 1200, 1200) else
    height = my.fig.png.height

  png(filename = paste(s,".png",sep=""), width = width, height = height)
  my.fig.pngdev <<- dev.cur()

  par(mfrow=c(h,w))
  
  # mar default = c(5, 4, 4, 2) + 0.1 c(bottom, left, top, right)
  par(mgp=c(2,.8,0), mar=c(3, 3, 1, 1) + 0.1)

  if (w == 1 && h == 1) par(cex=1.4)  
  else par(cex=1.5)
}

my.png.fig.off <- function() {

  if (!my.fig.on) {
    par(my.fig.opar)
    return(invisible(NULL))
  }

  dev.off(my.fig.pngdev)
}

my.png1.fig <- function(s, h=600, w=800, ...) {
  png(filename=paste(s,".png",sep=""),width=w, height=h, ...)
  my.fig.pngdev <<- dev.cur()

  # mar default = c(5, 4, 4, 2) + 0.1 c(bottom, left, top, right)
  par(mgp=c(2,.8,0), cex=1.4, mar=c(3, 3, 1, 1) + 0.1)
}

my.sub <- function(text, ...) {
  mtext(text, 1, line=3.2, cex=par("cex"), ...)
}
