package org.apache.gump.dynagump.presentation.actions;

import java.sql.SQLException;
import java.util.List;

import javax.servlet.http.HttpServletRequest;
import javax.servlet.http.HttpServletResponse;

import org.apache.commons.logging.Log;
import org.apache.commons.logging.LogFactory;
import org.apache.gump.dynagump.presentation.ModuleController;
import org.apache.gump.dynagump.presentation.database.CouldNotFindDBException;
import org.apache.gump.dynagump.presentation.valueObjects.Host;
import org.apache.struts.action.Action;
import org.apache.struts.action.ActionForm;
import org.apache.struts.action.ActionForward;
import org.apache.struts.action.ActionMapping;

/**
 * Action to get the workspaces from the database
 * @author hodden
 *
 */
//TODO Change the name to workspaceAction
public class BuildsAction extends Action {

	private static Log log = LogFactory.getLog(BuildsAction.class);
	
	public ActionForward execute(ActionMapping mapping,ActionForm form,
			HttpServletRequest request,HttpServletResponse response){

		boolean forward = true;
		String errorMsg = null;
		
		try{
			ModuleController mc = ModuleController.getController();
			List<Host> li = mc.getHosts();
			request.getSession().setAttribute("workspaces", li);
		}catch(SQLException sqle){
			log.error(sqle.getMessage());
			errorMsg = sqle.getMessage();
			forward = false;
		}catch(CouldNotFindDBException cnfdbe){
			log.error(cnfdbe.getMessage());
			errorMsg = cnfdbe.getMessage();
			forward = false;
		}
		
		if(forward == true){
			return mapping.findForward("success");
		}
		else{
			request.getSession().setAttribute("errorMsg",errorMsg);
			return mapping.findForward("errorPriv");
		}
	}

}
