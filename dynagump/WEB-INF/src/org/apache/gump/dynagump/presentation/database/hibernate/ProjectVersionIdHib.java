package org.apache.gump.dynagump.presentation.database.hibernate;

public class ProjectVersionIdHib {

	private String id;
	private ProjectHib project;
	private BuildHib build;
	
	public String getId() {
		return id;
	}
	public void setId(String id) {
		this.id = id;
	}
	public ProjectHib getProject() {
		return project;
	}
	public void setProject(ProjectHib project) {
		this.project = project;
	}
	public BuildHib getBuild() {
		return build;
	}
	public void setBuild(BuildHib build) {
		this.build = build;
	}
	
	
}
