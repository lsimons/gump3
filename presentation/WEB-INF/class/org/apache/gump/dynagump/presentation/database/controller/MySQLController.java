package org.apache.gump.dynagump.presentation.database.controller;

import java.sql.Connection;
import java.sql.DriverManager;
import java.sql.ResultSet;
import java.sql.SQLException;
import java.sql.Statement;
import java.util.HashMap;
import java.util.Iterator;
import java.util.LinkedList;
import java.util.List;
import java.util.Set;

import org.apache.gump.dynagump.presentation.valueObjects.Build;
import org.apache.gump.dynagump.presentation.valueObjects.HistoryVO;
import org.apache.gump.dynagump.presentation.valueObjects.Host;
import org.apache.gump.dynagump.presentation.valueObjects.ProjectBuildVO;
import org.apache.gump.dynagump.presentation.valueObjects.ProjectVO;
import org.apache.gump.dynagump.presentation.valueObjects.Run;
import org.apache.gump.dynagump.presentation.valueObjects.RunStatusVO;


public class MySQLController implements DBController {

	private Connection con;
	private Statement stm;
	
	public MySQLController()throws ClassNotFoundException, SQLException{
		 
		 
		 // Load the JDBC driver
		 String driverName = "com.mysql.jdbc.Driver"; // MySQL MM JDBC driver
		 Class.forName("com.mysql.jdbc.Driver"); 
		    
		        // Create a connection to the database
		 String serverName = "localhost";
		 String mydatabase = "gump";
		 String url = "jdbc:mysql://" + serverName +  "/" + mydatabase; // a JDBC url
		 String username = "root";
		 String password = "";
		 con = DriverManager.getConnection(url, username, password);
		 stm = con.createStatement();
	}
	public List<Host> getHosts()throws SQLException{
		//TODO A more Effective query, do both host and workspace in one request.
		
		List<Host> li = new LinkedList<Host>();
		
		Statement smt = con.createStatement();
		ResultSet rs = smt.executeQuery("select * from hosts");
		while(rs.next()){
			li.add(new Host(rs));
		}		
		rs.close();		
		return li;
		
	}
	public void setWorkspace(List<Host> li)throws SQLException{
		
		ResultSet rs = null;
		for(int i=0; i < li.size(); i++){
			rs = stm.executeQuery("select * from workspaces WHERE host='"+li.get(i).getAddress()+"'");
			li.get(i).setWorkspaces(rs);
			rs.close();
		}
		
	}
	public List<Run> getRuns(String workspace)throws SQLException{
		ResultSet rs = stm.executeQuery("Select * From runs Where workspace_id='"+workspace+"'");
		LinkedList<Run> li = new LinkedList<Run>();
		while(rs.next()){
			li.add(new Run(rs));
			
		}
		rs.close();
		return li;
	}
	public void getBuilds(RunStatusVO r, String id) throws SQLException{
		
		ResultSet rs = stm.executeQuery("SELECT builds.*, results.name AS result_name, projects.id AS project_id, projects.*, "
									   +"modules.description AS module_description, modules.name AS module_name FROM builds "
									   +"LEFT JOIN results ON builds.result=results.id "
									   +"LEFT JOIN project_versions ON builds.project_version_id=project_versions.id "
									   +"LEFT JOIN projects ON project_versions.project_id=projects.id "
									   +"LEFT JOIN modules ON projects.module_id = modules.id "
									   +"WHERE builds.run_id='"+id+"'");
		while(rs.next()){
			r.addBuild(new Build(rs));
			
		}
		rs.close();
	}
	public void setDependencies(RunStatusVO r)throws SQLException{
		HashMap<String, Build> builds = r.getBuildsMap();
		
		Set<String> keys = builds.keySet();
		Iterator<String> it = keys.iterator();
		String key = null;
		while(it.hasNext()){
			
			key = it.next();
			
			ResultSet rs = stm.executeQuery("SELECT project_dependencies.dependee, builds.id FROM project_dependencies LEFT JOIN builds ON project_dependencies.dependee=builds.project_version_id WHERE dependant='"+builds.get(key).getProjectVersionId()+"'");
			while(rs.next()){
				
				builds.get(key).addDependees(builds.get(rs.getString("id")));	
			}
			rs.close();
		}		
	}
	public void addHistory(Build b) throws SQLException{
		String query =  "SELECT builds.start_time AS start, builds.end_time AS end, builds.result AS result " 
		+"FROM projects " 
		+"LEFT JOIN project_versions ON projects.id=project_versions.project_id "
		+"LEFT JOIN builds ON project_versions.id=builds.project_version_id "
		+"WHERE projects.id='"+b.getProjectId()+"' ORDER BY start DESC ";
		
		ResultSet rs = stm.executeQuery(query);
		HistoryVO history = new HistoryVO();
		while(rs.next()){
			history.addValues(rs.getInt("result"),rs.getString("start"));			
		}
		history.setValues();
		b.addHistory(history);
		rs.close();
	}
	public List<ProjectVO> getProjects() throws SQLException{
		List<ProjectVO> li = new LinkedList<ProjectVO>();
		String query ="SELECT projects.*, modules.name AS module_name FROM projects "
					 +"LEFT JOIN modules ON modules.id = projects.module_id";
		ResultSet rs = stm.executeQuery(query);
		
		while(rs.next()){
			li.add(new ProjectVO(
					rs.getString("id"),
					rs.getString("name"),
					rs.getString("description"),
					rs.getString("module_id"),
					rs.getString("module_name")));
		}
		rs.close();
		return li;
	}
	public List<ProjectBuildVO> getProjectBuildsList(String projectID) throws SQLException{
		List<ProjectBuildVO> li = new LinkedList<ProjectBuildVO>();
		String query = "SELECT projects.*, builds.id AS build_id, builds.run_id, results.name AS result_name, builds.result, builds.start_time, builds.end_time, runs.workspace_id, runs.name AS run_name, workspaces.name AS workspace_name, modules.name AS module_name,project_versions.id AS project_versions_id "
					  +"FROM projects "
					  +"LEFT JOIN project_versions ON project_versions.project_id=projects.id " 
					  +"LEFT JOIN builds ON project_versions.id=builds.project_version_id "
					  +"LEFT JOIN runs ON builds.run_id=runs.id "
					  +"LEFT JOIN workspaces ON runs.workspace_id=workspaces.id "
					  +"LEFT JOIN modules ON projects.module_id = modules.id "
					  +"LEFT JOIN results ON builds.result=results.id "
					  +"WHERE projects.id='"+projectID+"'";

		ResultSet rs = stm.executeQuery(query);
		ProjectBuildVO tempVO = null;
		while(rs.next()){
			tempVO = new ProjectBuildVO();
			tempVO.setId(rs.getString("id"));
			tempVO.setName(rs.getString("name"));
			tempVO.setDescription(rs.getString("description"));
			tempVO.setModule_id(rs.getString("module_id"));
			tempVO.setModule_name(rs.getString("module_name"));
			tempVO.setBuild_id(rs.getString("build_id"));
			tempVO.setRun_id(rs.getString("run_id"));
			tempVO.setRun_name(rs.getString("run_name"));
			tempVO.setResult(rs.getInt("result"));
			
			tempVO.setResultString(rs.getString("result_name"));
			tempVO.setEnd_time(rs.getString("end_time"));
			tempVO.setStart_time(rs.getString("start_time"));
			tempVO.setWorkspace_id(rs.getString("workspace_id"));
			tempVO.setWorkspace_name(rs.getString("workspace_name"));
			tempVO.setProjectVersionID(rs.getString("project_versions_id"));
			li.add(tempVO);
		}
		rs.close();
		for(int i=0; i<li.size(); i++){
			tempVO = li.get(i);
			tempVO.setDependees(this.dependees(tempVO.getProjectVersionID()));
			tempVO.setDependant(this.dependant(tempVO.getProjectVersionID()));
		}
		return li;
	}
	private List<String> dependees(String s) throws SQLException{
		List<String> li = new LinkedList<String>();
		String query = "SELECT * FROM `project_dependencies` WHERE  dependant ='"+s+"'";
		ResultSet rs = stm.executeQuery(query);
		while(rs.next()){
			li.add(rs.getString("dependee"));
		}
		rs.close();
		return li;
	}
	private List<String> dependant(String s) throws SQLException{
		List<String> li = new LinkedList<String>();
		String query = "SELECT * FROM `project_dependencies` WHERE  dependee ='"+s+"'";
		ResultSet rs = stm.executeQuery(query);
		while(rs.next()){
			li.add(rs.getString("dependant"));
		}
		rs.close();
		return li;
	}

}
