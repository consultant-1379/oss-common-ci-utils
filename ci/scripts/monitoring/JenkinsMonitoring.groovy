import net.bull.javamelody.*;
import net.bull.javamelody.internal.model.*;
import net.bull.javamelody.internal.common.*;
import java.lang.management.ManagementFactory;
import java.lang.management.OperatingSystemMXBean;
import jenkins.model.*
import hudson.model.*
import groovy.json.JsonSlurper
import java.lang.management.MemoryPoolMXBean;

java = new JavaInformations(Parameters.getServletContext(), true);
memory = java.memoryInformations;
def message = "";
def object = "";

def getFEMMetrics = new URL("${METRICS_KEY_URL_FEM1}").openConnection();
def getFEMMetricsRC = getFEMMetrics.getResponseCode();
def jsonSlurper = new JsonSlurper();

currentNumberOfExecutors = "";
queueTimeAverage = "";
buildTimeAverage = "";
currentNumberOfExecutors = "";
jobScheduled = "";
cpuLoadPercentageOneHourAverage = "";
threshold = 90;

if (getFEMMetricsRC.equals(200)) {
    object = jsonSlurper.parseText(getFEMMetrics.getInputStream().getText());

    currentNumberOfExecutors = object.gauges["jenkins.executor.count.value"].value;
    queueTimeAverage = object.timers["jenkins.job.blocked.duration"].mean;
    buildTimeAverage = object.timers["jenkins.job.building.duration"].mean;
    jobScheduled = object.meters["jenkins.job.scheduled"].mean_rate;
    cpuLoadPercentageOneHourAverage = object.histograms["system.cpu.load.x100.window.1h"].mean;
}

def queueTimeAverage(){
    message = "";
    message = "\nQueue time average (seconds):\n    " + queueTimeAverage;

    return message;
}

def buildTimeAverage(){
    message = "";
    message = "\nBuild time average (seconds):\n    " + buildTimeAverage;

    return message;
}

def recommendedNumberOfExecutors(){
    message = "";
    recommendedNumberOfExecutors = jobScheduled*(buildTimeAverage/60)
    message = "\nRecommended number of executors):\n    " + recommendedNumberOfExecutors;
    if (recommendedNumberOfExecutors > currentNumberOfExecutors){
        message += "\nWARNING!: Recommended number of executors is larger than current number of executors!"
    }

    return message;
}

def sessions(){
    message = "";
    numberOfSessions = java.sessionCount;
    message = "\nNumber of sessions:\n    " + numberOfSessions;

    return message;
}

def systemLoadAverage(){
    message = "";
    systemLoadAverage = java.systemLoadAverage;
    message = "\nSystem load average:\n    " + systemLoadAverage;

    return message;
}

def startDate(){
    message = "";
    startDate = java.startDate;
    message = "\nStart date:\n    " + startDate;

    return message;
}

def javaMemory(){
    message = "";
    double usedMemory = memory.usedMemory / 1024 / 1024;
    usedMemory = Math.round(usedMemory);
    double maxMemory =  memory.maxMemory / 1024 / 1024;
    maxMemory = Math.round(maxMemory);
    double memoryThreshold = maxMemory * threshold /100;
    double memoryPercentageUsage = usedMemory/maxMemory*100

    message += "\nJava memory used:\n    " + usedMemory + " Mb";
    message += "\nAvailable java memory:\n    " + maxMemory + " Mb";
    message += "\nMemory usage:\n    " + memoryPercentageUsage + "%";

    if (usedMemory > memoryThreshold){
        message += "\nWARNING!: Java memory usage above " + threshold + "%!"
    }

    return message;
}

def metaSpaceSize(){
    message = "";
    for(MemoryPoolMXBean memoryMXBean : ManagementFactory.getMemoryPoolMXBeans()){
        if ("Metaspace".equals(memoryMXBean.getName())){
            float usedMetaSpaceSize = memoryMXBean.getUsage().getUsed() / 1024 / 1024;
            float maxMetaSpaceSize = memoryMXBean.getUsage().getMax() /1024 /1024;
            usedMetaSpaceSize = Math.round(usedMetaSpaceSize);
            maxMetaSpaceSize = Math.round(maxMetaSpaceSize);
            float MetaSpaceThreshold = maxMetaSpaceSize * threshold /100;

            message += "\nUsed MetaSpace:\n " + usedMetaSpaceSize + " Mb";
            message += "\nAvailable MetaSpace:\n " + maxMetaSpaceSize + " Mb";
            message += "\nMetaSpace usage:\n " + (usedMetaSpaceSize /maxMetaSpaceSize *100) + "%";

            if(usedMetaSpaceSize > MetaSpaceThreshold){
                message += "\nWARNING!: MetaSpace size usage above " + threshold + "%!"
            }

            return message;

        }
    }
}

def physicalMemorySize(){
    message = "";
    OperatingSystemMXBean operatingSystemMXBean = ManagementFactory.getOperatingSystemMXBean();
    float usedPhysicalMemorySize = memory.usedPhysicalMemorySize / 1024 / 1024;
    usedPhysicalMemorySize = Math.round(usedPhysicalMemorySize);
    float maxPhysicalMem = operatingSystemMXBean.getTotalPhysicalMemorySize() / 1024 / 1024;
    maxPhysicalMem = Math.round(maxPhysicalMem);
    float physicalMemThreshold = maxPhysicalMem * threshold /100;

    message += "\nUsed physical memory:\n    " + usedPhysicalMemorySize + " Mb";
    message += "\nAvailable physical memory:\n    " + maxPhysicalMem + " Mb";
    message += "\nPhysical Memory Size usage:\n    " + (usedPhysicalMemorySize/maxPhysicalMem*100) + "%";

    if (usedPhysicalMemorySize > physicalMemThreshold){
        message += "\nWARNING!: Physical memory usage above " + threshold + "%!"
    }

    return message;
}

def swapSpaceSize(){
    message = "";
    OperatingSystemMXBean operatingSystemMXBean = ManagementFactory.getOperatingSystemMXBean();
    float usedSwapSpaceSize = memory.usedSwapSpaceSize / 1024 / 1024;
    usedSwapSpaceSize = Math.round(usedSwapSpaceSize);
    float maxSwapSpace = operatingSystemMXBean.getTotalSwapSpaceSize() / 1024 / 1024;
    maxSwapSpace = Math.round(maxSwapSpace);
    float swapSpaceThreshold = (operatingSystemMXBean.getTotalSwapSpaceSize() / 1024 / 1024) * threshold /100;

    message += "\nUsed swap space:\n    " + usedSwapSpaceSize + " Mb";
    message += "\nAvailable swap space:\n    " + maxSwapSpace + " Mb";
    message += "\nSwap space usage:\n    " + (usedSwapSpaceSize /maxSwapSpace *100) + "%";

    if (usedSwapSpaceSize > swapSpaceThreshold ){
        message += "\nWARNING!: Physical memory usage above " + threshold + "%!"
    }

    return message;
}

def cpuUsage(){
    message = "";
    cpuLoadPercentageOneHourAverage = cpuLoadPercentageOneHourAverage/100;
    cpuLoadThreshold = threshold /10;
    message += "\nSystem CPU load:\n    " + cpuLoadPercentageOneHourAverage;
    if (cpuLoadPercentageOneHourAverage > cpuLoadThreshold){
        message += "\nWARNING!: CPU Load has been over " + threshold + "% for an hour!"
    }

    return message;
}

def threads(){
    message = "";
    threads = java.getThreadInformationsList();
    deadlocked = new java.util.ArrayList();
    for (thread in threads) {
        if (thread.deadlocked)
            deadlocked.add(thread);
    }

    message += "\n" + deadlocked.size() + " Deadlocked threads / " + threads.size() + " Threads\n";
    for (thread in deadlocked) {
        message += "";
        message += thread;
        for (s in thread.getStackTrace())
        message += "    " + s;
    }
    if (deadlocked.size() > 0){
        message += "\nWARNING! Deadlocked threads count is " + deadlocked.size() + "!"
    }

    return message;
}

def disabledJobs() {
  message = "";
  def allJobs = jenkins.model.Jenkins.instance.getAllItems(jenkins.model.ParameterizedJobMixIn.ParameterizedJob.class);
  int disabledJobsCount = 0;
  allJobs.each {
    if(it.isDisabled()){
      disabledJobsCount++;
    }
  }
  message += "Number of disabled jobs in the Jenkins FEM: " + disabledJobsCount + "\n";
  return message;
}

def enabledJobs() {
  message = "";
  def allJobs = jenkins.model.Jenkins.instance.getAllItems(jenkins.model.ParameterizedJobMixIn.ParameterizedJob.class);
  int enabledJobsCount = 0;
  allJobs.each {
    if(it.isBuildable()){
      enabledJobsCount++;
    }
  }
  message += "Number of enabled jobs in the Jenkins FEM: " + enabledJobsCount + "\n";
  return message;
}

def allJobs() {
  message = "";
  double maxNoOfJobs = java.availableProcessors*100;
  double maxNoOfJobsThreshold = threshold /100;
  double percentageCapacity = maxNoOfJobs*maxNoOfJobsThreshold;
  def allJobs = jenkins.model.Jenkins.instance.getAllItems(jenkins.model.ParameterizedJobMixIn.ParameterizedJob.class);
  noOfJobs = allJobs.size();
  message += "Total number of jobs in the Jenkins FEM: " + noOfJobs + "\n";
  if (noOfJobs >= maxNoOfJobs) {
        message += "WARNING! Total number of jobs in Jenkins FEM exceeds maximum amount!\n" + "Maximum number of jobs = " + maxNoOfJobs + "\nTotal number of jobs in Jenkins FEM = " + noOfJobs + "!";
  }
  if ((noOfJobs >= percentageCapacity) && (noOfJobs < maxNoOfJobs)) {
        message += "WARNING! Total number of jobs in Jenkins FEM is over " + threshold + "% capacity!\n" + "Maximum number of jobs = " + maxNoOfJobs + "\nTotal number of jobs in Jenkins FEM = " + noOfJobs + "!";
  }
  return message;
}

return this
