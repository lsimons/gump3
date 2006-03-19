package org.apache.gump.dynagump.database.controller;

import java.sql.SQLException;
import java.util.List;

import org.apache.gump.dynagump.valueObjects.Build;
import org.apache.gump.dynagump.valueObjects.Host;
import org.apache.gump.dynagump.valueObjects.ProjectBuildVO;
import org.apache.gump.dynagump.valueObjects.ProjectVO;
import org.apache.gump.dynagump.valueObjects.Run;
import org.apache.gump.dynagump.valueObjects.RunStatusVO;

/**
 * Interface for the Database specific classes to connect to the database.
 * 
 * @author hodden
 * 
 */
public interface DBController {

    /**
     * Returns the information of hosts and workspaces. See the value object
     * host for more information
     * 
     * @return List of Host Objects
     * @throws SQLException
     */
    public List<Host> getHosts() throws SQLException;

    public void setWorkspace(List<Host> li) throws SQLException;

    /**
     * Get the runs for a given workspace from the database.
     * 
     * @param workspace -
     *            The given workspace represented by a String
     * @return A list of Run Objects.
     * @throws SQLException
     */
    public List<Run> getRuns(String workspace) throws SQLException;

    /**
     * Takes a RunStatusVO (RunStatus Value Object) and fills it with
     * information from the database of the builds and package information.
     * 
     * @param r -
     *            RunStatusVO
     * @param id -
     *            the id of the run
     * @throws SQLException
     */
    public void getBuilds(RunStatusVO r, String id) throws SQLException;

    /**
     * Set dependencies for the packages in the RunStatusVO
     * 
     * @param r -
     *            The Run Status Value Object.
     * @throws SQLException
     */
    public void setDependencies(RunStatusVO r) throws SQLException;

    /**
     * Method to add a History object to the Build object containing the build
     * objects history.
     * 
     * @param b
     * @throws SQLException
     */
    public void addHistory(Build b) throws SQLException;

    /**
     * Get a list of all the projects from the database.
     * 
     * @return a list of projectVO objects.
     * @throws SQLException
     */
    public List<ProjectVO> getProjects() throws SQLException;

    /**
     * Returns a list with all the builds and there dependencies
     * 
     * @return A list a project build value objects
     * @throws SQLException
     */
    public List<ProjectBuildVO> getProjectBuildsList(String projectID) throws SQLException;
}
