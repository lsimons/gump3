package org.apache.gump.dynagump.presentation.valueObjects;

import java.io.Serializable;
import java.sql.ResultSet;
import java.sql.SQLException;

public class WorkSpace implements Serializable{

	private String id;
	private String name;
	private String host;
	private String description;
	
	public WorkSpace(){}
	public WorkSpace(String id, String name, String host, String description){
		this.id = id;
		this.name= name;
		this.host = host;
		this.description = description;
	}
	public WorkSpace(ResultSet rs) throws SQLException{
		this.id = rs.getString("id");
		this.name = rs.getString("name");
		this.host = rs.getString("host");
		this.description = rs.getString("description");
	}
	/** Getters and setters **/
	
	public String getDescription() {
		return description;
	}
	public void setDescription(String description) {
		this.description = description;
	}
	public String getHost() {
		return host;
	}
	public void setHost(String host) {
		this.host = host;
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
	
}
