package org.apache.gump.dynagump.database.hibernate;

public class RunsHib {

    private String id;

    private String startTime;

    private String endTime;

    private WorkspaceHib workspaceId;

    private String name;

    public String getEndTime() {
        return endTime;
    }

    public void setEndTime(String endTime) {
        this.endTime = endTime;
    }

    public String getId() {
        return id;
    }

    public void setId(String id) {
        this.id = id;
    }

    public String getName() {
        return name;
    }

    public void setName(String name) {
        this.name = name;
    }

    public String getStartTime() {
        return startTime;
    }

    public void setStartTime(String startTime) {
        this.startTime = startTime;
    }

    public WorkspaceHib getWorkspaceId() {
        return workspaceId;
    }

    public void setWorkspaceId(WorkspaceHib workspaceId) {
        this.workspaceId = workspaceId;
    }

}
