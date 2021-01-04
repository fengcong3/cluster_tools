#monitor my task
#fengcong@caas.cn
#2020-3-17 11:56:25

#usage: sh monitor_task.sh jobid scrptname workdir subcmd user_mail plot_or_not
subtime=`date +"%Y-%m-%d %H:%M:%S"`
jobid=$1
scriptname=$2
workdir=$3
subcmd=$4
user_mail=$5
plot=$6  #N=dont plot Y=plot

jobn=`echo $jobid | cut -f1 -d "."`
memfile="${scriptname}.m${jobn}"
echo -ne "time\tmem_kb\tvmem_kb\n" > $memfile

#echo $subcmd
running=0  #runing or not
maxmem=0 
maxvmem=0

startrun_time=`date +"%Y-%m-%d %H:%M:%S"`
endrun_time=`date +"%Y-%m-%d %H:%M:%S"`

while :
do
	sleep 2m;
	#judge finish or not
	qstat -u `whoami` | grep $jobid >/dev/null
	if [ $? -ne 0 ]; then 
		#echo "over 1"
		endrun_time=`date +"%Y-%m-%d %H:%M:%S"`
		break; 
	fi	
	#judge stat is C
	stat=`qstat -u \`whoami\` | grep $jobid | sed 's:[ ][ ]*: :g'| awk '{print $10}' `
	if [ $stat == "C" ]; then
		#echo "over 2" 
		endrun_time=`date +"%Y-%m-%d %H:%M:%S"`
		break; 
	fi


	#if it's in queue
	if [ $stat == "Q" ];then
		continue;
	fi

	if [ $stat == "R" ];then
		#start running ?
		if [ $running -eq 0 ]; then
			running=1
			startrun_time=`date +"%Y-%m-%d %H:%M:%S"`;
		fi	
		#get the status
		current_mem=`qstat -f $jobid | grep resources_used.mem | awk '{print $3}' | cut -f 1 -d "k"`
                current_vmem=`qstat -f $jobid | grep resources_used.vmem | awk '{print $3}' | cut -f 1 -d "k"`
		if [ "$current_mem" != "" ];then
			echo -ne "`date +"%Y_%m_%d_%H:%M:%S"`\t$current_mem\t$current_vmem\n" >> $memfile
                fi

		if [ $current_mem -ge $maxmem ] ; then
                        maxmem=$current_mem;
                fi
                if [ $current_vmem -ge $maxvmem ] ; then
                        maxvmem=$current_vmem;
                fi


		
	fi
		
done

#when the job is done
ln_start=`date -d  "$startrun_time" +%s`  
ln_end=`date -d  "$endrun_time" +%s`
interval=`expr $ln_end - $ln_start`

#subtime=`date +"%Y-%m-%d %H:%M:%S"`
#jobid=$1
#scriptname=$2
#workdir=$3
#subcmd=$4
#maxmem=0
#maxvmem=0

#record max mem usage
maxxx="#max\t${maxmem}\t${maxvmem}" 
sed -i "2i ${maxxx}" $memfile

#plot memusage
if [ $plot == "Y" ] ; then
	/public/home/fengcong/anaconda2/envs/R/bin/Rscript /public/home/fengcong/memplot.R $memfile
fi
#send email
if [ $user_mail != "nobody" ];then
	/public/home/fengcong/mail.py $jobid $scriptname $workdir "$subcmd" $maxmem $maxvmem "$subtime" $interval `whoami` $user_mail
fi


