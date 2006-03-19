package org.apache.gump.dynagump.presentation.valueObjects;

import java.io.Serializable;

public class ProjectVO implements Serializable {

    private String projectId;

    private String name;

    private String description;

    private String moduleId;

    private String moduleName;

    public ProjectVO() {
    }

    public ProjectVO(String id, String name, String description, String moduleId, String moduleName) {
        this.projectId = id;
        this.name = name;
        this.description = description;
        this.moduleId = moduleId;
        this.moduleName = moduleName;
    }

    public String getDescription() {
        return description;
    }

    public void setDescription(String description) {
        this.description = description;
    }

    public String getName() {
        return name;
    }

    public void setName(String name) {
        this.name = name;
    }

    public String getProjectId() {
        return projectId;
    }

    public void setProjectId(String projectId) {
        this.projectId = projectId;
    }

    public String getModuleId() {
        return moduleId;
    }

    public void setModuleId(String moduleId) {
        this.moduleId = moduleId;
    }

    public String getModuleName() {
        return moduleName;
    }

    public void setModuleName(String moduleName) {
        this.moduleName = moduleName;
    }

}
