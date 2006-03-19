package org.apache.gump.dynagump.presentation.database;

import org.apache.gump.dynagump.presentation.database.controller.DBController;

/**
 * DBHandler Controller for the dabase settings.
 * 
 * @author hodden
 * 
 */
// TODO expand to a more dynamic way of configuration ex: xml, textfile.
public class DBHandler {

    private static String db = "Hibernate"; // "MySQL";
    /*
     * private static HashMap<String, DBController> dbs = load();
     * 
     * private static HashMap<String, DBController> load(){ dbs = new HashMap<String,
     * DBController>(); dbs.put("MySQL", new MySqlController()); return dbs; }
     */

    public static DBController getController() throws CouldNotFindDBException {
        try {
            return (DBController) Class.forName("org.apache.gump.dynagump.presentation.database.controller." + db + "Controller").newInstance();
        } catch (ClassNotFoundException cnfe) {
            throw new CouldNotFindDBException("Could not initiate Database :" + db, cnfe);
        } catch (IllegalAccessException iae) {
            throw new CouldNotFindDBException("Could not initiate Database :" + db, iae);
        } catch (InstantiationException ie) {
            throw new CouldNotFindDBException("Could not initiate Database :" + db, ie);
        }
    }
}
