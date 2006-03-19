package org.apache.gump.dynagump.valueObjects;

import java.io.Serializable;
import java.sql.ResultSet;
import java.sql.SQLException;
import java.util.HashMap;
import java.util.Iterator;
import java.util.LinkedList;
import java.util.List;

public class Build implements Serializable {

    private String id; // build Id

    private String runId; // id of the run

    private String projectVersionId; // Project version id

    private String startTime; // Build started

    private String endTime; // build ended

    private int result; // result by values (0,1,2)

    private String log; // log from the build

    private String resultString; // the result represented by a string.

    private String projectName; // The name of the project

    private String projectId; // Database id for this project.

    private String description; // Project description

    private String module; // The module the project contains in.

    private List<Build> dependees = new LinkedList<Build>(); // Reference to
                                                                // other Build
                                                                // object that
                                                                // dependes on
                                                                // this one by
                                                                // builds.id.

    private List<Build> depends = new LinkedList<Build>(); // Reference to
                                                            // other builds the
                                                            // this build
                                                            // depends on.

    private HistoryVO history;

    public Build() {
    }

    public Build(String id, String runId, String projectVersionId, String startTime, String endTime, int result, String log, String resultString,
            String projectName, String projectId, String projectDescription, String moduleName) {
        this.id = id;
        this.runId = runId;
        this.projectVersionId = projectVersionId;
        this.startTime = startTime;
        this.endTime = endTime;
        this.result = result;
        this.log = log;
        this.resultString = resultString;
        this.projectName = projectName;
        this.projectId = projectId;
        this.description = projectDescription;
        this.module = moduleName;
    }

    public Build(ResultSet rs) throws SQLException {
        this.id = rs.getString("id");
        this.runId = rs.getString("run_id");
        this.projectVersionId = rs.getString("project_version_id");
        this.startTime = rs.getString("start_time");
        this.endTime = rs.getString("end_time");
        this.result = rs.getInt("result");
        this.log = rs.getString("log");
        this.resultString = rs.getString("result_name");
        this.projectName = rs.getString("name");
        this.projectId = rs.getString("project_id");
        this.description = rs.getString("description");
        this.module = rs.getString("module_name");
    }

    /**
     * Add a Build b as dependee to this object
     * 
     * @param b -
     *            Build object
     */
    public void addDependees(Build b) {
        this.dependees.add(b);
        b.addDependant(this);
    }

    public void addDependant(Build b) {
        this.depends.add(b);
    }

    public List<Build> getDependantList() {
        return this.depends;
    }

    public List<Build> getDependeesList() {
        return this.dependees;
    }

    /**
     * Return the number of Builds that dependes direct or inderect on this
     * build.
     * 
     * @return the number of dependees
     */
    public int getDependees() {

        if (this.dependees == null || this.dependees.size() == 0) {
            return 0;
        } else {
            HashMap map = new HashMap();
            this.calculateDependencies(map);
            int dependees = map.size();
            return dependees;
        }
    }

    /**
     * Returns the number of direct dependent packages
     * 
     * @return
     */
    public int getDirectDependees() {
        return dependees.size();
    }

    private void calculateDependencies(HashMap map) {
        Iterator<Build> it = dependees.iterator();
        Build tmp;
        while (it.hasNext()) {
            tmp = it.next();
            map.put(tmp.getId(), 0);
            tmp.calculateDependencies(map);
        }
    }

    /** Getters and setters */

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

    public String getLog() {
        return log;
    }

    public void setLog(String log) {
        this.log = log;
    }

    public String getProjectVersionId() {
        return projectVersionId;
    }

    public void setProjectVersionId(String projectVersionId) {
        this.projectVersionId = projectVersionId;
    }

    public int getResult() {
        return result;
    }

    public void setResult(int result) {
        this.result = result;
    }

    public String getRunId() {
        return runId;
    }

    public void setRunId(String runId) {
        this.runId = runId;
    }

    public String getStartTime() {
        return startTime;
    }

    public void setStartTime(String startTime) {
        this.startTime = startTime;
    }

    public String getResultString() {
        return resultString;
    }

    public void setResultString(String resultString) {
        this.resultString = resultString;
    }

    public String getProjectName() {
        return projectName;
    }

    public void setProjectName(String projectName) {
        this.projectName = projectName;
    }

    public String getDescription() {
        return description;
    }

    public void setDescription(String description) {
        this.description = description;
    }

    public String getModule() {
        return module;
    }

    public void setModule(String module) {
        this.module = module;
    }

    public String getProjectId() {
        return projectId;
    }

    public HistoryVO getHistory() {
        if (history == null) {
            System.out.println("history == null");
        }
        return history;
    }

    public void addHistory(HistoryVO h) {
        System.out.println("history = " + h + "\n" + "startTime: " + h.getStartOfState());
        this.history = h;
    }

}
