package org.apache.gump.dynagump.database.hibernate;

public class BuildHib {
    private String buildId;

    private RunsHib runId;

    private String startTime;

    private String endTime;

    private ResultHib result;

    private String log;

    private ProjectVersionIdHib projectId;

    private ProjectHib project;

    public ResultHib getResult() {
        return result;
    }

    public void setResult(ResultHib result) {
        this.result = result;
    }

    public ProjectHib getProject() {
        return project;
    }

    public void setProject(ProjectHib project) {
        this.project = project;
    }

    public ProjectVersionIdHib getProjectId() {
        return projectId;
    }

    public void setProjectId(ProjectVersionIdHib projectId) {
        this.projectId = projectId;
    }

    public String getEndTime() {
        return endTime;
    }

    public void setEndTime(String endTime) {
        this.endTime = endTime;
    }

    public String getBuildId() {
        return buildId;
    }

    public void setBuildId(String buildId) {
        this.buildId = buildId;
    }

    public String getLog() {
        return log;
    }

    public void setLog(String log) {
        this.log = log;
    }

    public RunsHib getRunId() {
        return runId;
    }

    public void setRunId(RunsHib runId) {
        this.runId = runId;
    }

    public String getStartTime() {
        return startTime;
    }

    public void setStartTime(String startTime) {
        this.startTime = startTime;
    }
}
