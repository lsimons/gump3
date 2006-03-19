package org.apache.gump.dynagump.presentation.database.hibernate;

import java.util.Set;

public class ResultHib {

    private Integer id;

    private String name;

    private String description;

    private Set builds;

    public Set getBuilds() {
        return builds;
    }

    public void setBuilds(Set builds) {
        this.builds = builds;
    }

    public String getDescription() {
        return description;
    }

    public void setDescription(String description) {
        this.description = description;
    }

    public Integer getId() {
        return id;
    }

    public void setId(Integer id) {
        this.id = id;
    }

    public String getName() {
        return name;
    }

    public void setName(String name) {
        this.name = name;
    }

}
