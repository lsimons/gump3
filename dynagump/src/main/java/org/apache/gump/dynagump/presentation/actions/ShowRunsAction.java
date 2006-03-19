package org.apache.gump.dynagump.presentation.actions;

import java.sql.SQLException;

import javax.servlet.http.HttpServletRequest;
import javax.servlet.http.HttpServletResponse;

import org.apache.commons.logging.Log;
import org.apache.commons.logging.LogFactory;
import org.apache.gump.dynagump.presentation.ModuleController;
import org.apache.gump.dynagump.presentation.database.CouldNotFindDBException;
import org.apache.struts.action.Action;
import org.apache.struts.action.ActionForm;
import org.apache.struts.action.ActionForward;
import org.apache.struts.action.ActionMapping;

/**
 * Action to get the runs for a given workspace from the database. The list of
 * runs are stored in the session Object and later retrieved by the jsp page.
 * 
 * @author hodden
 * 
 */
public class ShowRunsAction extends Action {

    private static Log log = LogFactory.getLog(ShowRunsAction.class);

    public ActionForward execute(ActionMapping mapping, ActionForm form, HttpServletRequest request, HttpServletResponse response) {

        boolean forward = true;
        String errorMsg = null;

        try {
            String workspace = request.getParameter("workspace");
            if (workspace == null || workspace.equals("")) {
                workspace = (String) request.getSession().getAttribute("currentWorkspace");
            }
            if (workspace == null) {
                throw new Exception("No workspace Selected!\n You have to select a workspace to see that workspace's runs.");
            }
            ModuleController mc = ModuleController.getController();
            request.getSession().setAttribute("runs", mc.getRuns(workspace));
            request.getSession().setAttribute("currentWorkspace", workspace);
        } catch (SQLException sqle) {
            log.error(sqle.getMessage());
            errorMsg = sqle.getMessage();
            forward = false;

        } catch (CouldNotFindDBException cnfdbe) {
            log.error(cnfdbe.getMessage());
            errorMsg = cnfdbe.getMessage();
            forward = false;
        } catch (Exception e) {
            log.error(e.getMessage());
            errorMsg = e.getMessage();
            forward = false;
        }

        if (forward == true) {
            return mapping.findForward("success");
        } else {
            request.getSession().setAttribute("errorMsg", errorMsg);
            return mapping.findForward("errorPriv");
        }
    }
}
