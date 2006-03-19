package org.apache.gump.dynagump;

/**
 * @author hodden
 * 
 * Facade Controller against the database and data layer.
 * The controller is static to decrese the amount of running objects. 
 */
import java.sql.SQLException;
import java.util.List;

import org.apache.gump.dynagump.database.CouldNotFindDBException;
import org.apache.gump.dynagump.database.DBHandler;
import org.apache.gump.dynagump.database.controller.DBController;
import org.apache.gump.dynagump.valueObjects.Build;
import org.apache.gump.dynagump.valueObjects.Host;
import org.apache.gump.dynagump.valueObjects.Run;
import org.apache.gump.dynagump.valueObjects.RunStatusVO;

public class ModuleController {

    private static ModuleController ref;

    private DBController db;

    /**
     * Constructor intitates a db connection.
     * 
     * @throws CouldNotFindDBException
     */
    private ModuleController() throws CouldNotFindDBException {
        db = DBHandler.getController();
    }

    /**
     * static method to get the ModuleController Object.
     * 
     * @return reference to a ModuleController Object
     * @throws CouldNotFindDBException
     */
    public static ModuleController getController() throws CouldNotFindDBException {
        if (ref == null) {
            ref = new ModuleController();
        }
        return ref;
    }

    /**
     * Returns a list of all the Hosts from the db in a Host Object
     * 
     * @return list of Host Objects
     * @throws SQLException
     */
    public List<Host> getHosts() throws SQLException {
        List<Host> li = db.getHosts();
        db.setWorkspace(li);
        return li;
    }

    /**
     * Returns a list of runs from a given workspace
     * 
     * @param workspace -
     *            name of the workspace (String)
     * @return A list of Run objects
     * @throws SQLException
     */
    public List<Run> getRuns(String workspace) throws SQLException {
        return db.getRuns(workspace);
    }

    /**
     * Returns a Runstatus object from the run with the given id.
     * 
     * @param id -
     *            Run id
     * @return A RunStatus Value Object
     * @throws CouldNotFindDBException
     * @throws SQLException
     */
    public RunStatusVO getRunStatus(String id) throws CouldNotFindDBException, SQLException {
        RunStatusVO r = new RunStatusVO();
        DBController db = DBHandler.getController();
        db.getBuilds(r, id);
        db.setDependencies(r);
        return r;
    }

    /**
     * Adds a history object with history to the package of its past states and
     * statistics.
     * 
     * @param b
     *            The build object
     * @throws SQLException
     * @throws CouldNotFindDBException
     */
    public void addProjectHistory(Build b) throws SQLException, CouldNotFindDBException {
        if (b.getHistory() == null) {
            DBController db = DBHandler.getController();
            db.addHistory(b);
        }
    }
}
