package org.apache.gump.dynagump.database.hibernate;

import java.util.Set;

public class ProjectHib {

    private String id;

    private String name;

    private String description;

    private ModuleHib module;

    private Set projectVersion;

    public ModuleHib getModule() {
        return module;
    }

    public void setModule(ModuleHib module) {
        this.module = module;
    }

    public String getDescription() {
        return description;
    }

    public void setDescription(String description) {
        this.description = description;
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

    public Set getProjectVersion() {
        return projectVersion;
    }

    public void setProjectVersion(Set projectVersion) {
        this.projectVersion = projectVersion;
    }

}
