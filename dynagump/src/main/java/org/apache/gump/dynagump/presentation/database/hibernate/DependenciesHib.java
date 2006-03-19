package org.apache.gump.dynagump.presentation.database.hibernate;

public class DependenciesHib {

    private String dependee;

    private String dependant;

    private BuildHib build;

    public String getDependant() {
        return dependant;
    }

    public void setDependant(String dependant) {
        this.dependant = dependant;
    }

    public String getDependee() {
        return dependee;
    }

    public void setDependee(String dependee) {
        this.dependee = dependee;
    }

    public BuildHib getBuild() {
        return build;
    }

    public void setBuild(BuildHib build) {
        this.build = build;
    }

}
