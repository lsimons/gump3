package org.apache.gump.dynagump.presentation.actions;

import java.sql.SQLException;

import javax.servlet.http.HttpServletRequest;
import javax.servlet.http.HttpServletResponse;

import org.apache.commons.logging.Log;
import org.apache.commons.logging.LogFactory;
import org.apache.gump.dynagump.presentation.ModuleController;
import org.apache.gump.dynagump.presentation.database.CouldNotFindDBException;
import org.apache.gump.dynagump.presentation.valueObjects.RunStatusVO;
import org.apache.struts.action.Action;
import org.apache.struts.action.ActionForm;
import org.apache.struts.action.ActionForward;
import org.apache.struts.action.ActionMapping;

/**
 * Action class to get the information of all the build for a given run.
 * @author hodden
 *
 */
public class StatusRunAction extends Action {
	
	private static Log log = LogFactory.getLog(StatusRunAction.class);
	
	public ActionForward execute(ActionMapping mapping,ActionForm form,
			HttpServletRequest request,HttpServletResponse response){
		
		boolean forward = true;
		String errorMsg = null;
		
		try{
			String id = request.getParameter("id");
			if(id == null || id.equals("")){
				id = (String)request.getSession().getAttribute("currentRun");
			}
			if(id == null){
				throw new RuntimeException("No Run Selected!\n You have to select a workspace and a build to see that the builds for that workspace.");
			}
			
			ModuleController mc = ModuleController.getController();
			RunStatusVO rs = mc.getRunStatus(id);
			request.getSession().setAttribute("runsStatus", rs);
			request.getSession().setAttribute("currentRun", id);
		}catch(SQLException sqle){
			log.error(sqle.getMessage());
			errorMsg = sqle.getMessage();
			forward = false;
			
		}catch(CouldNotFindDBException cnfdbe){
			log.error(cnfdbe.getMessage());
			errorMsg = cnfdbe.getMessage();
			forward = false;
		}catch(RuntimeException e){
			log.error(e.getMessage());
			e.getStackTrace();
			errorMsg = e.getMessage();
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
