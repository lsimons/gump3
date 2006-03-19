package org.apache.gump.dynagump.presentation;

import java.sql.SQLException;

import org.apache.gump.dynagump.presentation.database.CouldNotFindDBException;
import org.apache.gump.dynagump.presentation.database.DBHandler;
import org.apache.gump.dynagump.presentation.database.controller.DBController;
import org.apache.gump.dynagump.presentation.valueObjects.RunStatusVO;
/**
 * 
 * @author hodden
 * 
 * Controller for the Status evaluator. Evaluates and calculates the information retrieved from the database before presenting it for the user on a jsp.
 *
 */
public class StatusEvaluator {

	/**
	 * Constructor
	 *
	 */
	public StatusEvaluator(){
		
	}
	/**
	 * Calculates and evaluates the information from the db of the build for the given run by id.
	 * @param id - repsresenting the run id (String)
	 * @return Run Status Value Object
	 * @throws SQLException
	 * @throws CouldNotFindDBException
	 */
	public RunStatusVO getStatus(String id)throws SQLException, CouldNotFindDBException{
		RunStatusVO r = new RunStatusVO();
		DBController db  = DBHandler.getController();
		db.getBuilds(r, id);
		db.setDependencies(r);
		return r;
	}
}
