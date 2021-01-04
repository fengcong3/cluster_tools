args=commandArgs(T)
#args[1]


memfile=args[1]
# memfile="go_emmax_Q_943.sh.m142942"
data=read.table(memfile,head=T,comment.char="#")

data$time=factor(data$time)
data$mem_kb=data$mem_kb/(1024*1024)
data$vmem_kb=data$vmem_kb/(1024*1024)


sp=spline(data$time,data$mem_kb,n=1000)
sp1=spline(data$time,data$vmem_kb,n=1000)
maxmem=max(data$mem_kb)
maxvmem=max(data$vmem_kb)

pdf(paste(memfile,".pdf",sep=""),width = 8,height = 6)


plot(sp,col="red",type="l",lwd=2,
     xlab="Time",ylab="MEM(Gb)",main="memory usage",col.main="green",font.main=2,ylim = c(0,max(c(maxmem,maxvmem))))
lines(sp1,col="green",type="l",lwd=2,
      xlab="Time",ylab="MEM(Gb)")
legend("bottomright",legend=c("mem","vmem"),col=c("red","green"),lwd=2,lty=c(1,1))

dev.off()

