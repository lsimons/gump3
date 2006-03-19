package org.apache.gump.dynagump.valueObjects;

import java.io.Serializable;
import java.util.LinkedList;
import java.util.List;

public class ProjectBuildVO implements Serializable {

    private String id;

    private String name;

    private String description;

    private String module_id;

    private String build_id;

    private String run_id;

    private int result;

    private String start_time;

    private String end_time;

    private String workspace_id;

    private String run_name;

    private String workspace_name;

    private String module_name;

    private String resultString;

    private String projectVersionID;

    private List<String> dependees = new LinkedList<String>(); // packages
                                                                // depending on
                                                                // this package

    private List<String> dependant = new LinkedList<String>(); // packages this
                                                                // package
                                                                // depends on.

    public ProjectBuildVO() {
    }

    public ProjectBuildVO(String id, String name, String description, String module_id, String build_id, String run_id, int result,
            String start_time, String end_time, String workspace_id, String run_name, String workspace_name, String module_name, String resultString) {
        this.id = id;
        this.name = name;
        this.description = description;
        this.module_id = module_id;
        this.module_name = module_name;
        this.build_id = build_id;
        this.run_id = run_id;
        this.run_name = run_name;
        this.start_time = start_time;
        this.end_time = end_time;
        this.workspace_id = workspace_id;
        this.workspace_name = workspace_name;
        this.result = result;
        this.resultString = resultString;
    }

    public int getNumbersOfDependees() {
        return dependees.size();
    }

    public int getNumbersOfDependant() {
        return dependant.size();
    }

    /* Getters and setters */
    public String getBuild_id() {
        return build_id;
    }

    public void setBuild_id(String build_id) {
        this.build_id = build_id;
    }

    public String getDescription() {
        return description;
    }

    public void setDescription(String description) {
        this.description = description;
    }

    public String getEnd_time() {
        return end_time;
    }

    public void setEnd_time(String end_time) {
        this.end_time = end_time;
    }

    public String getId() {
        return id;
    }

    public void setId(String id) {
        this.id = id;
    }

    public String getModule_id() {
        return module_id;
    }

    public void setModule_id(String module_id) {
        this.module_id = module_id;
    }

    public String getModule_name() {
        return module_name;
    }

    public void setModule_name(String module_name) {
        this.module_name = module_name;
    }

    public String getName() {
        return name;
    }

    public void setName(String name) {
        this.name = name;
    }

    public int getResult() {
        return result;
    }

    public void setResult(int result) {
        this.result = result;
    }

    public String getResultString() {
        return resultString;
    }

    public void setResultString(String resultString) {
        this.resultString = resultString;
    }

    public String getRun_id() {
        return run_id;
    }

    public void setRun_id(String run_id) {
        this.run_id = run_id;
    }

    public String getRun_name() {
        return run_name;
    }

    public void setRun_name(String run_name) {
        this.run_name = run_name;
    }

    public String getStart_time() {
        return start_time;
    }

    public void setStart_time(String start_time) {
        this.start_time = start_time;
    }

    public String getWorkspace_id() {
        return workspace_id;
    }

    public void setWorkspace_id(String workspace_id) {
        this.workspace_id = workspace_id;
    }

    public String getWorkspace_name() {
        return workspace_name;
    }

    public void setWorkspace_name(String workspace_name) {
        this.workspace_name = workspace_name;
    }

    public List<String> getDependant() {
        return dependant;
    }

    public void setDependant(List<String> dependant) {
        this.dependant = dependant;
    }

    public List<String> getDependees() {
        return dependees;
    }

    public void setDependees(List<String> dependees) {
        this.dependees = dependees;
    }

    public String getProjectVersionID() {
        return projectVersionID;
    }

    public void setProjectVersionID(String projectVersionID) {
        this.projectVersionID = projectVersionID;
    }

}
