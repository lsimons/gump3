package org.apache.gump.dynagump.presentation.actions;

import java.sql.SQLException;

import javax.servlet.http.HttpServletRequest;
import javax.servlet.http.HttpServletResponse;

import org.apache.commons.logging.Log;
import org.apache.commons.logging.LogFactory;
import org.apache.gump.dynagump.presentation.ModuleController;
import org.apache.gump.dynagump.presentation.database.CouldNotFindDBException;
import org.apache.gump.dynagump.presentation.valueObjects.Build;
import org.apache.gump.dynagump.presentation.valueObjects.RunStatusVO;
import org.apache.struts.action.Action;
import org.apache.struts.action.ActionForm;
import org.apache.struts.action.ActionForward;
import org.apache.struts.action.ActionMapping;
/**
 * Action to list the projects indivdual statistics such as number of failures, success, duration of state and so on.
 * @author hodden
 *
 */
public class ProjectStatusAction extends Action {
	
	private static Log log = LogFactory.getLog(ProjectStatusAction.class);
	
	public ActionForward execute(ActionMapping mapping,ActionForm form,
			HttpServletRequest request,HttpServletResponse response){

		boolean forward = true;
		String errorMsg = null;
		
		try{
			String id = request.getParameter("id");
			if(id == null || id.equals("")){
				throw new RuntimeException("No Project Selected!\n You have to select a project from the status page (select: workspace/run/project).");
			}
			
			RunStatusVO rs = (RunStatusVO)request.getSession().getAttribute("runsStatus");
			Build build = rs.getBuild(id);
			ModuleController mc = ModuleController.getController();
			mc.addProjectHistory(build);
			request.getSession().setAttribute("project", build);

		}catch (CouldNotFindDBException cnfe){
			log.error(cnfe.getMessage());
			cnfe.getStackTrace();
			errorMsg = cnfe.getMessage();
			forward = false;			
		}catch (SQLException sqle){
			log.error(sqle.getMessage());
			sqle.getStackTrace();
			errorMsg = sqle.getMessage();
			forward = false;			
		}catch (NullPointerException nullE){
			log.error(nullE.getMessage());
			nullE.getStackTrace();
			errorMsg = nullE.getMessage();
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
