package org.apache.gump.dynagump.presentation.database.hibernate;

import java.util.Set;

public class ModuleHib {

    private String id;

    private String description;

    private String name;

    private Set project;

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

    public Set getProject() {
        return project;
    }

    public void setProject(Set project) {
        this.project = project;
    }

}
